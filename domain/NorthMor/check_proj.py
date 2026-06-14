import shapefile
import matplotlib.pyplot as plt
import numpy as np
import os
from pyproj import Transformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIMITS_DIR = os.path.join(BASE_DIR, 'Basins_limits')

# Shapefiles
shape_files = [
    ('Bouregreg', 'BV_Bouregreg_ExportFeatures.shp'),
    ('ABHBC', 'Limite_ABHBC.shp'),
    ('ABHOER', 'Limite_ABHOER.shp'),
    ('ABHS', 'Limite_ABHS_Export.shp'),
    ('ABHT', 'Limite_ABHT.shp')
]

# We need to figure out the EPSG of these shapefiles.
# Most likely EPSG:3857, EPSG:32630, or EPSG:4326.
# Let's read the .prj files.
for name, shp_name in shape_files:
    prj_file = os.path.join(LIMITS_DIR, shp_name.replace('.shp', '.prj'))
    if os.path.exists(prj_file):
        with open(prj_file, 'r') as f:
            print(f"{name} PRJ: {f.read()[:100]}")
