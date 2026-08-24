"""
01_build_dataset.py
===================

This script handles the data preparation and feature engineering step.
It merges spatial/temporal covariates, processes observational inputs, 
and produces a cleaned `.parquet` dataset ready for Random Forest training.
"""

# Author: M. EL Aabaribaoune (@um6p)
import os
import sys
import yaml
import argparse
import glob
import pandas as pd
import numpy as np
import xarray as xr
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

def process_hist_files(hist_dir, exp_name, month_filter, run_mode):
    """
    Reads 1 month of HIST files, computes RZSM, and applies monthly aggregation.
    """
    files = glob.glob(os.path.join(hist_dir, "**", f"LIS_HIST_{month_filter}*.nc"), recursive=True)
    if not files:
        print(f"[{exp_name}] No HIST files found for {month_filter} in {hist_dir}")
        return pd.DataFrame(), 0
        
    print(f"[{exp_name}] Found {len(files)} files for {month_filter}. Processing...")
    
    # We will use xarray to open multifile dataset
    ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', decode_times=False)
    
    # List of variables we care about
    var_list = ['SoilMoist_tavg', 'Evap_tavg', 'Qs_tavg', 'Qsb_tavg', 'Rainf_tavg', 'lat', 'lon']
    optional_vars = ['WaterTableD_tavg', 'WT_tavg']
    
    actual_vars = [v for v in var_list + optional_vars if v in ds.data_vars]
    ds_sub = ds[actual_vars]
    
    # Compute RZSM and SSM
    if 'SoilMoist_tavg' in ds_sub:
        smc = ds_sub['SoilMoist_tavg']
        ds_sub['SSM'] = smc.isel(SoilMoist_profiles=0)
        ds_sub['RZSM'] = (smc.isel(SoilMoist_profiles=0)*0.1 + 
                          smc.isel(SoilMoist_profiles=1)*0.3 + 
                          smc.isel(SoilMoist_profiles=2)*0.6) / 1.0
        ds_sub['SMC_L1'] = smc.isel(SoilMoist_profiles=0)
        ds_sub['SMC_L2'] = smc.isel(SoilMoist_profiles=1)
        ds_sub['SMC_L3'] = smc.isel(SoilMoist_profiles=2)
        ds_sub['SMC_L4'] = smc.isel(SoilMoist_profiles=3)
        actual_vars.extend(['SSM', 'RZSM', 'SMC_L1', 'SMC_L2', 'SMC_L3', 'SMC_L4'])
        
    # Temporal Aggregation
    agg_ds = xr.Dataset()
    
    for v in actual_vars:
        if v not in ds_sub: continue
        is_flux = False
        if v in ds.data_vars:
            units = ds[v].attrs.get('units', '').lower()
            if 's-1' in units or 's^-1' in units or 'rate' in units:
                is_flux = True
                
        if is_flux and v in ['Evap_tavg', 'Qs_tavg', 'Qsb_tavg', 'Rainf_tavg']:
            agg_ds[v] = ds_sub[v].mean(dim='time') * (30 * 86400)
        else:
            agg_ds[v] = ds_sub[v].mean(dim='time')
    # Drop extra multidimensional profile variables to avoid dataframe explosion
    vars_to_drop = [v for v in agg_ds.data_vars if 'SoilMoist_profiles' in agg_ds[v].dims or 'SoilTemp_profiles' in agg_ds[v].dims]
    if vars_to_drop:
        agg_ds = agg_ds.drop_vars(vars_to_drop)
        
    df = agg_ds.to_dataframe().reset_index()
    
    rename_dict = {c: f"{c}_{exp_name}" for c in df.columns if c not in ['lat', 'lon', 'north_south', 'east_west']}
    df = df.rename(columns=rename_dict)
    
    ds.close()
    
    if run_mode == "real_data_smoke_test":
        df = df.dropna().head(200)
    else:
        df = df.dropna()
        
    return df, len(files)

def load_monthly_smap_increments(exp_name, incr_dir, month_filter, config):
    """
    Reads SMAP DA increment files for a given month and aggregates them.
    """
    smap_cfg = config.get("paths", {}).get("smap_diagnostics", {})
    if not smap_cfg.get("use_increments", False):
        return pd.DataFrame(), 0
        
    pattern = smap_cfg.get("increment_file_pattern", "LIS_DA_EnKF_*_incr*.nc")
    files = glob.glob(os.path.join(incr_dir, "**", f"*{month_filter}*incr*.nc"), recursive=True)
    if not files:
        print(f"[{exp_name} Increments] No increment files found for {month_filter}")
        return pd.DataFrame(), 0
        
    print(f"[{exp_name} Increments] Found {len(files)} files for {month_filter}. Processing...")
    
    ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', decode_times=False)
    
    incr_vars = smap_cfg.get("increment_variables", {})
    l1 = incr_vars.get("layer1")
    l2 = incr_vars.get("layer2")
    l3 = incr_vars.get("layer3")
    l4 = incr_vars.get("layer4")
    
    agg_ds = xr.Dataset()
    
    if l1 in ds:
        agg_ds['increment_SMC_L1'] = ds[l1].sum(dim='time')
        agg_ds['increment_SSM'] = ds[l1].sum(dim='time')
        
    if l2 in ds: agg_ds['increment_SMC_L2'] = ds[l2].sum(dim='time')
    if l3 in ds: agg_ds['increment_SMC_L3'] = ds[l3].sum(dim='time')
    if l4 in ds: agg_ds['increment_SMC_L4'] = ds[l4].sum(dim='time')
    
    if l1 in ds and l2 in ds and l3 in ds:
        agg_ds['increment_RZSM'] = (ds[l1].sum(dim='time')*0.1 + 
                                    ds[l2].sum(dim='time')*0.3 + 
                                    ds[l3].sum(dim='time')*0.6) / 1.0
                                    
    df = agg_ds.to_dataframe().reset_index()
    rename_dict = {c: f"{c}_{exp_name}" for c in df.columns if c not in ['north_south', 'east_west']}
    df = df.rename(columns=rename_dict)
    
    ds.close()
    return df.dropna(), len(files)

def build_dataset():
    print("--- Starting Dataset Builder (01_build_dataset.py) ---")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=None, help="Override run_mode from config")
    parser.add_argument("--resume", action="store_true", help="Resume by skipping existing monthly parts")
    args = parser.parse_args()
    
    config_path = "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    paths = config.get("paths", {})
    options = config.get("options", {})
    smap_cfg = paths.get("smap_diagnostics", {})
    
    output_dataset = paths.get("output_dataset", "data/processed/monthly_pixel_dataset.parquet")
    parts_dir = "data/processed/monthly_parts"
    os.makedirs(parts_dir, exist_ok=True)
    
    run_mode = args.mode if args.mode else options.get("run_mode", "real_data")
    print(f"Run mode: {run_mode}")
    
    log_file = "logs/full_run_v0_log.md"
    os.makedirs("reports", exist_ok=True)
    if not args.resume or not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("# Full Run V0 Log\n\n")
            f.write("| Month | OPL/DA Files | Incr Files | Pixels | Time (s) | Warnings |\n")
            f.write("|---|---|---|---|---|---|\n")
            
    months_to_process = []
    if run_mode == "real_data_smoke_test":
        months_to_process = ["201703"]
    elif run_mode == "real_data":
        start_date = datetime.strptime(options.get("start_date", "2016-01-01"), "%Y-%m-%d")
        end_date = datetime.strptime(options.get("end_date", "2020-12-31"), "%Y-%m-%d")
        curr = start_date
        while curr <= end_date:
            months_to_process.append(curr.strftime("%Y%m"))
            curr += relativedelta(months=1)
    else:
        print("Running synthetic_test mode (skipped).")
        return
        
    opl_dir = paths.get("opl_hist_dir")
    da_nocdf_dir = paths.get("da_nocdf_hist_dir")
    da_cdf_dir = paths.get("da_cdf_hist_dir")
    da_nocdf_incr_dir = smap_cfg.get("da_nocdf_incr_dir")
    da_cdf_incr_dir = smap_cfg.get("da_cdf_incr_dir")
    
    all_months_dfs = []
    
    for month in months_to_process:
        print(f"\n========== Processing Month: {month} ==========")
        start_time = time.time()
        
        part_file = os.path.join(parts_dir, f"monthly_pixel_dataset_{month}.parquet")
        if args.resume and os.path.exists(part_file):
            try:
                main_df = pd.read_parquet(part_file)
                print(f"Loaded existing part for {month} ({main_df.shape[0]} rows)")
                all_months_dfs.append(main_df)
                continue
            except Exception as e:
                print(f"Error loading {part_file}: {e}. Reprocessing.")
                
        warnings = []
        df_opl, c_opl = process_hist_files(opl_dir, "OPL", month, run_mode)
        df_nocdf, c_noc = process_hist_files(da_nocdf_dir, "DA_NoCDF", month, run_mode)
        df_cdf, c_cdf = process_hist_files(da_cdf_dir, "DA_CDF", month, run_mode)
        
        hist_files = f"{c_opl}/{c_noc}/{c_cdf}"
        if df_opl.empty or df_nocdf.empty or df_cdf.empty:
            print(f"Error: Missing HIST data for {month}. Skipping.")
            warnings.append("Missing HIST")
            with open(log_file, "a") as f:
                f.write(f"| {month} | {hist_files} | 0/0 | 0 | {time.time()-start_time:.1f} | {', '.join(warnings)} |\n")
            continue
            
        print("Merging HIST datasets...")
        main_df = pd.merge(df_opl, df_nocdf, on=['lat', 'lon', 'north_south', 'east_west'])
        main_df = pd.merge(main_df, df_cdf, on=['lat', 'lon', 'north_south', 'east_west'])
        
        c_noc_inc, c_cdf_inc = 0, 0
        if smap_cfg.get("use_increments", False):
            df_nocdf_incr, c_noc_inc = load_monthly_smap_increments("DA_NoCDF", da_nocdf_incr_dir, month, config)
            df_cdf_incr, c_cdf_inc = load_monthly_smap_increments("DA_CDF", da_cdf_incr_dir, month, config)
            
            if not df_nocdf_incr.empty:
                main_df = pd.merge(main_df, df_nocdf_incr, on=['north_south', 'east_west'], how='left')
            if not df_cdf_incr.empty:
                main_df = pd.merge(main_df, df_cdf_incr, on=['north_south', 'east_west'], how='left')
                
        incr_files = f"{c_noc_inc}/{c_cdf_inc}"
        
        # Hydrological-response targets
        main_df["delta_NoCDF_minus_CDF_SSM"] = main_df["SSM_DA_NoCDF"] - main_df["SSM_DA_CDF"]
        main_df["delta_DA_NoCDF_minus_OPL_RZSM"] = main_df["RZSM_DA_NoCDF"] - main_df["RZSM_OPL"]
        main_df["delta_DA_CDF_minus_OPL_RZSM"] = main_df["RZSM_DA_CDF"] - main_df["RZSM_OPL"]
        main_df["delta_DA_NoCDF_minus_OPL_ET"] = main_df["Evap_tavg_DA_NoCDF"] - main_df["Evap_tavg_OPL"]
        main_df["delta_DA_CDF_minus_OPL_ET"] = main_df["Evap_tavg_DA_CDF"] - main_df["Evap_tavg_OPL"]
        main_df["delta_DA_NoCDF_minus_OPL_runoff"] = main_df["Qs_tavg_DA_NoCDF"] - main_df["Qs_tavg_OPL"]
        main_df["delta_DA_NoCDF_minus_OPL_baseflow"] = main_df["Qsb_tavg_DA_NoCDF"] - main_df["Qsb_tavg_OPL"]
        
        # Assimilation-increment targets
        if 'increment_SSM_DA_NoCDF' in main_df.columns and 'increment_SSM_DA_CDF' in main_df.columns:
            main_df["delta_increment_NoCDF_minus_CDF_SSM"] = main_df["increment_SSM_DA_NoCDF"] - main_df["increment_SSM_DA_CDF"]
        if 'increment_RZSM_DA_NoCDF' in main_df.columns and 'increment_RZSM_DA_CDF' in main_df.columns:
            main_df["delta_increment_NoCDF_minus_CDF_RZSM"] = main_df["increment_RZSM_DA_NoCDF"] - main_df["increment_RZSM_DA_CDF"]
            
        main_df["precipitation_model"] = main_df["Rainf_tavg_OPL"]
        
        year = int(month[:4])
        m = int(month[4:6])
        main_df["month"] = m
        main_df["season"] = (m%12 + 3)//3
        main_df["time"] = pd.to_datetime(f"{year}-{m:02d}-15")
        main_df["year"] = year
        
        main_df.to_parquet(part_file)
        print(f"Saved monthly part: {part_file} ({main_df.shape[0]} rows)")
        all_months_dfs.append(main_df)
        
        elapsed = time.time() - start_time
        with open(log_file, "a") as f:
            f.write(f"| {month} | {hist_files} | {incr_files} | {main_df.shape[0]} | {elapsed:.1f} | {', '.join(warnings)} |\n")
            
    print("\n========== Combining All Months ==========")
    if not all_months_dfs:
        print("Error: No data processed.")
        return
        
    final_df = pd.concat(all_months_dfs, ignore_index=True)
    
    os.makedirs(os.path.dirname(output_dataset), exist_ok=True)
    if run_mode == "real_data_smoke_test":
        final_df.to_parquet(output_dataset)
    else:
        if len(all_months_dfs) < 60:
            print(f"Error: Only {len(all_months_dfs)}/60 months were processed successfully.")
            print("The final full dataset will NOT be created to prevent RF training on partial data.")
            sys.exit(1)
            
        # Save as 2016-2020 if full run
        output_dataset_full = output_dataset.replace(".parquet", "_2016_2020.parquet")
        final_df.to_parquet(output_dataset_full)
        # Also symlink or save to the standard path for the next scripts
        final_df.to_parquet(output_dataset)
        print(f"Full dataset built with shape {final_df.shape} and saved to {output_dataset_full}")

if __name__ == "__main__":
    build_dataset()
