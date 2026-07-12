import os
import glob
import xarray as xr
import pandas as pd
import numpy as np

EXP_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/'
# Using the correct experiment directories found in configs/experiments.yaml
EXPERIMENTS = ['OPL_noirr_2016', 'DA_nocdf_noirr_2016', 'DA_cdf_noirr_2016']
OUT_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/'

def extract_date_from_filename(filename):
    # LIS_HIST_201606070000.d01.nc -> 20160607
    base = os.path.basename(filename)
    parts = base.split("_")
    for p in parts:
        if p.startswith("2016") and len(p) >= 8:
            return pd.Timestamp(p[:8])
    return None

def run_qc():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    temporal_rows = []
    grid_rows = []
    input_rows = []
    var_rows = []
    coord_rows = []
    missing_rows = []
    diag_rows = []
    
    for exp in EXPERIMENTS:
        path = os.path.join(EXP_DIR, exp, 'output', '2016-*', '**', '*.nc')
        files = glob.glob(path, recursive=True)
        files = [f for f in files if "SURFACEMODEL" in f and "LIS_HIST" in f]
        files = sorted(files)
        
        if not files:
            print(f"No files found for {exp}")
            continue
            
        print(f"Checking {exp}: {len(files)} files found.")
        input_rows.append({"experiment": exp, "num_files": len(files), "first_file": files[0], "last_file": files[-1]})
        
        try:
            # 1. Temporal Analysis (File vs Internal)
            file_dates = []
            internal_dates = []
            concordance_errors = 0
            
            # Since parsing 366 files takes time, we only read time coord from all files if they exist, but xarray open_dataset is slow.
            # We can use netCDF4 or just trust the first/last and file names for speed. 
            # But the user asked for exact numbers. Let's do it quickly by opening only time.
            
            for f in files:
                f_date = extract_date_from_filename(f)
                if f_date:
                    file_dates.append(f_date)
            
            # Let's open first and last for grid/vars
            ds_first = xr.open_dataset(files[0])
            ds_last = xr.open_dataset(files[-1])
            
            # Assume all files have 1 timestep matching filename for speed, unless we must open all.
            # We will use the file_dates as the "extracted dates" to represent the dataset if we don't open all 366.
            # Opening 366 NetCDF files takes ~10 seconds, which is fine. Let's open all for time only.
            
            for f, f_date in zip(files, file_dates):
                with xr.open_dataset(f, decode_times=True) as ds:
                    if "time" in ds.coords:
                        t = pd.Timestamp(ds.time.values[0]).normalize()
                        internal_dates.append(t)
                        if t != f_date:
                            concordance_errors += 1
            
            times = pd.DatetimeIndex(internal_dates)
            start_date = times.min()
            end_date = times.max()
            num_files = len(files)
            num_extracted = len(times)
            num_unique = len(np.unique(times))
            
            has_feb29 = pd.Timestamp('2016-02-29') in times
            
            expected_times = pd.date_range(start="2016-01-01", end="2016-12-31", freq='D')
            missing_days = expected_times.difference(times)
            dup_days = num_extracted - num_unique
            out_of_2016 = sum(1 for t in times if t.year != 2016)
            
            time_diffs = times.to_series().diff().dt.total_seconds() / 86400
            min_step = time_diffs.min() if len(time_diffs) > 1 else np.nan
            max_step = time_diffs.max() if len(time_diffs) > 1 else np.nan
            
            temporal_rows.append({
                "experiment": exp,
                "num_files": num_files,
                "num_dates_extracted": num_extracted,
                "num_dates_unique": num_unique,
                "first_date": start_date,
                "last_date": end_date,
                "has_feb29": has_feb29,
                "min_time_step_days": min_step,
                "max_time_step_days": max_step,
                "missing_dates_count": len(missing_days),
                "duplicated_dates_count": dup_days,
                "dates_out_of_2016": out_of_2016,
                "filename_internal_concordance_errors": concordance_errors
            })
            
            # Grid checks (use first file)
            lat = ds_first.lat.values
            lon = ds_first.lon.values
            lat_res = np.abs(lat[1] - lat[0]) if len(lat) > 1 else np.nan
            lon_res = np.abs(lon[1] - lon[0]) if len(lon) > 1 else np.nan
            lat_orient = "North-to-South" if lat[0] > lat[-1] else "South-to-North"
            lon_orient = "West-to-East" if lon[0] < lon[-1] else "East-to-West"
            
            grid_rows.append({
                "experiment": exp,
                "lat_size": len(lat),
                "lon_size": len(lon),
                "lat_res": lat_res,
                "lon_res": lon_res,
                "lat_orient": lat_orient,
                "lon_orient": lon_orient
            })
            
            coord_rows.append({
                "experiment": exp,
                "has_lat": "lat" in ds_first.coords,
                "has_lon": "lon" in ds_first.coords,
                "has_time": "time" in ds_first.coords
            })

            # Variable availability & missing values (use first file)
            for var in ds_first.data_vars:
                var_rows.append({"experiment": exp, "variable": var, "dtype": str(ds_first[var].dtype)})
                da = ds_first[var]
                valid_count = int(da.count().compute().item())
                missing_count = int(np.isnan(da.values).sum())
                missing_rows.append({
                    "experiment": exp, 
                    "variable": var, 
                    "valid_values_ts0": valid_count, 
                    "missing_values_ts0": missing_count
                })

            diag_rows.append({"experiment": exp, "qc_status": "READY"})
            ds_first.close()
            ds_last.close()
        except Exception as e:
            print(f"Error processing {exp}: {e}")
            diag_rows.append({"experiment": exp, "qc_status": "FAILED", "error": str(e)})
            
    pd.DataFrame(input_rows).to_csv(os.path.join(OUT_DIR, "input_inventory.csv"), index=False)
    pd.DataFrame(temporal_rows).to_csv(os.path.join(OUT_DIR, "temporal_coverage.csv"), index=False)
    pd.DataFrame(grid_rows).to_csv(os.path.join(OUT_DIR, "grid_compatibility.csv"), index=False)
    pd.DataFrame(var_rows).to_csv(os.path.join(OUT_DIR, "variable_availability.csv"), index=False)
    pd.DataFrame(coord_rows).to_csv(os.path.join(OUT_DIR, "coordinate_checks.csv"), index=False)
    pd.DataFrame(missing_rows).to_csv(os.path.join(OUT_DIR, "missing_values.csv"), index=False)
    pd.DataFrame(diag_rows).to_csv(os.path.join(OUT_DIR, "diagnostic_capabilities.csv"), index=False)
    print("QC checks completed. CSVs generated.")

if __name__ == "__main__":
    run_qc()
