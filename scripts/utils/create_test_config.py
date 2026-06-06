#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os

with open("spinup/configs/lis.config.spinup_sebou", "r") as f:
    config = f.read()

# Disable HyMAP routing for the test
config = config.replace('Routing model:                          "HYMAP router"', 'Routing model:                          "none"')

# Change end date to run for just 1 day
config = config.replace('Ending month:                           04', 'Ending month:                           01')
config = config.replace('Ending day:                             01', 'Ending day:                             02')

# Change log output
config = config.replace('Diagnostic output file:                 "spinup/SPINUP_sebou/cycle1/lislog"', 'Diagnostic output file:                 "spinup/SPINUP_sebou/cycle1/lislog_test"')

with open("spinup/configs/lis.config.test", "w") as f:
    f.write(config)

print("Created spinup/configs/lis.config.test")
