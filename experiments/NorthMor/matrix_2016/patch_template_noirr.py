import sys
with open(sys.argv[1], 'r') as f:
    text = f.read()

old_lsm = "#-----------------------LAND SURFACE MODELS--------------------------"
irr_block = """#-----------------------IRRIGATION CONFIGURATION---------------------
Irrigation scheme:                          "none"

"""
if irr_block not in text:
    text = text.replace(old_lsm, irr_block + old_lsm)
with open(sys.argv[1], 'w') as f:
    f.write(text)
