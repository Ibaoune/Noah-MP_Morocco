# Author: M. EL Aabaribaoune (@um6p)

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Domain bounds
new_min_lon = -7.0
new_max_lon = -3.5
new_min_lat = 32.5
new_max_lat = 35.5

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('#f8f9fa')  # Light background

# Load GeoJSON
with open('/tmp/maroc.geojson', 'r', encoding='utf-8') as f:
    geojson = json.load(f)

# Plot each feature
for feature in geojson['features']:
    geom = feature['geometry']
    if geom['type'] == 'MultiPolygon':
        for poly in geom['coordinates']:
            for ring in poly:
                x = [p[0] for p in ring]
                y = [p[1] for p in ring]
                # Plot filled polygon
                ax.fill(x, y, color='#EAE3D9', zorder=1)
                # Plot border
                ax.plot(x, y, color='#888888', linewidth=0.5, zorder=2)

# Set grid
ax.grid(True, linestyle='-', linewidth=0.5, color='#e0e0e0', zorder=0)

# Set axes limits
ax.set_xlim([-18, -1])
ax.set_ylim([20, 37])

# Cities coordinates
cities = {
    'Tangier': (-5.8340, 35.7595),
    'Fes': (-5.0003, 34.0331),
    'Rabat': (-6.8416, 34.0209),
    'Casablanca': (-7.5898, 33.5731),
    'Marrakech': (-7.9811, 31.6295)
}

# Plot cities
for city, (lon, lat) in cities.items():
    ax.plot(lon, lat, 'ko', markersize=4, zorder=4)
    # Add offset to text
    ax.text(lon - 0.2, lat - 0.2, city, fontsize=10, fontweight='bold',
            horizontalalignment='right', verticalalignment='top', zorder=5)

# Ocean Labels
ax.text(-12, 30.5, 'ATLANTIC\nOCEAN', fontsize=12, fontweight='bold', fontstyle='italic',
        color='#3A7CA5', horizontalalignment='center', zorder=3)
ax.text(-3, 36.2, 'MEDITERRANEAN SEA', fontsize=10, fontweight='bold', fontstyle='italic',
        color='#3A7CA5', horizontalalignment='center', zorder=3)

# Plot domain bounding box
width = new_max_lon - new_min_lon
height = new_max_lat - new_min_lat
rect = patches.Rectangle((new_min_lon, new_min_lat), width, height, 
                         linewidth=1.5, edgecolor='#d9534f', facecolor='#d9534f', 
                         alpha=0.4, linestyle='--', zorder=6)
ax.add_patch(rect)

# Removed text label inside/near the box as requested

# Labels and Title
ax.set_xlabel('Longitude (°E)', fontweight='bold')
ax.set_ylabel('Latitude (°N)', fontweight='bold')
ax.set_title('Location of the Sebou Basin Study Area within Morocco', fontsize=14, fontweight='bold', pad=15)

# Legend
legend_element = [patches.Patch(facecolor='#d9534f', edgecolor='none', alpha=0.4, label='Study Area')]
ax.legend(handles=legend_element, loc='lower left', frameon=False)

plot_path = os.path.join(BASE_DIR, 'morocco_domain_map.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"Plot saved to {plot_path}")
