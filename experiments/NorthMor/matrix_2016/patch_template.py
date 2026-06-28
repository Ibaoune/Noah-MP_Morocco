import sys
with open(sys.argv[1], 'r') as f:
    text = f.read()

old_lsm = "#-----------------------LAND SURFACE MODELS--------------------------"
irr_block = """#-----------------------IRRIGATION CONFIGURATION---------------------
Irrigation scheme:                          "Sprinkler"
Irrigation output interval:                 "1da"
Irrigation threshold:                       0.50
Irrigation max soil layer depth:            2
Sprinkler irrigation max root depth file:   ./data/land_params/noahmp401_parms/maxrootdepth32.txt
Irrigation GVF parameter 1:                 0.40
Irrigation GVF parameter 2:                 0.00

"""
if irr_block not in text:
    text = text.replace(old_lsm, irr_block + old_lsm)
text = text.replace("lis_input_NorthMor_5km.nc", "lis_input_NorthMor_5km_irr.nc")
with open(sys.argv[1], 'w') as f:
    f.write(text)
