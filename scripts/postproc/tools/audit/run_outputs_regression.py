import os
import yaml
import hashlib
import pandas as pd

SNAPSHOT_PATH = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/baseline_outputs_snapshot.yaml'
OUT_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/'
OUTPUTS_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/figures/smap_cdf_sensitivity/'

def get_hash(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def run_regression():
    with open(SNAPSHOT_PATH, 'r') as f:
        snapshot = yaml.safe_load(f)
        
    rows = []
    status = "PASSED"
    
    for f_info in snapshot:
        path = os.path.join(OUTPUTS_DIR, f_info['filepath'])
        if not os.path.exists(path):
            rows.append({"type": f_info['type'], "path": f_info['filepath'], "expected_size": f_info['size'], "actual_size": "MISSING", "expected_hash": f_info['hash'], "actual_hash": "MISSING", "status": "FAILED"})
            status = "FAILED"
            continue
            
        current_size = os.path.getsize(path)
        current_hash = get_hash(path)
        
        row_status = "PASSED"
        if current_size != f_info['size'] or current_hash != f_info['hash']:
            row_status = "FAILED"
            status = "FAILED"
            
        rows.append({
            "type": f_info['type'],
            "path": f_info['filepath'],
            "expected_size": f_info['size'],
            "actual_size": current_size,
            "expected_hash": f_info['hash'],
            "actual_hash": current_hash,
            "status": row_status
        })
            
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "baseline_regression_comparison.csv"), index=False)
    
    with open(os.path.join(OUT_DIR, "baseline_regression_report.md"), "w") as f:
        f.write("# Baseline Regression Report\n\n")
        f.write(f"**Conclusion:** {status}\n\n")
        failed = [r for r in rows if r["status"] == "FAILED"]
        if failed:
            f.write("## Failed Items\n")
            for r in failed:
                f.write(f"- {r['path']}\n")
        else:
            f.write("All baseline files perfectly match the original snapshot (sizes and hashes).\n")
            
    print(f"Outputs regression check finished with status {status}")

if __name__ == "__main__":
    run_regression()
