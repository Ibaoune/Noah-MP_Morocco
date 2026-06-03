# Author: M. EL Aabaribaoune (@um6p)

import shapefile
import matplotlib.pyplot as plt
import numpy as np
import os
from pyproj import Transformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load shapefiles
sebou = shapefile.Reader(os.path.join(BASE_DIR, 'shapefiles/Sebou_limits/Limite_ABHS.shp'))
elfassi = shapefile.Reader(os.path.join(BASE_DIR, 'shapefiles/ElFassi_Extent/1ElFassiWatershed.shp'))

# Transformers
transformer_sebou = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True) # Web Mercator
transformer_elfassi = Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True) # UTM zone 30N

def get_transformed_bounds(shp, transformer):
    min_x, min_y, max_x, max_y = shp.bbox
    # corners
    corners = [
        transformer.transform(min_x, min_y),
        transformer.transform(min_x, max_y),
        transformer.transform(max_x, min_y),
        transformer.transform(max_x, max_y)
    ]
    lons = [c[0] for c in corners]
    lats = [c[1] for c in corners]
    return min(lons), min(lats), max(lons), max(lats)

bounds_s = get_transformed_bounds(sebou, transformer_sebou)
bounds_e = get_transformed_bounds(elfassi, transformer_elfassi)

# Combined bounds (min_lon, min_lat, max_lon, max_lat)
min_lon = min(bounds_s[0], bounds_e[0])
min_lat = min(bounds_s[1], bounds_e[1])
max_lon = max(bounds_s[2], bounds_e[2])
max_lat = max(bounds_s[3], bounds_e[3])

print(f"\nShapefiles Bounding Box:")
print(f"Min Lon: {min_lon:.4f}, Min Lat: {min_lat:.4f}")
print(f"Max Lon: {max_lon:.4f}, Max Lat: {max_lat:.4f}")

# Define new domain with user-provided bounds
new_min_lon = -7.0
new_max_lon = -3.5
new_min_lat = 32.5
new_max_lat = 35.5

print(f"\nNew Suggested Domain (User Bounds):")
print(f"Lat: {new_min_lat} to {new_max_lat}")
print(f"Lon: {new_min_lon} to {new_max_lon}")

# Calculate number of grid points for new domain (dx=0.01, dy=0.01)
dx, dy = 0.01, 0.01
nlon = int(round((new_max_lon - new_min_lon) / dx)) + 1
nlat = int(round((new_max_lat - new_min_lat) / dy)) + 1

print(f"\nCharacteristics for dx=0.01, dy=0.01:")
print(f"Number of lons: {nlon}")
print(f"Number of lats: {nlat}")
print(f"Total grid points: {nlon * nlat}")

# Plotting
fig, ax = plt.subplots(figsize=(10, 8))

for shape in sebou.shapes():
    parts = shape.parts
    parts.append(len(shape.points))
    for i in range(len(parts)-1):
        points = shape.points[parts[i]:parts[i+1]]
        x = [transformer_sebou.transform(p[0], p[1])[0] for p in points]
        y = [transformer_sebou.transform(p[0], p[1])[1] for p in points]
        if i == 0:
            ax.plot(x, y, color='blue', linewidth=2, label='Sebou Basin')
        else:
            ax.plot(x, y, color='blue', linewidth=2)

for shape in elfassi.shapes():
    parts = shape.parts
    parts.append(len(shape.points))
    for i in range(len(parts)-1):
        points = shape.points[parts[i]:parts[i+1]]
        x = [transformer_elfassi.transform(p[0], p[1])[0] for p in points]
        y = [transformer_elfassi.transform(p[0], p[1])[1] for p in points]
        if i == 0:
            ax.plot(x, y, color='red', linewidth=2, label='ElFassi Subbasin')
        else:
            ax.plot(x, y, color='red', linewidth=2)

# Plot new domain
ax.plot([new_min_lon, new_max_lon, new_max_lon, new_min_lon, new_min_lon],
        [new_min_lat, new_min_lat, new_max_lat, new_max_lat, new_min_lat],
        color='green', linestyle='-', linewidth=2, label='Domain Extent')

ax.set_xlim([new_min_lon - 0.5, new_max_lon + 0.5])
ax.set_ylim([new_min_lat - 0.5, new_max_lat + 0.5])
ax.grid(True, linestyle=':')

# avoid duplicate labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Noah-MP Morocco Domain and Basin Boundaries')
plot_path = os.path.join(BASE_DIR, 'domain_plot.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to {plot_path}")
