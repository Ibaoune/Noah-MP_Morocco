import os
import glob
import xarray as xr
import pandas as pd
import numpy as np
import yaml

EXP_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/'
DA_EXPERIMENTS = {
    'DA_smap_nocdf_noirr_2016': 'DA_nocdf_noirr_2016',
    'DA_smap_cdf_noirr_2016': 'DA_cdf_noirr_2016'
}
OUT_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/'

def audit_da():
    os.makedirs(OUT_DIR, exist_ok=True)
    strategies = {}
    
    for exp_id, folder in DA_EXPERIMENTS.items():
        print(f"Auditing DA for {exp_id}")
        
        # We know from LOT 2A that the increments are in SURFACEMODEL
        sm_path = os.path.join(EXP_DIR, folder, 'output', '2016-*', '**', '*.nc')
        files = glob.glob(sm_path, recursive=True)
        files = [f for f in files if "SURFACEMODEL" in f and "LIS_HIST" in f]
        files = sorted(files)
        
        if not files:
            continue
            
        strategy = "INCREMENT_NOT_AVAILABLE"
        inc_var = "SoilMoist_inc"
        
        files_with_var = 0
        total_non_zero = 0
        total_valid = 0
        
        dims = ""
        layers = 0
        unit = ""
        sample_path = ""
        
        for i, f in enumerate(files):
            try:
                with xr.open_dataset(f) as ds:
                    if inc_var in ds.data_vars:
                        files_with_var += 1
                        if i == 0:
                            dims = str(ds[inc_var].dims)
                            layers = ds[inc_var].shape[1] if len(ds[inc_var].shape) > 2 else 1
                            unit = ds[inc_var].attrs.get("units", "unknown")
                            sample_path = os.path.relpath(f, EXP_DIR)
                            
                        # compute non zeros
                        arr = ds[inc_var].values
                        valid = ~np.isnan(arr)
                        non_zero = np.sum(arr[valid] != 0)
                        total_valid += np.sum(valid)
                        total_non_zero += non_zero
            except:
                pass
                
        pct_files = (files_with_var / len(files)) * 100 if files else 0
        frac_nonzero = (total_non_zero / total_valid) if total_valid > 0 else 0
        
        level = "NONE"
        if files_with_var > 0:
            strategy = "EXPLICIT_INCREMENT"
            level = "VARIABLE_PRESENT"
            if frac_nonzero > 0:
                level = "NONZERO_VALUES_CONFIRMED"
                if unit != "unknown":
                    level = "UNITS_CONFIRMED"
                    # We haven't confirmed sign convention or water equivalent programmatically
                    # but we record where we are at.
        
        strategies[exp_id] = {
            "directory_name": folder,
            "sample_file": sample_path,
            "increment_variable": inc_var if files_with_var > 0 else "None",
            "dimensions": dims,
            "layers": layers,
            "unit": unit,
            "frequency": "Daily",
            "sign_convention": "TBD",
            "percentage_files_present": pct_files,
            "fraction_nonzero_values": float(frac_nonzero),
            "strategy": strategy,
            "verification_level": level
        }
        
    with open(os.path.join(OUT_DIR, "assimilation_increment_strategy.yaml"), "w") as f:
        yaml.dump(strategies, f, default_flow_style=False)
        
    print("DA Audit complete.")

if __name__ == "__main__":
    audit_da()
