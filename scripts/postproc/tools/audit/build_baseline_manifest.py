import os
import glob
import pandas as pd
import hashlib
from datetime import datetime
import yaml

POSTPROC_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/"
OUTPUT_DIR = os.path.join(POSTPROC_DIR, "outputs/matrix_2016/opl_vs_smap_da_scientific/")

def get_hash(filepath):
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as afile:
            buf = afile.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(65536)
        return hasher.hexdigest()
    except Exception:
        return "ERROR"

def find_dependencies():
    records = []
    
    # 1. Configs
    configs = glob.glob(os.path.join(POSTPROC_DIR, "configs/**/*.yaml"), recursive=True)
    for c in configs:
        if "smap_cdf_sensitivity_2016" in c or "global.yaml" in c or "experiments.yaml" in c or "domain" in c or "variables" in c:
            records.append({
                "filepath": os.path.relpath(c, POSTPROC_DIR),
                "type": "CONFIG",
                "dependency_class": "BASELINE_DEPENDENCY",
                "hash": get_hash(c)
            })
            
    # 2. Python Scripts
    scripts = glob.glob(os.path.join(POSTPROC_DIR, "src/**/*.py"), recursive=True)
    scripts.extend(glob.glob(os.path.join(POSTPROC_DIR, "scripts/**/*.py"), recursive=True))
    for s in scripts:
        dep_class = "PRESERVED_UNUSED"
        if "run_postproc.py" in s or "assimilation_diagnostics" in s or "domain" in s or "hydrology" in s or "runoff_partitioning" in s or "opl_vs_da" in s:
            dep_class = "BASELINE_DEPENDENCY"
        if "paper_reproductions" in s:
            dep_class = "EXPERIMENTAL"
            
        records.append({
            "filepath": os.path.relpath(s, POSTPROC_DIR),
            "type": "PYTHON_SCRIPT",
            "dependency_class": dep_class,
            "hash": get_hash(s)
        })
        
    df = pd.DataFrame(records)
    out_dir = os.path.join(OUTPUT_DIR, "tables")
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "baseline_dependency_inventory.csv"), index=False)
    print(f"Generated baseline_dependency_inventory.csv with {len(df)} records.")
    return df

def generate_manifest(dep_df):
    manifest = {
        "baseline_id": "smap_cdf_sensitivity_2016",
        "timestamp": datetime.now().isoformat(),
        "command": "python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures --make-pdf",
        "protection": {
            "protected_output_dir": "outputs/matrix_2016/figures/smap_cdf_sensitivity/",
            "allow_overwrite": False
        },
        "dependencies": dep_df.to_dict(orient="records")
    }
    
    prov_dir = os.path.join(OUTPUT_DIR, "provenance")
    os.makedirs(prov_dir, exist_ok=True)
    
    with open(os.path.join(prov_dir, "baseline_manifest.yaml"), 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False)
        
    # Also save as the baseline config
    baseline_cfg_dir = os.path.join(POSTPROC_DIR, "configs/baselines/")
    os.makedirs(baseline_cfg_dir, exist_ok=True)
    with open(os.path.join(baseline_cfg_dir, "smap_cdf_sensitivity_2016.yaml"), 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False)

if __name__ == "__main__":
    print("Building baseline dependencies and manifest...")
    df = find_dependencies()
    generate_manifest(df)
    print("Manifests generated.")
