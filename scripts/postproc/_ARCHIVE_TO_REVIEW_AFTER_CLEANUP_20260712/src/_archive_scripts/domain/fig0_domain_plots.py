# Author: M. EL Aabaribaoune (@um6p)

"""
===============================================================================
Script: fig0_domain_plots.py
Author: M. El Aabaribaoune (@um6p)

Objective: Generate comprehensive domain context and spatial feature figures.

Description:
    This script is the main entry point for producing study domain maps for the 
    NorthMor basin experiments. It generates geospatial plots including:
    - Dominant Land Cover Types (MODIS IGBP)
    - Dominant Soil Texture Classes (STATSGOFAO)
    - Topography & Elevation (SRTM 30m)
    - Hydrological Basins & In-Situ Stations Overlay
    - SMAP L3 Soil Moisture Observations context
    - MERRA-2 Air Temperature forcing snapshot

Dependencies:
    numpy, netCDF4, h5py, matplotlib, cartopy, geopandas
===============================================================================
"""

import os
import glob
import h5py
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as path_effects
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# -----------------
# 1. SETUP PATHS & CONFIG
# -----------------
import config_postproc as cfg

os.makedirs(cfg.DIR_FIGURES, exist_ok=True)
ldt_nc_path = cfg.LDT_FILE
smap_h5_path = "input/RS_DATA/SMAP/SPL3SMP.009/2020.06.01/SMAP_L3_SM_P_20200601.h5"
merra_nc_path = "input/MET_FORCING/MERRA2/M2T1NXSLV/MERRA2_400.tavg1_2d_slv_Nx.20200604.nc4"

# Load LDT domain details
ds_ldt = nc.Dataset(ldt_nc_path, "r")
lats_ldt = ds_ldt.variables["lat"][:]
lons_ldt = ds_ldt.variables["lon"][:]
elevation = ds_ldt.variables["ELEVATION"][:]
landmask = ds_ldt.variables["LANDMASK"][:]

# Lat/Lon bounding box for Morocco domain
lat_min, lat_max = cfg.DOMAIN_LAT_MIN, cfg.DOMAIN_LAT_MAX
lon_min, lon_max = cfg.DOMAIN_LON_MIN, cfg.DOMAIN_LON_MAX

# Reference cities with coordinates
cities = {
    "Fes": (-5.0003, 34.0331),
    "Meknes": (-5.5403, 33.8965),
    "Taza": (-4.0100, 34.2200),
    "Rabat": (-6.8333, 34.0167)
}

def add_geospatial_context(ax, fig):
    """Add country boundaries, coastlines, reference cities, and a Morocco inset map."""
    # Add cartopy features
    ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor='black', linestyle=':', zorder=4)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black', zorder=4)
    ax.add_feature(cfeature.RIVERS, linewidth=0.5, edgecolor='blue', alpha=0.5, zorder=4)
    
    # Plot gridlines with labels
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}
    
    # Plot reference cities to help locate the domain
    for city, coord in cities.items():
        # Only plot cities inside or very close to the boundaries
        if lon_min - 1.5 <= coord[0] <= lon_max + 0.5 and lat_min - 0.5 <= coord[1] <= lat_max + 0.5:
            ax.plot(coord[0], coord[1], 'ro', markersize=6, markeredgecolor='black', markeredgewidth=1.0, zorder=6)
            txt = ax.text(coord[0] + 0.04, coord[1] + 0.02, city, fontsize=10, fontweight='bold', zorder=7)
            # Add a white halo outline to the text for readability over colorful backgrounds
            txt.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

# -----------------

# FIGURE 1: TOPOGRAPHY (ELEVATION)
# -----------------
print("Plotting Topography with geospatial context...")
fig = plt.figure(figsize=(10, 8), dpi=300)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

# Mask elevations outside landmask
elevation_masked = np.where(landmask == 1, elevation, np.nan)
im = ax.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="terrain", shading="auto", zorder=2, transform=ccrs.PlateCarree())
ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())

# Add custom colorbar
cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.03, shrink=0.8)
cbar.set_label("Elevation (m above sea level)", fontsize=11, fontweight='bold')

plt.title("Study Region - Topography & Elevation (Source: SRTM 30m)", fontsize=11, fontweight="bold", pad=15)
add_geospatial_context(ax, fig)
plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "Fig0_c_topography.png"), bbox_inches="tight")
plt.close()
print("Saved Fig0_c_topography.png")


# -----------------
# FIGURE 2: LAND COVER TYPES
# -----------------
print("Plotting Landcover with geospatial context...")
lc_fractions = ds_ldt.variables["LANDCOVER"][:]
dominant_lc = np.argmax(lc_fractions, axis=0) + 1
dominant_lc = np.where(landmask == 1, dominant_lc, np.nan)

modis_labels = {
    1: "Evergreen Needleleaf Forest",
    2: "Evergreen Broadleaf Forest",
    3: "Deciduous Needleleaf Forest",
    4: "Deciduous Broadleaf Forest",
    5: "Mixed Forest",
    6: "Closed Shrublands",
    7: "Open Shrublands",
    8: "Woody Savannas",
    9: "Savannas",
    10: "Grasslands",
    11: "Permanent Wetlands",
    12: "Croplands",
    13: "Urban and Built-up",
    14: "Cropland/Natural Veg. Mosaic",
    15: "Snow and Ice",
    16: "Barren or Sparsely Vegetated",
    17: "Water Bodies"
}

present_classes = sorted([int(x) for x in np.unique(dominant_lc[~np.isnan(dominant_lc)])])
num_classes = len(present_classes)

cmap = plt.cm.get_cmap("tab20", num_classes)
bounds = np.arange(num_classes + 1) - 0.5
norm = mcolors.BoundaryNorm(bounds, num_classes)

lc_mapped = np.zeros_like(dominant_lc) * np.nan
for idx, cls in enumerate(present_classes):
    lc_mapped[dominant_lc == cls] = idx

fig = plt.figure(figsize=(11, 8), dpi=300)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

im = ax.pcolormesh(lons_ldt, lats_ldt, lc_mapped, cmap=cmap, norm=norm, shading="auto", zorder=2, transform=ccrs.PlateCarree())
ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())

# Custom Legend
handles = []
for idx, cls in enumerate(present_classes):
    patch = plt.Rectangle((0,0),1,1, color=cmap(idx), label=f"{cls}: {modis_labels.get(cls, 'Unknown')}")
    handles.append(patch)

ax.legend(handles=handles, bbox_to_anchor=(1.05, 0.9), loc='upper left', borderaxespad=0., fontsize=9)
plt.title("Study Region - Dominant Land Cover Types (Source: MODIS IGBP)", fontsize=11, fontweight="bold", pad=15)
add_geospatial_context(ax, fig)
plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "Fig0_a_landcover.png"), bbox_inches="tight")
plt.close()
print("Saved Fig0_a_landcover.png")


# -----------------
# FIGURE 3: SOIL TEXTURE TYPES
# -----------------
print("Plotting Soil Texture with geospatial context...")
tex_fractions = ds_ldt.variables["TEXTURE"][:]
dominant_tex = np.argmax(tex_fractions, axis=0) + 1
dominant_tex = np.where(landmask == 1, dominant_tex, np.nan)

usda_labels = {
    1: "Sand",
    2: "Loamy Sand",
    3: "Sandy Loam",
    4: "Silt Loam",
    5: "Silt",
    6: "Loam",
    7: "Sandy Clay Loam",
    8: "Silty Clay Loam",
    9: "Clay Loam",
    10: "Sandy Clay",
    11: "Silty Clay",
    12: "Clay",
    13: "Organic Materials",
    14: "Water",
    15: "Bedrock",
    16: "Other/Unknown"
}

present_tex = sorted([int(x) for x in np.unique(dominant_tex[~np.isnan(dominant_tex)])])
num_tex = len(present_tex)

cmap_tex = plt.cm.get_cmap("Accent", num_tex)
bounds_tex = np.arange(num_tex + 1) - 0.5
norm_tex = mcolors.BoundaryNorm(bounds_tex, num_tex)

tex_mapped = np.zeros_like(dominant_tex) * np.nan
for idx, cls in enumerate(present_tex):
    tex_mapped[dominant_tex == cls] = idx

fig = plt.figure(figsize=(11, 8), dpi=300)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

im = ax.pcolormesh(lons_ldt, lats_ldt, tex_mapped, cmap=cmap_tex, norm=norm_tex, shading="auto", zorder=2, transform=ccrs.PlateCarree())
ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())

# Custom Legend
handles_tex = []
for idx, cls in enumerate(present_tex):
    patch = plt.Rectangle((0,0),1,1, color=cmap_tex(idx), label=f"{cls}: {usda_labels.get(cls, 'Unknown')}")
    handles_tex.append(patch)

ax.legend(handles=handles_tex, bbox_to_anchor=(1.05, 0.9), loc='upper left', borderaxespad=0., fontsize=9)
plt.title("Study Region - Dominant Soil Texture Classes (Source: STATSGOFAO)", fontsize=11, fontweight="bold", pad=15)
add_geospatial_context(ax, fig)
plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "Fig0_b_soil_texture.png"), bbox_inches="tight")
plt.close()
print("Saved Fig0_b_soil_texture.png")


# -----------------
# FIGURE 4: SMAP SOIL MOISTURE OBSERVATIONS
# -----------------
print("Plotting SMAP Observations with geospatial context...")
try:
    with h5py.File(smap_h5_path, "r") as f:
        smap_lats = f["Soil_Moisture_Retrieval_Data_AM/latitude"][:]
        smap_lons = f["Soil_Moisture_Retrieval_Data_AM/longitude"][:]
        smap_sm = f["Soil_Moisture_Retrieval_Data_AM/soil_moisture"][:]
        
        smap_mask = (smap_lats >= lat_min) & (smap_lats <= lat_max) & \
                    (smap_lons >= lon_min) & (smap_lons <= lon_max) & \
                    (smap_sm > 0)
        
        val_lats = smap_lats[smap_mask]
        val_lons = smap_lons[smap_mask]
        val_sm = smap_sm[smap_mask]

    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    # Plot masked topography as background in clean greyscale
    im_bg = ax.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="gist_earth", alpha=0.35, shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())
    
    # Overlay SMAP observations as colored circles
    sc = ax.scatter(val_lons, val_lats, c=val_sm, cmap="YlGnBu", s=250, edgecolor='black', alpha=0.9, zorder=5, transform=ccrs.PlateCarree())
    cbar = plt.colorbar(sc, ax=ax, orientation='vertical', pad=0.03, shrink=0.8)
    cbar.set_label("SMAP Soil Moisture (m³/m³)", fontsize=11, fontweight='bold')
    
    plt.title("SMAP L3 Soil Moisture Observations - June 1, 2020", fontsize=13, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "smap_observation.png"), bbox_inches="tight")
    plt.close()
    print("Saved smap_observation.png")
except Exception as e:
    print("Error plotting SMAP observations:", e)


# -----------------
# FIGURE 5: MERRA-2 TEMPERATURE SNAPSHOT
# -----------------
print("Plotting MERRA-2 Forcing Snapshot with geospatial context...")
try:
    ds_merra = nc.Dataset(merra_nc_path, "r")
    m_lats = ds_merra.variables["lat"][:]
    m_lons = ds_merra.variables["lon"][:]
    m_t2m = ds_merra.variables["T2M"][:]  # Hourly data shape (24, 361, 576)
    
    lat_indices = np.where((m_lats >= lat_min - 0.5) & (m_lats <= lat_max + 0.5))[0]
    lon_indices = np.where((m_lons >= lon_min - 0.5) & (m_lons <= lon_max + 0.5))[0]
    
    cropped_lats = m_lats[lat_indices]
    cropped_lons = m_lons[lon_indices]
    
    # Take hour index 14 (2:00 PM) snapshot and convert from K to C
    t2m_snap = m_t2m[14, lat_indices, :][:, lon_indices] - 273.15
    lon_mesh, lat_mesh = np.meshgrid(cropped_lons, cropped_lats)
    
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    im = ax.pcolormesh(lon_mesh, lat_mesh, t2m_snap, cmap="coolwarm", shading="auto", zorder=2, transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.03, shrink=0.8)
    cbar.set_label("Air Temperature at 2m (°C)", fontsize=11, fontweight='bold')
    
    # Overlay model boundary outline
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=1.2, linestyles='--', zorder=3, transform=ccrs.PlateCarree())
    
    plt.title("MERRA-2 Forcing: Air Temperature Snapshot (June 4, 2020 14:00 UTC)", fontsize=13, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "merra2_temperature.png"), bbox_inches="tight")
    plt.close()
    print("Saved merra2_temperature.png")
except Exception as e:
    print("Error plotting MERRA-2 temperature:", e)

# -----------------
# FIGURE 6: BASIN LIMITS & IN-SITU STATIONS
# -----------------
print("Plotting Hydrological Basins & In-Situ Stations...")
try:
    import geopandas as gpd
    import matplotlib.lines as mlines
    
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    # Plot masked topography as background in clean greyscale
    im_bg = ax.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="Greys", alpha=0.6, shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.5, zorder=3, transform=ccrs.PlateCarree())
    
    # Plot Basin Limits
    basin_dir = os.path.join(cfg.PROJECT_ROOT, "domain", "NorthMor", "Basins_limits")
    basin_files = glob.glob(os.path.join(basin_dir, "*.shp"))
    
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
    handles = []
    for i, b_file in enumerate(basin_files):
        try:
            gdf = gpd.read_file(b_file)
            if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")
            gdf.plot(ax=ax, facecolor='none', edgecolor=colors[i % len(colors)], linewidth=2.0, zorder=5)
            handles.append(mlines.Line2D([], [], color=colors[i % len(colors)], linewidth=2, label=os.path.basename(b_file).replace('.shp','')))
        except Exception as e:
            print(f"Failed to plot basin {b_file}: {e}")
            
    # Plot In-Situ Stations
    station_dir = os.path.join(cfg.PROJECT_ROOT, "domain", "NorthMor", "ABH_data")
    station_files = glob.glob(os.path.join(station_dir, "Stations_hydro_*.shp"))
    
    for s_file in station_files:
        try:
            gdf_s = gpd.read_file(s_file)
            if gdf_s.crs is None or gdf_s.crs.to_string() != "EPSG:4326":
                gdf_s = gdf_s.to_crs("EPSG:4326")
            gdf_s.plot(ax=ax, marker='^', color='darkblue', markersize=60, edgecolor='white', linewidth=0.8, zorder=6)
        except Exception as e:
            print(f"Failed to plot station {s_file}: {e}")

    handles.append(mlines.Line2D([], [], color='white', marker='^', markerfacecolor='darkblue', markersize=10, label='In-Situ Stations'))
    
    ax.legend(handles=handles, loc='upper right', fontsize=9, title="Map Legend")

    plt.title("Study Region - Hydrological Basins & In-Situ Stations", fontsize=11, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    plt.savefig(os.path.join(cfg.DIR_FIGURES_DOMAIN, "Fig0_d_basins_and_insitudata.png"), bbox_inches="tight")
    plt.close()
    print("Saved Fig0_d_basins_and_insitudata.png")

except ImportError:
    print("geopandas is not installed. Skipping Basin Limits & Stations plot.")
except Exception as e:
    print("Error plotting Basins & Stations:", e)

print("All geospatial plots generated successfully!")
ds_ldt.close()
