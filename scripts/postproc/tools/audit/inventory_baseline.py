import os
import glob
import pandas as pd
import hashlib
from datetime import datetime
import json

BASELINE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/figures/smap_cdf_sensitivity/"
OUTPUT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/tables/"

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

def extract_json_metrics(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return str(list(data.keys()))[:100]
    except Exception:
        return ""

def snapshot_baseline():
    records = []
    
    # Snapshot all files in baseline dir
    for root, dirs, files in os.walk(BASELINE_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, BASELINE_DIR)
            stat = os.stat(filepath)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            ext = os.path.splitext(file)[1].lower()
            metrics_summary = extract_json_metrics(filepath) if ext == '.json' else ""
                
            records.append({
                "filename": file,
                "relative_path": rel_path,
                "size_bytes": size,
                "modification_time": mtime,
                "hash": get_hash(filepath),
                "metrics_summary": metrics_summary
            })
            
    df = pd.DataFrame(records)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, "baseline_output_inventory.csv"), index=False)
    print(f"Generated baseline_output_inventory.csv with {len(df)} records.")

if __name__ == "__main__":
    print("Snapshotting baseline outputs...")
    snapshot_baseline()
