#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)
#
# Plot domain parameters (Topography, Landcover, Soil Texture) for the Sebou Basin experiment

import os
import sys
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm


# Paths
INPUT_NC = "data/lis_input/lis_input.d01_sebou.nc"
OUT_DIR = "postproc/figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Define IGBP MODIS Landcover classes (1 to 17)
IGBP_NAMES = {
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
    14: "Cropland/Nat. Veg. Mosaic",
    15: "Snow and Ice",
    16: "Barren / Sparsely Veg.",
    17: "Water Bodies"
}

# Define USDA STATSGO Soil Texture classes (1 to 16)
STATSGO_NAMES = {
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
    16: "Other"
}

def load_data():
    if not os.path.exists(INPUT_NC):
        raise FileNotFoundError(f"LDT parameter file not found: {INPUT_NC}")
        
    ds = nc.Dataset(INPUT_NC)
    lat = ds.variables["lat"][:]
    lon = ds.variables["lon"][:]
    landmask = ds.variables["LANDMASK"][:]
    elevation = ds.variables["ELEVATION"][:]
    landcover = ds.variables["LANDCOVER"][:]
    soil_texture = ds.variables["TEXTURE"][:]
    ds.close()
    
    # Convert tiled fractional parameters to dominant class index (1-based index)
    landcover_dominant = np.argmax(landcover, axis=0) + 1
    soil_texture_dominant = np.argmax(soil_texture, axis=0) + 1
    
    # Mask out-of-domain / water points for clear visualization
    elevation_masked = np.ma.masked_where(landmask == 0, elevation)
    landcover_masked = np.ma.masked_where(landmask == 0, landcover_dominant)
    soil_texture_masked = np.ma.masked_where(landmask == 0, soil_texture_dominant)
    
    return lat, lon, landmask, elevation_masked, landcover_masked, soil_texture_masked

def plot_topography(lat, lon, elevation):
    print("Plotting topography map...")
    plt.figure(figsize=(10, 8), dpi=300)
    plt.style.use('seaborn-whitegrid')
    
    # Plot using terrain colormap
    im = plt.pcolormesh(lon, lat, elevation, cmap="terrain", shading="auto")
    cb = plt.colorbar(im, fraction=0.035, pad=0.04)
    cb.set_label("Elevation (meters above sea level)", fontsize=12, fontweight='bold', labelpad=10)
    cb.ax.tick_params(labelsize=10)
    
    plt.title("Sebou Basin - Topography (Digital Elevation Model)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Longitude (°E)", fontsize=11, labelpad=8)
    plt.ylabel("Latitude (°N)", fontsize=11, labelpad=8)
    plt.tick_params(labelsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    
    out_path = os.path.join(OUT_DIR, "sebou_topography.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

def plot_landcover(lat, lon, landcover):
    print("Plotting landcover map...")
    # Find unique values present in the domain
    unique_vals = np.unique(landcover.compressed()).astype(int)
    unique_vals = [v for v in unique_vals if v in IGBP_NAMES]
    
    num_classes = len(unique_vals)
    if num_classes == 0:
        print("[WARN] No valid landcover classes found.")
        return
        
    # Set up discrete colormap
    colors = plt.cm.tab20(np.linspace(0, 1, num_classes))
    cmap = ListedColormap(colors)
    bounds = np.append(unique_vals, unique_vals[-1] + 1)
    norm = BoundaryNorm(bounds, cmap.N)
    
    plt.figure(figsize=(12, 8), dpi=300)
    plt.style.use('seaborn-whitegrid')
    
    im = plt.pcolormesh(lon, lat, landcover, cmap=cmap, norm=norm, shading="auto")
    
    # Custom colorbar with discrete class labels
    cb = plt.colorbar(im, fraction=0.035, pad=0.04, ticks=[v + 0.5 for v in unique_vals])
    cb.ax.set_yticklabels([IGBP_NAMES[v] for v in unique_vals], fontsize=10)
    cb.set_label("MODIS IGBP Land Cover Classes", fontsize=12, fontweight='bold', labelpad=10)
    
    plt.title("Sebou Basin - Land Use and Land Cover", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Longitude (°E)", fontsize=11, labelpad=8)
    plt.ylabel("Latitude (°N)", fontsize=11, labelpad=8)
    plt.tick_params(labelsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    
    out_path = os.path.join(OUT_DIR, "sebou_landcover.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

def plot_soil_texture(lat, lon, soil_texture):
    print("Plotting soil texture map...")
    # Find unique values present in the domain
    unique_vals = np.unique(soil_texture.compressed()).astype(int)
    unique_vals = [v for v in unique_vals if v in STATSGO_NAMES]
    
    num_classes = len(unique_vals)
    if num_classes == 0:
        print("[WARN] No valid soil texture classes found.")
        return
        
    # Set up discrete colormap
    colors = plt.cm.Accent(np.linspace(0, 1, num_classes))
    cmap = ListedColormap(colors)
    bounds = np.append(unique_vals, unique_vals[-1] + 1)
    norm = BoundaryNorm(bounds, cmap.N)
    
    plt.figure(figsize=(12, 8), dpi=300)
    plt.style.use('seaborn-whitegrid')
    
    im = plt.pcolormesh(lon, lat, soil_texture, cmap=cmap, norm=norm, shading="auto")
    
    # Custom colorbar with discrete class labels
    cb = plt.colorbar(im, fraction=0.035, pad=0.04, ticks=[v + 0.5 for v in unique_vals])
    cb.ax.set_yticklabels([STATSGO_NAMES[v] for v in unique_vals], fontsize=10)
    cb.set_label("STATSGO-FAO Soil Texture Classes", fontsize=12, fontweight='bold', labelpad=10)
    
    plt.title("Sebou Basin - Soil Texture Map", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Longitude (°E)", fontsize=11, labelpad=8)
    plt.ylabel("Latitude (°N)", fontsize=11, labelpad=8)
    plt.tick_params(labelsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    
    out_path = os.path.join(OUT_DIR, "sebou_soil_texture.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    try:
        lat, lon, landmask, elevation, landcover, soil_texture = load_data()
        
        plot_topography(lat, lon, elevation)
        plot_landcover(lat, lon, landcover)
        plot_soil_texture(lat, lon, soil_texture)
        
        print("\nDomain parameter visualization complete! Figures are saved in postproc/figures/")
    except Exception as e:
        print(f"Error plotting domain parameters: {e}", file=sys.stderr)
