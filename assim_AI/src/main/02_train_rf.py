"""
02_train_rf.py
==============

This script trains a Random Forest (RF) model to diagnose the assimilation 
process in the Noah-MP/LIS SMAP study.

Features:
- Configurable via 'config.yaml' and command-line arguments.
- Supports 'temporal' and 'spatial' cross-validation modes.
- Calculates and exports model skill metrics (R², RMSE, MAE, Pearson).
- Evaluates predictor importance using Permutation Importance.
- Saves trained model artifacts (.joblib) in the output models directory.

Usage:
    python 02_train_rf.py [--mode MODE] [--dataset DATASET] [--cv CV_MODE] [--mini-test]
"""

# Author: M. EL Aabaribaoune (@um6p)
import os
import sys
import yaml
import argparse
import pandas as pd
import numpy as np
import traceback

if not hasattr(np, 'float'): np.float = float
if not hasattr(np, 'bool'): np.bool = bool
if not hasattr(np, 'int'): np.int = int
if not hasattr(np, 'object'): np.object = object
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from scipy.stats import pearsonr

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

def train_rf():
    print("--- Starting Random Forest Training (02_train_rf.py) ---")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=None, help="Override run_mode from config")
    parser.add_argument("--dataset", default="v0", help="Dataset version to use (e.g., static)")
    parser.add_argument("--cv", default="temporal", help="Validation mode: temporal or spatial")
    parser.add_argument("--mini-test", action="store_true", help="Run a quick test on a 50k sample")
    args = parser.parse_args()
    
    config_path = "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    paths = config.get("paths", {})
    options = config.get("options", {})
    
    input_dataset = paths.get("output_dataset", "data/processed/monthly_pixel_dataset_2016_2020.parquet")
    output_metrics = paths.get("output_metrics", "results/metrics/rf_metrics.csv")
    output_feat_imp = paths.get("output_feature_importance", "results/metrics/rf_feature_importance.csv")
    output_perm_imp = "results/metrics/rf_permutation_importance.csv"
    output_models_dir = paths.get("output_models_dir", "models")
    
    if args.dataset == "static":
        input_dataset = "data/processed/monthly_pixel_dataset_2016_2020_static.parquet"
        
    if args.cv == "spatial":
        output_metrics = output_metrics.replace(".csv", "_v02_spatial_cv.csv")
        output_feat_imp = output_feat_imp.replace(".csv", "_v02_spatial_cv.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_v02_spatial_cv.csv")
        output_models_dir = output_models_dir + "_v02_spatial_cv"
    elif args.dataset == "static":
        output_metrics = output_metrics.replace(".csv", "_v01_static.csv")
        output_feat_imp = output_feat_imp.replace(".csv", "_v01_static.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_v01_static.csv")
        output_models_dir = output_models_dir + "_v01_static"
        
    run_mode = args.mode if args.mode else options.get("run_mode", "real_data")
    
    if args.mini_test:
        print("Running in MINI-TEST mode (max 50,000 rows)")
        output_metrics = output_metrics.replace(".csv", "_test.csv")
        output_feat_imp = output_feat_imp.replace(".csv", "_test.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_test.csv")
        output_models_dir = output_models_dir + "_test"
        
    print(f"Run mode: {run_mode}")
    print(f"Dataset mode: {args.dataset}")
    print(f"Validation mode: {args.cv}")
    
    if args.mini_test and args.dataset == "static":
        test_static = "data/processed/monthly_pixel_dataset_test_static.parquet"
        if os.path.exists(test_static):
            input_dataset = test_static
            
    if not os.path.exists(input_dataset):
        fallback = "data/processed/monthly_pixel_dataset.parquet"
        if args.dataset == "static":
            fallback = "data/processed/monthly_pixel_dataset_2016_2020_static.parquet"
            
        if os.path.exists(fallback):
            input_dataset = fallback
        else:
            print(f"Error: Dataset {input_dataset} not found. Run dataset builder first.")
            return
        
    print(f"Loading dataset from {input_dataset}...")
    df = pd.read_parquet(input_dataset)
    
    if args.mini_test and len(df) > 50000:
        df = df.sample(n=50000, random_state=42)
        
    if args.cv == "spatial":
        if 'north_south' in df.columns and 'east_west' in df.columns:
            df['block_ns'] = pd.qcut(df['north_south'], 5, labels=False, duplicates='drop')
            df['block_ew'] = pd.qcut(df['east_west'], 5, labels=False, duplicates='drop')
            df['spatial_block'] = df['block_ns'].astype(str) + "_" + df['block_ew'].astype(str)
        else:
            print("Error: Spatial coords north_south and east_west not found.")
            return
            
    if args.cv == "spatial":
        priority_targets = [
            "delta_increment_NoCDF_minus_CDF_SSM",
            "increment_SSM_DA_NoCDF",
            "delta_DA_NoCDF_minus_OPL_RZSM",
            "delta_DA_NoCDF_minus_OPL_ET",
            "delta_DA_NoCDF_minus_OPL_baseflow",
            "delta_increment_NoCDF_minus_CDF_RZSM",
            "delta_DA_CDF_minus_OPL_ET",
            "delta_DA_CDF_minus_OPL_RZSM"
        ]
    else:
        priority_targets = [
            "increment_SSM_DA_NoCDF", "increment_SSM_DA_CDF", "delta_increment_NoCDF_minus_CDF_SSM",
            "increment_RZSM_DA_NoCDF", "increment_RZSM_DA_CDF", "delta_increment_NoCDF_minus_CDF_RZSM",
            "delta_NoCDF_minus_CDF_SSM", "delta_DA_NoCDF_minus_OPL_RZSM", "delta_DA_CDF_minus_OPL_RZSM",
            "delta_DA_NoCDF_minus_OPL_ET", "delta_DA_CDF_minus_OPL_ET", "delta_DA_NoCDF_minus_OPL_runoff",
            "delta_DA_NoCDF_minus_OPL_baseflow"
        ]
        
    potential_predictors = [
        "precipitation_model", "SSM_OPL", "RZSM_OPL", "Evap_tavg_OPL", "Qs_tavg_OPL", "Qsb_tavg_OPL",
        "SMC_L1_OPL", "SMC_L2_OPL", "SMC_L3_OPL", "SMC_L4_OPL",
        "month", "season", "elevation", "soil_texture", "land_cover", 
        "irrigation_fraction", "crop_type", "soil_texture_dominant_fraction", "land_cover_dominant_fraction",
        "basin_id"
    ]
    
    targets = [t for t in priority_targets if t in df.columns]
    predictors = [p for p in potential_predictors if p in df.columns]
    
    categorical_features = [f for f in ["land_cover", "soil_texture", "crop_type", "basin_id", "season"] if f in predictors]
    numerical_features = [f for f in predictors if f not in categorical_features]
    
    print(f"Targets: {targets}")
    print(f"Predictors: {predictors}")
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )
    
    metrics_list = []
    perm_imp_list = []
    
    os.makedirs(output_models_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_metrics), exist_ok=True)
    
    for t in targets:
        print(f"\n[{t}] Processing...")
        
        n_est = 150 if not args.mini_test else 10
        
        if args.cv == "spatial":
            gkf = GroupKFold(n_splits=5)
            X = df[predictors]
            y = df[t].fillna(0)
            groups = df['spatial_block']
            
            fold_metrics = []
            fold_perms = []
            
            fold_idx = 0
            for train_idx, test_idx in gkf.split(X, y, groups=groups):
                fold_idx += 1
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                print(f"[{t}] Fold {fold_idx}: Train {len(X_train)}, Test {len(X_test)}")
                
                X_train_processed = preprocessor.fit_transform(X_train)
                X_test_processed = preprocessor.transform(X_test)
                
                rf = RandomForestRegressor(n_estimators=n_est, max_features="sqrt", min_samples_leaf=5, random_state=42, n_jobs=-1)
                rf.fit(X_train_processed, y_train)
                
                preds = rf.predict(X_test_processed)
                r2 = r2_score(y_test, preds)
                rmse = np.sqrt(mean_squared_error(y_test, preds))
                mae = mean_absolute_error(y_test, preds)
                pearson, _ = pearsonr(y_test, preds) if len(y_test) > 1 else (np.nan, np.nan)
                
                fold_metrics.append({
                    "Target": t, "Fold": fold_idx, "R2": r2, "RMSE": rmse, "MAE": mae, "Pearson": pearson
                })
                
                pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', rf)])
                perm_sample_size = min(len(X_test), 10000) 
                X_test_perm = X_test.sample(n=perm_sample_size, random_state=42)
                y_test_perm = y_test.loc[X_test_perm.index]
                
                perm_results = permutation_importance(pipeline, X_test_perm, y_test_perm, n_repeats=3, random_state=42, n_jobs=-1)
                
                for p, imp in zip(predictors, perm_results.importances_mean):
                    fold_perms.append({"Target": t, "Predictor": p, "Fold": fold_idx, "Importance": imp})
            
            mean_r2 = np.mean([m['R2'] for m in fold_metrics])
            mean_rmse = np.mean([m['RMSE'] for m in fold_metrics])
            mean_mae = np.mean([m['MAE'] for m in fold_metrics])
            mean_pearson = np.mean([m['Pearson'] for m in fold_metrics])
            
            metrics_list.append({
                "Target": t, "R2": mean_r2, "RMSE": mean_rmse, "MAE": mean_mae, "Pearson": mean_pearson,
                "Bias": 0, "Std_Obs": 0, "Std_Pred": 0 
            })
            print(f"[{t}] Spatial CV Mean R2: {mean_r2:.4f}, Mean Pearson: {mean_pearson:.4f}")
            
            fold_perms_df = pd.DataFrame(fold_perms)
            mean_perms = fold_perms_df.groupby('Predictor')['Importance'].mean().reset_index()
            for _, row in mean_perms.iterrows():
                perm_imp_list.append({
                    "Target": t, "Predictor": row['Predictor'], "Importance": row['Importance'], "Importance_Type": "Permutation_CV_Mean"
                })
                
        else:
            train_years = options.get("train_years", [2016, 2017, 2018, 2019])
            test_years = options.get("test_years", [2020])
            
            if "year" in df.columns and not args.mini_test:
                train_df = df[df["year"].isin(train_years)]
                test_df = df[df["year"].isin(test_years)]
            else:
                train_df = df.sample(frac=0.8, random_state=42)
                test_df = df.drop(train_df.index)
                
            if len(test_df) == 0:
                train_df = df.sample(frac=0.8, random_state=42)
                test_df = df.drop(train_df.index)
                
            X_train = train_df[predictors]
            X_test = test_df[predictors]
            y_train = train_df[t].fillna(0)
            y_test = test_df[t].fillna(0)
            
            X_train_processed = preprocessor.fit_transform(X_train)
            X_test_processed = preprocessor.transform(X_test)
            
            rf = RandomForestRegressor(n_estimators=n_est, max_features="sqrt", min_samples_leaf=5, random_state=42, n_jobs=-1)
            rf.fit(X_train_processed, y_train)
            
            preds = rf.predict(X_test_processed)
            r2 = r2_score(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            mae = mean_absolute_error(y_test, preds)
            pearson, _ = pearsonr(y_test, preds) if len(y_test) > 1 else (np.nan, np.nan)
            
            metrics_list.append({
                "Target": t, "R2": r2, "RMSE": rmse, "MAE": mae, "Pearson": pearson,
                "Bias": np.mean(preds - y_test), "Std_Obs": np.std(y_test), "Std_Pred": np.std(preds)
            })
            print(f"[{t}] R2: {r2:.4f}, Pearson: {pearson:.4f}")
            
            print(f"[{t}] Calculating Permutation Importance...")
            pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', rf)])
            perm_sample_size = min(len(X_test), 50000)
            X_test_perm = X_test.sample(n=perm_sample_size, random_state=42)
            y_test_perm = y_test.loc[X_test_perm.index]
            
            perm_results = permutation_importance(pipeline, X_test_perm, y_test_perm, n_repeats=5, random_state=42, n_jobs=-1)
            for p, imp in zip(predictors, perm_results.importances_mean):
                perm_imp_list.append({"Target": t, "Predictor": p, "Importance": imp, "Importance_Type": "Permutation"})
                
            joblib.dump(rf, os.path.join(output_models_dir, f"rf_{t}.joblib"))
            
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(output_metrics, index=False)
    
    perm_imp_df = pd.DataFrame(perm_imp_list)
    perm_imp_df.to_csv(output_perm_imp, index=False)
    
    print(f"\nSaved metrics to {output_metrics}")
    print(f"Saved permutation importances to {output_perm_imp}")
    print("Training pipeline completed successfully.")

if __name__ == "__main__":
    train_rf()
