import os
import pandas as pd
import xarray as xr
import sys

VALIDATION_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/validation/"
OUTPUT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/tables/"

def inspect_netcdf():
    records = []
    
    # We will pick one netcdf file per subdirectory to represent the product metadata
    for root, dirs, files in os.walk(VALIDATION_DIR):
        nc_files = [f for f in files if f.endswith('.nc') or f.endswith('.nc4')]
        if not nc_files:
            continue
        
        # Pick the first as representative
        sample_file = os.path.join(root, nc_files[0])
        rel_path = os.path.relpath(sample_file, VALIDATION_DIR)
        category = rel_path.split('/')[0] if '/' in rel_path else rel_path
        
        try:
            ds = xr.open_dataset(sample_file)
            dims = str(dict(ds.dims))
            coords = str(list(ds.coords))
            vars_list = list(ds.data_vars)
            if 'time' in ds.coords:
                time_cov = f"{ds['time'].values.min()} to {ds['time'].values.max()}"
                time_len = len(ds['time'])
            else:
                time_cov = "UNKNOWN"
                time_len = "UNKNOWN"
                
            attrs = str(ds.attrs)
            
            # Extract main variable attributes
            main_var = vars_list[0] if vars_list else "NONE"
            if main_var != "NONE":
                units = ds[main_var].attrs.get('units', 'UNKNOWN')
                fill = ds[main_var].attrs.get('_FillValue', 'UNKNOWN')
                scale = ds[main_var].attrs.get('scale_factor', 1)
            else:
                units = fill = scale = "UNKNOWN"
                
            ds.close()
            
            independence = "NOT_VERIFIED"
            if "lsm" in category.lower():
                independence = "MODEL_BENCHMARK"
            elif "soil_moisture" in category.lower() and "smap" not in rel_path.lower():
                independence = "INDEPENDENT"
                
            records.append({
                "category": category,
                "sample_file": nc_files[0],
                "product_name": ds.attrs.get('title', 'UNKNOWN'),
                "version": ds.attrs.get('version', 'VERSION_TO_VERIFY'),
                "variable": main_var,
                "units": units,
                "scale_factor": scale,
                "fill_value": fill,
                "dimensions": dims,
                "coordinates": coords,
                "time_coverage": time_cov,
                "num_time_steps": time_len,
                "independence_status": independence,
                "local_status": "READY" if time_cov != "UNKNOWN" else "PARTIAL",
                "recommended_version": "VERSION_TO_VERIFY",
                "version_verification_status": "PENDING"
            })
            
        except Exception as e:
            records.append({
                "category": category,
                "sample_file": nc_files[0],
                "error": str(e),
                "local_status": "CORRUPT",
                "independence_status": "NOT_VERIFIED"
            })
            
    df = pd.DataFrame(records)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, "validation_dataset_metadata.csv"), index=False)
    print(f"Generated validation_dataset_metadata.csv with {len(df)} records.")

if __name__ == "__main__":
    print("Extracting NetCDF metadata...")
    inspect_netcdf()
