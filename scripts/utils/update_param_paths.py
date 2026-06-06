#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os
import glob

config_files = glob.glob('configs/lis.config.*') + glob.glob('spinup/configs/lis.config.*')

for filepath in config_files:
    if not os.path.isfile(filepath): continue
    if "tmp" in filepath: continue
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Replace parameter table paths
    content = content.replace('./data/land_params/noah_2dparms/VEGPARM.TBL', './data/land_params/noahmp401_parms/VEGPARM.TBL')
    content = content.replace('./data/land_params/noah_2dparms/SOILPARM.TBL', './data/land_params/noahmp401_parms/SOILPARM.TBL')
    content = content.replace('./data/land_params/noah_2dparms/GENPARM.TBL', './data/land_params/noahmp401_parms/GENPARM.TBL')
    content = content.replace('./data/land_params/noah_2dparms/MPTABLE.TBL', './data/land_params/noahmp401_parms/MPTABLE.TBL')
    
    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Updated parameter paths in {filepath}")
