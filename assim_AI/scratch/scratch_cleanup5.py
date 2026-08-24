# Author: M. EL Aabaribaoune (@um6p)
import os
import shutil
import hashlib
import glob
from datetime import datetime

base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/"
os.chdir(base_dir)

archive_dir = "_ARCHIVE_BEFORE_Q1_DUPLICATE_CLEANUP_20260808"
os.makedirs(archive_dir, exist_ok=True)

patterns_to_archive = [
    "outputs/figures/q1_fig_*.png",
    "outputs/tables/q1_*.csv",
    "reports/q1_*.md",
    "reports/q1_*.zip"
]

rf_files_to_archive = [
    "outputs/figures/rf_temporal_vs_spatial_cv_v02.png",
    "outputs/figures/rf_model_skill_v02_spatial_cv.png",
    "outputs/figures/rf_grouped_feature_importance_v02.png",
    "outputs/figures/rf_feature_importance_v02_spatial_cv.png",
    "outputs/figures/rf_increment_feature_importance_v02_spatial_cv.png"
]

files_to_process = []
for p in patterns_to_archive:
    files_to_process.extend(glob.glob(p))
for f in rf_files_to_archive:
    if os.path.exists(f):
        files_to_process.append(f)

def get_sha256(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

print("--- Archiving ---")
manifest_lines = []
archived_count = 0
for f in set(files_to_process):
    if not os.path.exists(f):
        print(f"Warning: {f} not found.")
        continue
    dest = os.path.join(archive_dir, os.path.basename(f))
    shutil.copy2(f, dest)
    size = os.path.getsize(f)
    sha = get_sha256(f)
    manifest_lines.append(f"{f} | {dest} | {size} | {sha}")
    archived_count += 1

with open(os.path.join(archive_dir, "manifest.txt"), "w") as f:
    f.write("original_path | archived_path | size | sha256\n")
    f.write("\n".join(manifest_lines))
    
print(f"Archived {archived_count} files and wrote manifest.")

# Deletion
print("--- Deleting Duplicates ---")

rf_mapping = {
    "outputs/figures/rf_temporal_vs_spatial_cv_v02.png": "outputs/figures/rf_skill/manuscript_rf_temporal_vs_spatial_cv.png",
    "outputs/figures/rf_model_skill_v02_spatial_cv.png": "outputs/figures/rf_skill/manuscript_rf_model_skill_spatial_cv.png",
    "outputs/figures/rf_grouped_feature_importance_v02.png": "outputs/figures/rf_grouped_importance/manuscript_rf_grouped_feature_importance.png",
    "outputs/figures/rf_feature_importance_v02_spatial_cv.png": "outputs/figures/rf_importance/manuscript_rf_feature_importance_spatial_cv.png",
    "outputs/figures/rf_increment_feature_importance_v02_spatial_cv.png": "outputs/figures/rf_importance/manuscript_rf_increment_feature_importance_spatial_cv.png"
}

deleted_count = 0
for f in set(files_to_process):
    safe_to_delete = False
    
    # Check if it's an RF figure
    if f in rf_mapping:
        if os.path.exists(rf_mapping[f]):
            safe_to_delete = True
        else:
            print(f"Safety constraint failed: copy {rf_mapping[f]} not found. Skipping deletion of {f}.")
    else:
        # It's a q1_ file
        safe_to_delete = True
        
    if safe_to_delete:
        os.remove(f)
        deleted_count += 1
        print(f"Deleted {f}")

print(f"Deleted {deleted_count} files.")
