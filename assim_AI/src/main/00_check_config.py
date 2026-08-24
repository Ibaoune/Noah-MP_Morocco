# Author: M. EL Aabaribaoune (@um6p)
import yaml
import os
import sys

def check_config(config_path="config.yaml"):
    print(f"Loading configuration from {config_path}...")
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found.")
        return False
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    sections = ["paths", "options"]
    for sec in sections:
        if sec not in config:
            print(f"Error: Missing required section '{sec}' in config.")
            return False
            
    paths = config["paths"]
    
    # 1. Create output directories if they don't exist
    output_files = [
        paths.get("output_dataset", ""),
        paths.get("output_metrics", ""),
        paths.get("output_feature_importance", ""),
        paths.get("output_dominant_factor_map", "")
    ]
    
    dirs_to_create = [
        paths.get("output_models_dir", ""),
        paths.get("output_figures_dir", ""),
        paths.get("reports_dir", "reports"),
    ]
    
    # Also create directories for the output files
    for f in output_files:
        if f:
            dirs_to_create.append(os.path.dirname(f))
            
    for d in set(dirs_to_create):
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            print(f"Created directory: {d}")
            
    # 2. Check input paths and warn if missing (no fatal error)
    print("\n--- Checking paths ---")
    missing_paths = []
    for key, path in paths.items():
        if "output" in key or "reports" in key:
            continue
        if isinstance(path, dict):
            continue
        if not path or path == "null" or "placeholder_path" in str(path) or not os.path.exists(str(path)):
            missing_paths.append(f"{key}: {path}")
            
    if missing_paths:
        print("WARNING: The following input paths are missing or still set as placeholders:")
        for mp in missing_paths:
            print(f"  - {mp}")
        print("The pipeline will skip full processing until these are provided.")
    else:
        print("All input paths exist.")
        
    print("\nConfiguration check complete. Architecture is stable.")
    return True

if __name__ == "__main__":
    check_config()
