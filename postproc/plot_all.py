import os
import glob
import h5py
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# -----------------
# 1. SETUP PATHS
# -----------------
os.makedirs("postproc", exist_ok=True)
ldt_nc_path = "lis_input.d01.nc"
smap_h5_path = "input/RS_DATA/SMAP/SPL3SMP.009/2020.06.01/SMAP_L3_SM_P_20200601.h5"
merra_nc_path = "input/MET_FORCING/MERRA2/M2T1NXSLV/MERRA2_400.tavg1_2d_slv_Nx.20200604.nc4"

# Load LDT domain details
ds_ldt = nc.Dataset(ldt_nc_path, "r")
lats_ldt = ds_ldt.variables["lat"][:]
lons_ldt = ds_ldt.variables["lon"][:]
elevation = ds_ldt.variables["ELEVATION"][:]
landmask = ds_ldt.variables["LANDMASK"][:]

# Lat/Lon bounding box for Morocco domain
lat_min, lat_max = 33.0, 34.5
lon_min, lon_max = -5.5, -3.5

# -----------------
# FIGURE 1: TOPOGRAPHY (ELEVATION)
# -----------------
print("Plotting Topography...")
plt.figure(figsize=(10, 8), dpi=300)
# Mask elevations outside landmask to show clean basin shape
elevation_masked = np.where(landmask == 1, elevation, np.nan)
im = plt.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="terrain", shading="auto")
# Draw a clean border line around the landmask
plt.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8)

plt.colorbar(im, label="Elevation (m above sea level)")
plt.xlabel("Longitude (°E)", fontsize=12)
plt.ylabel("Latitude (°N)", fontsize=12)
plt.title("Morocco Domain - Topography & Elevation (Noah-MP Grid)", fontsize=14, fontweight="bold", pad=15)
plt.xlim(lon_min, lon_max)
plt.ylim(lat_min, lat_max)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("postproc/basin_topography.png", bbox_inches="tight")
plt.close()
print("Saved basin_topography.png")

# -----------------
# FIGURE 2: LAND COVER TYPES
# -----------------
print("Plotting Landcover...")
lc_fractions = ds_ldt.variables["LANDCOVER"][:]
dominant_lc = np.argmax(lc_fractions, axis=0) + 1  # 1-indexed for classes
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

plt.figure(figsize=(11, 8), dpi=300)
im = plt.pcolormesh(lons_ldt, lats_ldt, lc_mapped, cmap=cmap, norm=norm, shading="auto")
plt.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8)

handles = []
for idx, cls in enumerate(present_classes):
    patch = plt.Rectangle((0,0),1,1, color=cmap(idx), label=f"{cls}: {modis_labels.get(cls, 'Unknown')}")
    handles.append(patch)

plt.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=10)
plt.xlabel("Longitude (°E)", fontsize=12)
plt.ylabel("Latitude (°N)", fontsize=12)
plt.title("Morocco Domain - Dominant Land Cover Types (MODIS)", fontsize=14, fontweight="bold", pad=15)
plt.xlim(lon_min, lon_max)
plt.ylim(lat_min, lat_max)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("postproc/basin_landcover.png", bbox_inches="tight")
plt.close()
print("Saved basin_landcover.png")

# -----------------
# FIGURE 3: SOIL TEXTURE TYPES
# -----------------
print("Plotting Soil Texture...")
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

plt.figure(figsize=(11, 8), dpi=300)
im = plt.pcolormesh(lons_ldt, lats_ldt, tex_mapped, cmap=cmap_tex, norm=norm_tex, shading="auto")
plt.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8)

handles_tex = []
for idx, cls in enumerate(present_tex):
    patch = plt.Rectangle((0,0),1,1, color=cmap_tex(idx), label=f"{cls}: {usda_labels.get(cls, 'Unknown')}")
    handles_tex.append(patch)

plt.legend(handles=handles_tex, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=10)
plt.xlabel("Longitude (°E)", fontsize=12)
plt.ylabel("Latitude (°N)", fontsize=12)
plt.title("Morocco Domain - Dominant Soil Texture Classes (STATSGO/STAS)", fontsize=14, fontweight="bold", pad=15)
plt.xlim(lon_min, lon_max)
plt.ylim(lat_min, lat_max)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("postproc/basin_soil_texture.png", bbox_inches="tight")
plt.close()
print("Saved basin_soil_texture.png")

# -----------------
# FIGURE 4: SMAP SOIL MOISTURE OBSERVATIONS
# -----------------
print("Plotting SMAP Observations...")
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

    plt.figure(figsize=(10, 8), dpi=300)
    
    # Plot masked topography as background in greyscale/terrain for clean overlay
    plt.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="gist_earth", alpha=0.4, shading="auto")
    plt.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8)
    
    # Overlay SMAP observations
    sc = plt.scatter(val_lons, val_lats, c=val_sm, cmap="YlGnBu", s=250, edgecolor='black', alpha=0.9, zorder=3)
    plt.colorbar(sc, label="SMAP Soil Moisture (m³/m³)")
    
    plt.xlabel("Longitude (°E)", fontsize=12)
    plt.ylabel("Latitude (°N)", fontsize=12)
    plt.title("SMAP L3 Soil Moisture Observations - June 1, 2020", fontsize=14, fontweight="bold", pad=15)
    plt.xlim(lon_min, lon_max)
    plt.ylim(lat_min, lat_max)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("postproc/smap_observation.png", bbox_inches="tight")
    plt.close()
    print("Saved smap_observation.png")
except Exception as e:
    print("Error plotting SMAP observations:", e)

# -----------------
# FIGURE 5: MERRA-2 TEMPERATURE SNAPSHOT
# -----------------
print("Plotting MERRA-2 Forcing Snapshot...")
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
    
    plt.figure(figsize=(10, 8), dpi=300)
    im = plt.pcolormesh(lon_mesh, lat_mesh, t2m_snap, cmap="coolwarm", shading="auto")
    plt.colorbar(im, label="Air Temperature at 2m (°C)")
    
    # Overlay model boundary outline
    plt.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=1.0, linestyles='--')
    
    plt.xlabel("Longitude (°E)", fontsize=12)
    plt.ylabel("Latitude (°N)", fontsize=12)
    plt.title("MERRA-2 Forcing: Air Temperature Snapshot (June 4, 2020 14:00 UTC)", fontsize=14, fontweight="bold", pad=15)
    plt.xlim(lon_min, lon_max)
    plt.ylim(lat_min, lat_max)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("postproc/merra2_temperature.png", bbox_inches="tight")
    plt.close()
    print("Saved merra2_temperature.png")
except Exception as e:
    print("Error plotting MERRA-2 temperature:", e)

print("All plots generated successfully!")
ds_ldt.close()
