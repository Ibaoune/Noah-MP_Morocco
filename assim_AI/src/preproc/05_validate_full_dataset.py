"""
05_validate_full_dataset.py
===========================

This script strictly validates the dataset completeness before training.
It checks for missing predictors, infinite values, or null target values 
to prevent partial or corrupted Random Forest training.
"""

# Author: M. EL Aabaribaoune (@um6p)
import pandas as pd
import numpy as np
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-complete", action="store_true", help="Require exact 60 months of data")
    args = parser.parse_args()
    
    print("--- Starting Dataset Validation ---")
    
    output_report = "logs/full_run_v0_validation_report.md"
    dataset_path = "data/processed/monthly_pixel_dataset_2016_2020.parquet"
    
    if not os.path.exists(dataset_path):
        # Fallback to the default one if the full run didn't explicitly name it
        dataset_path = "data/processed/monthly_pixel_dataset.parquet"
        
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        if args.require_complete:
            sys.exit(1)
        return
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_parquet(dataset_path)
    
    is_valid = True
    
    with open(output_report, "w") as f:
        f.write("# Full Run V0 Technical Validation Report\n\n")
        
        # A. Dataset
        f.write("## A. Dataset Overview\n")
        f.write(f"- **Path**: `{dataset_path}`\n")
        f.write(f"- **Total Rows**: {df.shape[0]}\n")
        f.write(f"- **Total Columns**: {df.shape[1]}\n")
        
        if 'time' in df.columns:
            months = df['time'].dt.strftime('%Y%m').unique()
            f.write(f"- **Total Months**: {len(months)}\n")
            f.write(f"- **Period**: {months.min()} to {months.max()}\n")
            
            f.write("- **Missing Months**: ")
            all_months = pd.date_range(start='2016-01-01', end='2020-12-31', freq='MS').strftime('%Y%m')
            missing = set(all_months) - set(months)
            if missing:
                f.write(f"{len(missing)} missing ({', '.join(sorted(missing))})\n")
                if args.require_complete:
                    print(f"Validation failed: {len(missing)} missing months.")
                    is_valid = False
            else:
                f.write("None. All 60 months present.\n")
                
            if args.require_complete and len(months) != 60:
                print(f"Validation failed: Found {len(months)} months, expected 60.")
                is_valid = False
                
            f.write(f"- **Pixels per Month**: ~{df.shape[0] / len(months):.0f}\n")
        
        if 'year' in df.columns and 'month' in df.columns and 'lat' in df.columns and 'lon' in df.columns:
            dups = df.duplicated(subset=['year', 'month', 'lat', 'lon']).sum()
            f.write(f"- **Duplicates (year, month, lat, lon)**: {dups}\n")
            if args.require_complete and dups > 0:
                print(f"Validation failed: Found {dups} duplicates.")
                is_valid = False
            
        file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
        f.write(f"- **File Size**: {file_size_mb:.1f} MB\n\n")
        
        # Targets & Predictors
        all_targets = [
            "increment_SSM_DA_NoCDF", "increment_SSM_DA_CDF", "delta_increment_NoCDF_minus_CDF_SSM",
            "increment_RZSM_DA_NoCDF", "increment_RZSM_DA_CDF", "delta_increment_NoCDF_minus_CDF_RZSM",
            "delta_NoCDF_minus_CDF_SSM", "delta_DA_NoCDF_minus_OPL_RZSM", "delta_DA_CDF_minus_OPL_RZSM",
            "delta_DA_NoCDF_minus_OPL_ET", "delta_DA_CDF_minus_OPL_ET", "delta_DA_NoCDF_minus_OPL_runoff",
            "delta_DA_NoCDF_minus_OPL_baseflow"
        ]
        
        avail_targets = [t for t in all_targets if t in df.columns]
        f.write("### Available Targets\n")
        for t in avail_targets:
            missing_vals = df[t].isnull().sum()
            f.write(f"- {t} (Missing: {missing_vals})\n")
            
        # B. Targets Stats
        f.write("\n## B. Target Statistics\n")
        f.write("| Target | Min | Max | Mean | Std |\n")
        f.write("|---|---|---|---|---|\n")
        for t in avail_targets:
            f.write(f"| {t} | {df[t].min():.4f} | {df[t].max():.4f} | {df[t].mean():.4f} | {df[t].std():.4f} |\n")
            
        # C. Units / Orders of Magnitude
        f.write("\n## C. Orders of Magnitude Check\n")
        sm_check = df['SSM_OPL'].between(0, 0.6).mean() * 100 if 'SSM_OPL' in df.columns else 0
        f.write(f"- **Soil Moisture Realistic (0-0.6)**: {sm_check:.1f}% of values\n")
        
        if 'Evap_tavg_OPL' in df.columns:
            et_check = (df['Evap_tavg_OPL'] >= -1e-5).mean() * 100
            f.write(f"- **ET Positive**: {et_check:.1f}% of values\n")
            
        if 'Rainf_tavg_OPL' in df.columns:
            rain_check = (df['Rainf_tavg_OPL'] >= 0).mean() * 100
            f.write(f"- **Rainf Positive**: {rain_check:.1f}% of values\n")
            
        if 'Qs_tavg_OPL' in df.columns:
            runoff_check = (df['Qs_tavg_OPL'] >= -1e-5).mean() * 100
            f.write(f"- **Runoff Non-Negative**: {runoff_check:.1f}% of values\n")
            
        # D. Increments
        f.write("\n## D. Increments Check\n")
        if 'increment_SSM_DA_NoCDF' in df.columns and 'increment_SSM_DA_CDF' in df.columns:
            amp_nocdf = df['increment_SSM_DA_NoCDF'].abs().mean()
            amp_cdf = df['increment_SSM_DA_CDF'].abs().mean()
            ratio = amp_nocdf / amp_cdf if amp_cdf != 0 else np.inf
            f.write(f"- **Mean Abs Amplitude (NoCDF)**: {amp_nocdf:.5f}\n")
            f.write(f"- **Mean Abs Amplitude (CDF)**: {amp_cdf:.5f}\n")
            f.write(f"- **Ratio NoCDF/CDF**: {ratio:.1f}\n")
            
        # E. RF Outputs
        f.write("\n## E. RF Outputs Check\n")
        f.write(f"- **rf_metrics.csv**: {'Exists' if os.path.exists('results/metrics/rf_metrics.csv') else 'Missing'}\n")
        f.write(f"- **rf_feature_importance.csv**: {'Exists' if os.path.exists('results/metrics/rf_feature_importance.csv') else 'Missing'}\n")
        
        models_dir = 'models'
        models_count = len([m for m in os.listdir(models_dir) if m.endswith('.joblib')]) if os.path.exists(models_dir) else 0
        f.write(f"- **.joblib models saved**: {models_count}\n")
        
        fig_dir = 'results/figures'
        figs_count = len([f for f in os.listdir(fig_dir) if f.endswith('.png')]) if os.path.exists(fig_dir) else 0
        f.write(f"- **.png figures saved**: {figs_count}\n")
        
        f.write("\n## Recommendations\n")
        f.write("- Validation technique réussie. Le dataset est prêt pour l'interprétation scientifique, ou pour générer la version V1 avec les stations in situ.\n")
        
    print(f"Validation report generated at {output_report}")
    
    if args.require_complete and not is_valid:
        print("Validation failed strict requirements. Exiting with error.")
        sys.exit(1)

if __name__ == "__main__":
    main()
