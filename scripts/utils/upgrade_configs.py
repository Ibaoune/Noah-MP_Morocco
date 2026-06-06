import os
import glob

config_files = glob.glob('configs/lis.config.*') + ['spinup/configs/lis.config.spinup_cycle1.tmp']

for filepath in config_files:
    if not os.path.isfile(filepath): continue
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Replace the model name
    content = content.replace('Land surface model:                     "NoahMP.3.6"', 'Land surface model:                     "Noah-MP.4.0.1"')
    content = content.replace('Land surface model:                     "Noah-MP.3.6"', 'Land surface model:                     "Noah-MP.4.0.1"')
    
    # Replace all prefixes
    content = content.replace('Noah-MP.3.6 ', 'Noah-MP.4.0.1 ')
    
    # Configure HyMAP if routing is none
    if 'Routing model:                          "none"' in content:
        hymap_config = """Routing model:                          "HYMAP router"

#HYMAP router
HYMAP routing model time step:                 15mn
HYMAP routing model output interval:           1da
HYMAP routing model restart interval:          1mo
HYMAP run in ensemble mode:                    0
HYMAP routing method:                          kinematic
HYMAP routing model linear reservoir flag:     1
HYMAP routing model evaporation option:        2
HYMAP routing model restart file:              none
HYMAP routing model start mode:                coldstart
HYMAP routing LIS output directory:            "routing"
"""
        content = content.replace('Routing model:                          "none"', hymap_config)
    
    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"Updated {filepath}")
