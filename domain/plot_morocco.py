import matplotlib.pyplot as plt
import numpy as np
import os
from mpl_toolkits.basemap import Basemap
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Domain bounds
new_min_lon = -7.0
new_max_lon = -3.5
new_min_lat = 32.5
new_max_lat = 35.5

fig, ax = plt.subplots(figsize=(10, 10))

# Create basemap of Morocco including Western Sahara (roughly Lat 20 to 37, Lon -18 to 0)
m = Basemap(projection='merc', llcrnrlat=20.5, urcrnrlat=36.5,
            llcrnrlon=-17.5, urcrnrlon=-0.5, resolution='i', ax=ax)

m.drawcoastlines(linewidth=1.0)
m.drawcountries(linewidth=1.0)
m.fillcontinents(color='lightgray', lake_color='aqua')
m.drawmapboundary(fill_color='aqua')

# Draw parallels and meridians
m.drawparallels(np.arange(20., 40., 5.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-20., 0., 5.), labels=[0,0,0,1], fontsize=10)

# Convert domain coordinates to map projection
x1, y1 = m(new_min_lon, new_min_lat)
x2, y2 = m(new_max_lon, new_max_lat)

# Plot domain bounding box
width = x2 - x1
height = y2 - y1
rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor='red', facecolor='red', alpha=0.5, zorder=10)
ax.add_patch(rect)

# Add a text label
plt.text(x1 + width/2, y1 + height/2, 'Noah-MP\nDomain', 
         horizontalalignment='center', verticalalignment='center',
         fontsize=12, fontweight='bold', color='black', zorder=11)

plt.title('Domain Location over Morocco (including Sahara)', fontsize=14, pad=20)

plot_path = os.path.join(BASE_DIR, 'morocco_domain_map.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"Plot saved to {plot_path}")
