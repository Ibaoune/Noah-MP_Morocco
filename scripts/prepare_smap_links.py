import os
import glob
import re

base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/observations/SMAP_SPL3SMP_E"
os.chdir(base_dir)

# File pattern: SMAP_L3_SM_P_E_20200531_R19240_001.h5
pattern = re.compile(r'SMAP_L3_SM_P_E_(\d{4})(\d{2})(\d{2})_(R\d+)_00\d\.h5')

count = 0
files = glob.glob("raw/*.h5")
print(f"Found {len(files)} files in raw/ directory.")

for f in files:
    filename = os.path.basename(f)
    match = pattern.search(filename)
    if match:
        yyyy, mm, dd, crid = match.groups()
        target_dir = f"{yyyy}.{mm}.{dd}"
        os.makedirs(target_dir, exist_ok=True)
        
        target_link = os.path.join(target_dir, filename)
        if os.path.lexists(target_link):
            os.unlink(target_link)
            
        # path relative to target_dir is ../raw/filename
        source = f"../raw/{filename}"
        os.symlink(source, target_link)
        count += 1

print(f"Created {count} new symlinks in YYYY.MM.DD structure.")
