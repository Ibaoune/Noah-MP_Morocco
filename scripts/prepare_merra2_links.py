import os
import glob
import re

base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2"
os.chdir(base_dir)

variables = ["M2T1NXFLX", "M2T1NXRAD", "M2T1NXSLV"]
pattern = re.compile(r'\.(\d{4})(\d{2})\d{2}\.nc4$')

count = 0
for var in variables:
    if not os.path.isdir(var):
        continue
    print(f"Processing {var}...")
    files = glob.glob(f"{var}/*.nc4")
    for f in files:
        filename = os.path.basename(f)
        match = pattern.search(filename)
        if match:
            yyyy, mm = match.groups()
            target_dir = f"MERRA2_400/Y{yyyy}/M{mm}"
            os.makedirs(target_dir, exist_ok=True)
            
            target_link = os.path.join(target_dir, filename)
            if os.path.lexists(target_link):
                os.unlink(target_link)
                
            # path relative to target_dir: ../../../var/filename
            source = f"../../../{var}/{filename}"
            os.symlink(source, target_link)
            count += 1

print(f"Created {count} new symlinks.")
