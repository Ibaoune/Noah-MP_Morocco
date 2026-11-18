"""
Script: plot_domain_physiography.py
Purpose: Generate a clean, publication-quality two-panel figure for Section 2.1:
  - Panel (a): Regional setting of Morocco, Noah-MP 5-km grid bounding box,
              hydrologically delineated Bouregreg basin, and ABH Sebou agency perimeter.
  - Panel (b): Model domain physiography (GTOPO30 elevation), digital drainage network,
              basin boundaries, and in-situ hydrometric stations (daily vs monthly),
              with minimal annotations focused strictly on Lalla Chafia and Sidi Jabeur.
Outputs:
  - domain_physiography_hydrometric_network.png (300 dpi)
  - domain_physiography_hydrometric_network.pdf (vector)
"""

import os
import json
import numpy as np
import netCDF4 as nc
import pandas as pd

# Configure PROJ environment to avoid warnings
proj_dir = '/home/mohammad.elaabaribao/.conda/envs/gridded_dataset/share/proj'
if os.path.exists(proj_dir):
    os.environ['PROJ_LIB'] = proj_dir
    os.environ['PROJ_DATA'] = proj_dir

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from shapely.geometry import shape

# Scientific publication styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10.5
plt.rcParams['axes.titlesize'] = 11.5
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../..'))

# Paths
nc_path = os.path.join(PROJECT_ROOT, 'data/lis_input/lis_input_NorthMor_5km.nc')
hymap_nc = os.path.join(PROJECT_ROOT, 'experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc')
morocco_geojson = os.path.join(PROJECT_ROOT, 'domain/sebou/morocco_map.geojson')
limits_dir = os.path.join(BASE_DIR, 'Basins_limits')

shp_bouregreg = os.path.join(limits_dir, 'BV_Bouregreg_ExportFeatures.shp')
shp_abhs = os.path.join(limits_dir, 'Limite_ABHS_Export.shp')
stations_csv = os.path.join(PROJECT_ROOT, 'experiments/NorthMor/routing/stations/hymap_stations_pairing.csv')

output_png = os.path.join(BASE_DIR, 'domain_physiography_hydrometric_network.png')
output_pdf = os.path.join(BASE_DIR, 'domain_physiography_hydrometric_network.pdf')

print("1. Loading LIS NetCDF grid and elevation...")
ds = nc.Dataset(nc_path)
lats = ds.variables['lat'][:]
lons = ds.variables['lon'][:]
elev = ds.variables['ELEVATION'][:]
mask = ds.variables['LANDMASK'][:]
ds.close()

# Mask ocean cells
elev_land = np.ma.masked_where(mask == 0, elev)

# Load Morocco boundary GeoJSON
print("2. Loading Morocco national boundary...")
morocco_geoms = []
if os.path.exists(morocco_geojson):
    with open(morocco_geojson, 'r', encoding='utf-8') as f:
        geo_data = json.load(f)
    for g in geo_data['geometries']:
        morocco_geoms.append(shape(g))
morocco_gdf = gpd.GeoDataFrame(geometry=morocco_geoms, crs='EPSG:4326')

# Load Basin shapefiles and ensure WGS84
print("3. Loading and reprojecting basin shapefiles...")
gdf_bouregreg = gpd.read_file(shp_bouregreg).to_crs(epsg=4326)
gdf_abhs = gpd.read_file(shp_abhs).to_crs(epsg=4326)

# Extract digital river network from HyMAP
print("4. Extracting drainage reaches from HyMAP parameters...")
river_lines = []
if os.path.exists(hymap_nc):
    ds_h = nc.Dataset(hymap_nc)
    da = ds_h.variables['HYMAP_drain_area'][:] / 1e6 # km2
    fdx = ds_h.variables['HYMAP_flow_direction_x'][:]
    fdy = ds_h.variables['HYMAP_flow_direction_y'][:]
    h_lats = ds_h.variables['lat'][:]
    h_lons = ds_h.variables['lon'][:]
    ds_h.close()
    
    nr, nc_cols = da.shape
    for r in range(nr):
        for c in range(nc_cols):
            if da[r, c] >= 1000: # threshold for major river reaches (km2)
                nc_idx = int(fdx[r, c]) - 1
                nr_idx = int(fdy[r, c]) - 1
                if 0 <= nr_idx < nr and 0 <= nc_idx < nc_cols:
                    river_lines.append([(h_lons[r, c], h_lats[r, c]), 
                                        (h_lons[nr_idx, nc_idx], h_lats[nr_idx, nc_idx])])

# Load Stations
print("5. Loading hydrometric stations...")
df_stations = pd.read_csv(stations_csv)
daily_st = df_stations[df_stations['type_pas'] == 'journalier']
monthly_st = df_stations[df_stations['type_pas'] == 'mensuel']

# -------------------------------------------------------------
# FIGURE GENERATION
# -------------------------------------------------------------
print("6. Plotting simplified two-panel scientific figure...")
fig = plt.figure(figsize=(15.2, 8.2), dpi=300)
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.48], wspace=0.18)

# -------------------------------------------------------------
# PANEL A: Regional Setting of Morocco & Study Basins
# -------------------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#edf2f7') # light ocean tone

# Morocco land polygons
morocco_gdf.plot(ax=ax1, facecolor='#f8fafc', edgecolor='#64748b', linewidth=0.85, zorder=2)

# Basins in Panel A: Polygons without intrusive map labels or arrows
gdf_abhs.plot(ax=ax1, facecolor='#bae6fd', edgecolor='#0369a1', linewidth=1.1, alpha=0.65, zorder=3)
gdf_bouregreg.plot(ax=ax1, facecolor='#fecaca', edgecolor='#b91c1c', linewidth=1.1, alpha=0.75, zorder=4)

# Noah-MP Domain Bounding Box
dom_box_lon = [-10.0, -1.0, -1.0, -10.0, -10.0]
dom_box_lat = [30.0, 30.0, 36.0, 36.0, 30.0]
ax1.plot(dom_box_lon, dom_box_lat, color='#0f172a', linestyle='--', linewidth=1.8, zorder=5)

# Subtle geographic landmarks in Panel A
ax1.text(-7.8, 31.5, 'High Atlas', fontsize=8.5, color='#475569', fontstyle='italic', zorder=6)
ax1.text(-5.0, 33.2, 'Middle Atlas', fontsize=8.5, color='#475569', fontstyle='italic', zorder=6)
ax1.text(-4.8, 35.0, 'Rif', fontsize=8.5, color='#475569', fontstyle='italic', zorder=6)
ax1.text(-14.0, 27.0, 'Atlantic Ocean', fontsize=9.5, color='#64748b', fontstyle='italic', zorder=6)
ax1.text(-3.5, 36.6, 'Mediterranean Sea', fontsize=9.0, color='#64748b', fontstyle='italic', zorder=6)

# Panel A bounds and styling
ax1.set_xlim([-17.5, 0.0])
ax1.set_ylim([21.0, 37.5])
ax1.set_xlabel('Longitude (°W)')
ax1.set_ylabel('Latitude (°N)')
ax1.set_title('(a) Regional Setting & Modeling Extent', weight='bold', loc='left', pad=8)
ax1.grid(True, linestyle=':', color='#cbd5e1', alpha=0.7)

# Panel A Legend: Simple, sober, exact nomenclature requested
legend_a = [
    Line2D([0], [0], color='#0f172a', linestyle='--', lw=1.8, label='Noah-MP domain (5 km)'),
    mpatches.Patch(facecolor='#fecaca', edgecolor='#b91c1c', lw=1.1, label='Bouregreg hydrologic watershed'),
    mpatches.Patch(facecolor='#bae6fd', edgecolor='#0369a1', lw=1.1, label='Sebou region (ABHS boundary)')
]
ax1.legend(handles=legend_a, loc='lower left', framealpha=0.95, edgecolor='#cbd5e1', fontsize=8.5)

# -------------------------------------------------------------
# PANEL B: Noah-MP Elevation, River Network & Gauge Network
# -------------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#edf2f7') # neutral ocean

# DEM Colormap (terrain)
terrain_cmap = plt.cm.terrain
norm = mcolors.Normalize(vmin=0, vmax=3500)

# Raster surface elevation
mesh = ax2.pcolormesh(lons, lats, elev_land, cmap=terrain_cmap, norm=norm, shading='auto', zorder=2)

# Drainage river lines
lc = LineCollection(river_lines, colors='#0284c7', linewidths=1.05, alpha=0.85, zorder=3)
ax2.add_collection(lc)

# Basin Boundaries
gdf_abhs.boundary.plot(ax=ax2, color='#1e3a8a', linewidth=1.6, linestyle='-', zorder=4)
gdf_bouregreg.boundary.plot(ax=ax2, color='#991b1b', linewidth=1.8, linestyle='-', zorder=5)

# Hydrometric Stations:
# Daily stations: red circles (all daily stations plotted as uniform, clean symbols)
ax2.scatter(daily_st['lon_obs'], daily_st['lat_obs'],
            s=65, c='#dc2626', marker='o', edgecolors='black', linewidth=1.1,
            zorder=7)

# Monthly stations: blue triangles (all monthly stations plotted as uniform symbols)
ax2.scatter(monthly_st['lon_obs'], monthly_st['lat_obs'],
            s=65, c='#2563eb', marker='^', edgecolors='black', linewidth=1.1,
            zorder=7)

# Only label the two independent benchmark daily stations: Lalla Chafia and Sidi Jabeur
# Lalla Chafia
ax2.annotate('Lalla Chafia', xy=(-6.38, 33.70), xytext=(-6.00, 33.90),
             arrowprops=dict(arrowstyle="->", color='#991b1b', lw=0.9),
             fontsize=8.5, weight='bold', color='#991b1b', zorder=9,
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#991b1b", alpha=0.9))

# Sidi Jabeur
ax2.annotate('Sidi Jabeur', xy=(-6.43, 33.58), xytext=(-6.05, 33.30),
             arrowprops=dict(arrowstyle="->", color='#991b1b', lw=0.9),
             fontsize=8.5, weight='bold', color='#991b1b', zorder=9,
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#991b1b", alpha=0.9))

# Panel B bounds and styling
ax2.set_xlim([-10.0, -1.0])
ax2.set_ylim([30.0, 36.0])
ax2.set_xlabel('Longitude (°W)')
ax2.set_ylabel('Latitude (°N)')
ax2.set_title('(b) Noah-MP Domain Topography & Gauge Network', weight='bold', loc='left', pad=8)
ax2.grid(True, linestyle=':', color='#cbd5e1', alpha=0.7)

# Panel B Legend: Clean, simplified, without verbose formulations
legend_b = [
    Line2D([0], [0], color='#991b1b', lw=1.8, label='Bouregreg hydrologic watershed'),
    Line2D([0], [0], color='#1e3a8a', lw=1.6, label='Sebou region (ABHS boundary)'),
    Line2D([0], [0], color='#0284c7', lw=1.2, label='River network (da ≥ 1000 km²)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#dc2626', markeredgecolor='k', markersize=8, label='Daily gauge'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#2563eb', markeredgecolor='k', markersize=8, label='Monthly gauge')
]
ax2.legend(handles=legend_b, loc='lower right', framealpha=0.95, edgecolor='#cbd5e1', fontsize=8.2, labelspacing=0.4, handletextpad=0.6)

# Colorbar for Elevation
cax = fig.add_axes([0.925, 0.14, 0.016, 0.72])
cbar = fig.colorbar(mesh, cax=cax, orientation='vertical')
cbar.set_label('Noah-MP Surface Elevation (m a.s.l.)', fontsize=9.5)
cbar.ax.tick_params(labelsize=8.5)

# Save figures
print(f"7. Saving high-resolution PNG to {output_png}...")
plt.savefig(output_png, dpi=300, bbox_inches='tight')

print(f"8. Saving vector PDF to {output_pdf}...")
plt.savefig(output_pdf, bbox_inches='tight')

print("Cartographic generation completed successfully without warnings!")
