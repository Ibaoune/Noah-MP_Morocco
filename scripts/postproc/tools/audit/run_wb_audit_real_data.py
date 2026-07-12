import os
import glob
import xarray as xr
import pandas as pd

EXP_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/'
EXPERIMENTS = ['OPL_noirr_2016', 'DA_nocdf_noirr_2016', 'DA_cdf_noirr_2016']
OUT_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/'

VARS_OF_INTEREST = {
    "Rainf_f_tavg": {"type": "flux", "role": "source", "in_tws": False, "conv": "kg m-2 s-1 to mm/day", "time": "mean", "use": "YES", "just": "Forcing precip"},
    "Evap_tavg": {"type": "flux", "role": "sink", "in_tws": False, "conv": "kg m-2 s-1 to mm/day", "time": "mean", "use": "YES", "just": "Total ET"},
    "Qs_tavg": {"type": "flux", "role": "sink", "in_tws": False, "conv": "kg m-2 s-1 to mm/day", "time": "mean", "use": "YES", "just": "Surface runoff"},
    "Qsb_tavg": {"type": "flux", "role": "sink", "in_tws": False, "conv": "kg m-2 s-1 to mm/day", "time": "mean", "use": "YES", "just": "Subsurface runoff"},
    "TWS_tavg": {"type": "storage", "role": "storage", "in_tws": True, "conv": "mm", "time": "mean", "use": "PENDING", "just": "Needs definition check"},
    "GWS_tavg": {"type": "storage", "role": "storage", "in_tws": True, "conv": "mm", "time": "mean", "use": "PENDING", "just": "Double count risk with TWS"},
    "SoilMoist_inst": {"type": "storage", "role": "storage", "in_tws": True, "conv": "m3/m3 to mm", "time": "instant", "use": "PENDING", "just": "Maybe better for dS"},
    "SoilMoist_tavg": {"type": "storage", "role": "storage", "in_tws": True, "conv": "m3/m3 to mm", "time": "mean", "use": "PENDING", "just": "Maybe better for dS"}
}

def run_wb_audit():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    
    for exp in EXPERIMENTS:
        path = os.path.join(EXP_DIR, exp, 'output', '2016-*', '**', '*.nc')
        files = glob.glob(path, recursive=True)
        files = [f for f in files if "SURFACEMODEL" in f and "LIS_HIST" in f]
        files = sorted(files)
        
        if not files:
            continue
            
        print(f"WB Audit {exp}: reading first and last files.")
        try:
            ds_start = xr.open_dataset(files[0])
            ds_end = xr.open_dataset(files[-1])
            
            # Check standard vars
            for var, info in VARS_OF_INTEREST.items():
                start_avail = var in ds_start.data_vars
                end_avail = var in ds_end.data_vars
                unit = ds_start[var].attrs.get("units", "unknown") if start_avail else "N/A"
                double_count = "HIGH" if (info["in_tws"] and var != "TWS_tavg" and "TWS_tavg" in ds_start.data_vars) else "LOW"
                
                rows.append({
                    "experiment": exp,
                    "variable": var,
                    "unit": unit,
                    "type": info["type"],
                    "time_convention": info["time"],
                    "conversion": info["conv"],
                    "role": info["role"],
                    "in_tws": info["in_tws"],
                    "double_count_risk": double_count,
                    "avail_start": start_avail,
                    "avail_end": end_avail,
                    "usage_status": info["use"],
                    "justification": info["just"]
                })
            
            # Look for increments dynamically
            inc_vars = [v for v in ds_start.data_vars if "inc" in v.lower()]
            for var in inc_vars:
                unit = ds_start[var].attrs.get("units", "unknown")
                rows.append({
                    "experiment": exp,
                    "variable": var,
                    "unit": unit,
                    "type": "increment",
                    "time_convention": "instant",
                    "conversion": "TBD",
                    "role": "source/sink",
                    "in_tws": True,
                    "double_count_risk": "N/A",
                    "avail_start": True,
                    "avail_end": var in ds_end.data_vars,
                    "usage_status": "REQUIRED",
                    "justification": "DA increment for closure"
                })

            ds_start.close()
            ds_end.close()
        except Exception as e:
            print(f"Error processing WB for {exp}: {e}")
            
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "water_balance_variable_audit.csv"), index=False)
    print("WB Audit completed.")

if __name__ == "__main__":
    run_wb_audit()
