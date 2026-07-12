import os
import glob
import pandas as pd
import hashlib
from datetime import datetime

VALIDATION_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/validation/"
OUTPUT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/"

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

def build_file_inventory():
    records = []
    for root, dirs, files in os.walk(VALIDATION_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, VALIDATION_DIR)
            stat = os.stat(filepath)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
            ext = os.path.splitext(file)[1].lower()
            
            is_compressed = ext in ['.gz', '.zip', '.tar']
            try:
                with open(filepath, 'rb') as f:
                    f.read(1)
                readability = "OK"
            except Exception:
                readability = "UNREADABLE"
                
            records.append({
                "filename": file,
                "relative_path": rel_path,
                "size_bytes": size,
                "format": ext,
                "modification_time": mtime,
                "is_compressed": is_compressed,
                "readability_status": readability,
                "hash": get_hash(filepath) if size < 100*1024*1024 else "SKIPPED_LARGE",
                "empty_or_corrupt": size == 0 or readability == "UNREADABLE"
            })
            
    df = pd.DataFrame(records)
    out_dir = os.path.join(OUTPUT_DIR, "tables")
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "validation_file_inventory.csv"), index=False)
    print(f"Generated validation_file_inventory.csv with {len(df)} records.")
    return df

def search_for_scripts():
    import subprocess
    cmd = 'grep -r -i -E "wget|curl|download|validation|wapor|grace|ascat|mswep" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/ --include="*.py" --include="*.sh" --include="*.ipynb"'
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        with open(os.path.join(OUTPUT_DIR, "tables", "validation_scripts_search_results.txt"), "w") as f:
            f.write(output)
        print("Found related scripts/notebooks.")
    except Exception as e:
        print("No script references found or error.", e)

def main():
    print("Starting validation data file inventory...")
    build_file_inventory()
    search_for_scripts()

if __name__ == "__main__":
    main()
