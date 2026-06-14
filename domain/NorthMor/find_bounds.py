import shapefile
import matplotlib.pyplot as plt
import numpy as np
import os
from pyproj import Transformer, CRS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIMITS_DIR = os.path.join(BASE_DIR, 'Basins_limits')

shape_files = [
    ('Bouregreg', 'BV_Bouregreg_ExportFeatures.shp', 'red'),
    ('ABHBC', 'Limite_ABHBC.shp', 'orange'),
    ('ABHOER', 'Limite_ABHOER.shp', 'purple'),
    ('ABHS', 'Limite_ABHS_Export.shp', 'blue'),
    ('ABHT', 'Limite_ABHT.shp', 'cyan')
]

fig, ax = plt.subplots(figsize=(12, 10))
all_lons = []
all_lats = []

for name, shp_name, color in shape_files:
    shp_path = os.path.join(LIMITS_DIR, shp_name)
    prj_path = shp_path.replace('.shp', '.prj')
    
    if name == 'Bouregreg':
        crs_src = CRS.from_epsg(26191) # Merchich / Nord Maroc
    else:
        crs_src = CRS.from_epsg(3857) # Web Mercator
    crs_dst = CRS.from_epsg(4326) # WGS84
    transformer = Transformer.from_crs(crs_src, crs_dst, always_xy=True)
    
    shp_file = open(shp_path, 'rb')
    shx_file = open(shp_path.replace('.shp', '.shx'), 'rb')
    sf = shapefile.Reader(shp=shp_file, shx=shx_file)
    
    # get bounds
    min_x, min_y, max_x, max_y = sf.bbox
    corners = [
        transformer.transform(min_x, min_y),
        transformer.transform(min_x, max_y),
        transformer.transform(max_x, min_y),
        transformer.transform(max_x, max_y)
    ]
    lons = [c[0] for c in corners]
    lats = [c[1] for c in corners]
    
    all_lons.extend(lons)
    all_lats.extend(lats)
    
    # Plotting
    for shape in sf.shapes():
        parts = shape.parts
        parts.append(len(shape.points))
        for i in range(len(parts)-1):
            points = shape.points[parts[i]:parts[i+1]]
            x = [transformer.transform(p[0], p[1])[0] for p in points]
            y = [transformer.transform(p[0], p[1])[1] for p in points]
            if i == 0:
                ax.plot(x, y, color=color, linewidth=2, label=name)
            else:
                ax.plot(x, y, color=color, linewidth=2)

import json

# Plot morocco map
geojson_path = os.path.join(BASE_DIR, '../sebou/morocco_map.geojson')
if os.path.exists(geojson_path):
    with open(geojson_path, 'r') as f:
        morocco_data = json.load(f)
    for geometry in morocco_data['geometries']:
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]
            xs, ys = zip(*coords)
            ax.plot(xs, ys, color='grey', linewidth=1.5, alpha=0.5)
        elif geometry['type'] == 'MultiPolygon':
            for polygon in geometry['coordinates']:
                coords = polygon[0]
                xs, ys = zip(*coords)
                ax.plot(xs, ys, color='grey', linewidth=1.5, alpha=0.5)

min_lon = min(all_lons)
max_lon = max(all_lons)
min_lat = min(all_lats)
max_lat = max(all_lats)

print(f"\nShapefiles Bounding Box:")
print(f"Min Lon: {min_lon:.4f}, Min Lat: {min_lat:.4f}")
print(f"Max Lon: {max_lon:.4f}, Max Lat: {max_lat:.4f}")

# Define new domain with user provided limits
new_min_lon = -10.0
new_max_lon = -1.0
new_min_lat = 30.0
new_max_lat = 36.0

print(f"\nNew Suggested Domain (User bounds):")
print(f"Lat: {new_min_lat} to {new_max_lat}")
print(f"Lon: {new_min_lon} to {new_max_lon}")

# Calculate number of grid points for new domain (dx=0.01, dy=0.01)
dx, dy = 0.05, 0.05
nlon = int(round((new_max_lon - new_min_lon) / dx)) + 1
nlat = int(round((new_max_lat - new_min_lat) / dy)) + 1

print(f"\nCharacteristics for dx={dx}, dy={dy}:")
print(f"Number of lons: {nlon}")
print(f"Number of lats: {nlat}")
print(f"Total grid points: {nlon * nlat}")

ax.plot([new_min_lon, new_max_lon, new_max_lon, new_min_lon, new_min_lon],
        [new_min_lat, new_min_lat, new_max_lat, new_max_lat, new_min_lat],
        color='black', linestyle='--', linewidth=2, label='Proposed LIS Domain')

# Set map limits to show full Morocco
ax.set_xlim([-18, 0])
ax.set_ylim([20, 40])
ax.grid(True, linestyle=':')

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='upper left')

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Noah-MP Domain and Morocco Boundaries')
plot_path = os.path.join(BASE_DIR, 'domain_plot.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to {plot_path}")
