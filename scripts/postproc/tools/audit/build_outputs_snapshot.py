import os
import glob
import json
import hashlib
import pandas as pd
import yaml

OUTPUT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/figures/smap_cdf_sensitivity/"
PROV_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/"

def get_hash(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def build_snapshot():
    records = []
    
    files = glob.glob(os.path.join(OUTPUT_DIR, "**", "*"), recursive=True)
    
    for f in files:
        if os.path.isfile(f):
            size = os.path.getsize(f)
            ext = os.path.splitext(f)[1].lower()
            
            rec = {
                "filepath": os.path.relpath(f, OUTPUT_DIR),
                "size": size,
                "extension": ext,
                "hash": get_hash(f)
            }
            
            if ext == ".png":
                # We could use PIL but let's just record size and hash for now
                rec["type"] = "IMAGE"
            elif ext == ".json":
                rec["type"] = "METRICS"
            elif ext == ".nc":
                rec["type"] = "DATA"
            elif ext in [".yaml", ".yml"]:
                rec["type"] = "CONFIG"
            else:
                rec["type"] = "OTHER"
                
            records.append(rec)
            
    os.makedirs(PROV_DIR, exist_ok=True)
    with open(os.path.join(PROV_DIR, "baseline_outputs_snapshot.yaml"), "w") as f:
        yaml.dump(records, f, default_flow_style=False)
        
    print(f"Snapshot created with {len(records)} output files.")

if __name__ == "__main__":
    build_snapshot()
