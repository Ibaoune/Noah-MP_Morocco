# Author: M. El Aabaribaoune (@um6p)

import os

we = ["w180", "w140", "w100", "w060", "w020", "e020", "e060", "e100", "e140"]
ns = ["n90", "n40", "s10"]
we_antarc = ["w180", "w120", "w060", "w000", "e060", "e120"]

out_dir = "data/land_params/topo_parms/GTOPO30"

print("Fixing GTOPO30 structure for LDT...")

for lat in ns:
    for lon in we:
        name = f"gt30{lon}{lat}.dem"
        path = f"{out_dir}/{name}"
        if not os.path.exists(path):
            print(f"Creating symlink for {name}")
            os.symlink("w020n40/W020N40.DEM", path)

for lon in we_antarc:
    name = f"gt30{lon}s60.dem"
    path = f"{out_dir}/{name}"
    if not os.path.exists(path):
        print(f"Creating dummy file for {name}")
        with open(path, "wb") as f:
            f.write(b'\0' * 77760000)

print("Done!")
