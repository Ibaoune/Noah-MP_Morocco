import os
import yaml
import hashlib
import pandas as pd

MANIFEST_PATH = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/baseline_manifest.yaml'
OUT_DIR = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/provenance/'
PROJECT_ROOT = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/'

def get_hash(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def run_regression():
    with open(MANIFEST_PATH, 'r') as f:
        manifest = yaml.safe_load(f)
        
    rows = []
    status = "PASSED"
    
    # Check dependencies
    for dep in manifest.get('dependencies', []):
        path = os.path.join(PROJECT_ROOT, dep['filepath'])
        if not os.path.exists(path):
            rows.append({"type": "dependency", "path": dep['filepath'], "expected_hash": dep.get('hash'), "actual_hash": "MISSING", "status": "FAILED"})
            status = "FAILED"
            continue
            
        current_hash = get_hash(path)
        if current_hash != dep.get('hash'):
            rows.append({"type": "dependency", "path": dep['filepath'], "expected_hash": dep.get('hash'), "actual_hash": current_hash, "status": "FAILED"})
            status = "FAILED"
        else:
            rows.append({"type": "dependency", "path": dep['filepath'], "expected_hash": dep.get('hash'), "actual_hash": current_hash, "status": "PASSED"})
            
    # Check outputs
    for out in manifest.get('outputs', []):
        path = os.path.join(PROJECT_ROOT, out['filepath'])
        if not os.path.exists(path):
            rows.append({"type": "output", "path": out['filepath'], "expected_size": out.get('size'), "actual_size": "MISSING", "status": "FAILED"})
            status = "FAILED"
            continue
            
        current_size = os.path.getsize(path)
        if current_size != out.get('size'):
            rows.append({"type": "output", "path": out['filepath'], "expected_size": out.get('size'), "actual_size": current_size, "status": "FAILED"})
            status = "FAILED"
        else:
            rows.append({"type": "output", "path": out['filepath'], "expected_size": out.get('size'), "actual_size": current_size, "status": "PASSED"})
            
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
            f.write("All baseline files and dependencies match the original snapshot perfectly (hashes and sizes).\n")
            
    print(f"Regression check finished with status {status}")

if __name__ == "__main__":
    run_regression()
