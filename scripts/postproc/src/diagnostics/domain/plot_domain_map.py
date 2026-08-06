# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: domain.plot_domain_map
Description: Geospatial mapping and domain characterization.
================================================================================
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
import geopandas as gpd
import matplotlib.lines as mlines

def plot_all_domain_maps(out_dir, project_root):
    """
    Generates and saves the 4 geospatial domain maps.
    
    Args:
        out_dir (str): Output directory where the maps will be saved.
        project_root (str): Root path of the NoahMP_Morocco project.
        
    Returns:
        list: List of file paths to the generated PNG images.
    """
    # Paths to the input reference files (LDT, SMAP, MERRA2)
    ldt_nc_path = os.path.join(project_root, "data", "lis_input", "lis_input_NorthMor_5km.nc")
    
    smap_h5_path = os.path.join(project_root, "input", "RS_DATA", "SMAP", "SPL3SMP.009", "2020.06.01", "SMAP_L3_SM_P_20200601.h5")
    merra_nc_path = os.path.join(project_root, "input", "MET_FORCING", "MERRA2", "M2T1NXSLV", "MERRA2_400.tavg1_2d_slv_Nx.20200604.nc4")
    
    if not os.path.exists(ldt_nc_path):
        print(f"LDT file not found: {ldt_nc_path}")
        return []

    ds_ldt = nc.Dataset(ldt_nc_path, "r")
    lats_ldt = ds_ldt.variables["lat"][:]
    lons_ldt = ds_ldt.variables["lon"][:]
    elevation = ds_ldt.variables["ELEVATION"][:]
    landmask = ds_ldt.variables["LANDMASK"][:]

    lat_min, lat_max = 30.0, 36.0
    lon_min, lon_max = -10.0, -1.0

    cities = {
        "Fes": (-5.0003, 34.0331),
        "Meknes": (-5.5403, 33.8965),
        "Taza": (-4.0100, 34.2200),
        "Rabat": (-6.8333, 34.0167)
    }

    def add_geospatial_context(ax, fig, discreet_cities=False):
        """
        Adds borders, coastlines, rivers, gridlines (lat/lon), 
        and major city locations to the map context.
        """
        ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor='black', linestyle=':', zorder=4)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black', zorder=4)
        ax.add_feature(cfeature.RIVERS, linewidth=0.5, edgecolor='blue', alpha=0.5, zorder=4)
        
        # Add lat/lon gridlines
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        
        # Loop through cities to overlay them on the map
        for city, coord in cities.items():
            if lon_min - 1.5 <= coord[0] <= lon_max + 0.5 and lat_min - 0.5 <= coord[1] <= lat_max + 0.5:
                if discreet_cities:
                    txt = ax.text(coord[0], coord[1], city, fontsize=9, fontweight='semibold', ha='left', va='bottom', zorder=20)
                else:
                    ax.plot(coord[0], coord[1], 'ro', markersize=6, markeredgecolor='black', markeredgewidth=1.0, zorder=6)
                    txt = ax.text(coord[0] + 0.04, coord[1] + 0.02, city, fontsize=10, fontweight='bold', zorder=7)
                txt.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

    generated = []

    # FIGURE 1: TOPOGRAPHY (ELEVATION)
    print("Plotting Topography...")
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    elevation_masked = np.where(landmask == 1, elevation, np.nan)
    im = ax.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="terrain", shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.03, shrink=0.8)
    cbar.set_label("Elevation (m above sea level)", fontsize=11, fontweight='bold')
    plt.title("Study Region - Topography & Elevation (Source: SRTM 30m)", fontsize=11, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    f_out = os.path.join(out_dir, "Fig0_c_topography.png")
    plt.savefig(f_out, bbox_inches="tight")
    plt.close()
    generated.append(f_out)

    # FIGURE 2: LAND COVER
    print("Plotting Landcover...")
    lc_fractions = ds_ldt.variables["LANDCOVER"][:]
    dominant_lc = np.argmax(lc_fractions, axis=0) + 1
    dominant_lc = np.where(landmask == 1, dominant_lc, np.nan)
    modis_labels = {1: "Evergreen Needleleaf Forest", 2: "Evergreen Broadleaf Forest", 3: "Deciduous Needleleaf Forest", 4: "Deciduous Broadleaf Forest", 5: "Mixed Forest", 6: "Closed Shrublands", 7: "Open Shrublands", 8: "Woody Savannas", 9: "Savannas", 10: "Grasslands", 11: "Permanent Wetlands", 12: "Croplands", 13: "Urban and Built-up", 14: "Cropland/Natural Veg. Mosaic", 15: "Snow and Ice", 16: "Barren or Sparsely Vegetated", 17: "Water Bodies"}
    present_classes = sorted([int(x) for x in np.unique(dominant_lc[~np.isnan(dominant_lc)])])
    num_classes = len(present_classes)
    cmap = plt.colormaps.get_cmap("tab20").resampled(num_classes)
    bounds = np.arange(num_classes + 1) - 0.5
    norm = mcolors.BoundaryNorm(bounds, num_classes)
    lc_mapped = np.zeros_like(dominant_lc) * np.nan
    for idx, cls in enumerate(present_classes): lc_mapped[dominant_lc == cls] = idx
    fig = plt.figure(figsize=(11, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    im = ax.pcolormesh(lons_ldt, lats_ldt, lc_mapped, cmap=cmap, norm=norm, shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())
    handles = [plt.Rectangle((0,0),1,1, color=cmap(idx), label=f"{cls}: {modis_labels.get(cls, 'Unknown')}") for idx, cls in enumerate(present_classes)]
    ax.legend(handles=handles, bbox_to_anchor=(1.05, 0.9), loc='upper left', borderaxespad=0., fontsize=9)
    plt.title("Study Region - Dominant Land Cover Types (Source: MODIS IGBP)", fontsize=11, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    f_out = os.path.join(out_dir, "Fig0_a_landcover.png")
    plt.savefig(f_out, bbox_inches="tight")
    plt.close()
    generated.append(f_out)

    # FIGURE 3: SOIL TEXTURE
    print("Plotting Soil Texture...")
    tex_fractions = ds_ldt.variables["TEXTURE"][:]
    dominant_tex = np.argmax(tex_fractions, axis=0) + 1
    dominant_tex = np.where(landmask == 1, dominant_tex, np.nan)
    usda_labels = {1: "Sand", 2: "Loamy Sand", 3: "Sandy Loam", 4: "Silt Loam", 5: "Silt", 6: "Loam", 7: "Sandy Clay Loam", 8: "Silty Clay Loam", 9: "Clay Loam", 10: "Sandy Clay", 11: "Silty Clay", 12: "Clay", 13: "Organic Materials", 14: "Water", 15: "Bedrock", 16: "Other/Unknown"}
    present_tex = sorted([int(x) for x in np.unique(dominant_tex[~np.isnan(dominant_tex)])])
    num_tex = len(present_tex)
    cmap_tex = plt.colormaps.get_cmap("Accent").resampled(num_tex)
    bounds_tex = np.arange(num_tex + 1) - 0.5
    norm_tex = mcolors.BoundaryNorm(bounds_tex, num_tex)
    tex_mapped = np.zeros_like(dominant_tex) * np.nan
    for idx, cls in enumerate(present_tex): tex_mapped[dominant_tex == cls] = idx
    fig = plt.figure(figsize=(11, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    im = ax.pcolormesh(lons_ldt, lats_ldt, tex_mapped, cmap=cmap_tex, norm=norm_tex, shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.8, zorder=3, transform=ccrs.PlateCarree())
    handles_tex = [plt.Rectangle((0,0),1,1, color=cmap_tex(idx), label=f"{cls}: {usda_labels.get(cls, 'Unknown')}") for idx, cls in enumerate(present_tex)]
    ax.legend(handles=handles_tex, bbox_to_anchor=(1.05, 0.9), loc='upper left', borderaxespad=0., fontsize=9)
    plt.title("Study Region - Dominant Soil Texture Classes (Source: STATSGOFAO)", fontsize=11, fontweight="bold", pad=15)
    add_geospatial_context(ax, fig)
    f_out = os.path.join(out_dir, "Fig0_b_soil_texture.png")
    plt.savefig(f_out, bbox_inches="tight")
    plt.close()
    generated.append(f_out)

    # FIGURE 6: BASIN LIMITS & STATIONS
    print("Plotting Hydrological Basins & In-Situ Stations...")
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    im_bg = ax.pcolormesh(lons_ldt, lats_ldt, elevation_masked, cmap="Greys", alpha=0.4, shading="auto", zorder=2, transform=ccrs.PlateCarree())
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=0.5, zorder=3, transform=ccrs.PlateCarree())
    
    basin_dir = os.path.join(project_root, "domain", "NorthMor", "Basins_limits")
    all_basin_files = glob.glob(os.path.join(basin_dir, "*.shp"))
    
    allowed_basin_layers = {
        "BV_Bouregreg_ExportFeatures.shp",
        "Limite_ABHBC.shp",
        "Limite_ABHOER.shp",
        "Limite_ABHS_Export.shp",
        "Limite_ABHT.shp"
    }
    
    basin_files = [f for f in all_basin_files if os.path.basename(f) in allowed_basin_layers]
    rain_gauge_file = os.path.join(basin_dir, "Postes_pluvio.shp")
    
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
    handles = []
    
    name_map = {
        "BV_Bouregreg_ExportFeatures": "Bouregreg basin",
        "Limite_ABHBC": "ABHBC water agency boundary",
        "Limite_ABHOER": "ABHOER water agency boundary",
        "Limite_ABHS_Export": "ABHS water agency boundary",
        "Limite_ABHT": "ABHT water agency boundary"
    }

    for i, b_file in enumerate(basin_files):
        try:
            gdf = gpd.read_file(b_file)
            if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
            
            b_name = os.path.basename(b_file).replace('.shp','')
            color = colors[i % len(colors)]
            gdf.plot(ax=ax, facecolor='none', edgecolor=color, linewidth=2.0, zorder=5)
            
            legend_label = name_map.get(b_name, b_name)
            handles.append(mlines.Line2D([], [], color=color, linewidth=2, label=legend_label))
            
            rep_pt = gdf.geometry.representative_point().iloc[0]
            lon, lat = rep_pt.x, rep_pt.y
            
            txt = ax.text(lon, lat, legend_label, fontsize=9, fontweight="semibold", ha="center", va="center", color=color, transform=ccrs.PlateCarree(), zorder=20)
            txt.set_path_effects([path_effects.withStroke(linewidth=3, foreground="white")])
            
        except Exception as e: pass

    try:
        gdf_rg = gpd.read_file(rain_gauge_file)
        if gdf_rg.crs is None or gdf_rg.crs.to_string() != "EPSG:4326": gdf_rg = gdf_rg.to_crs("EPSG:4326")
        gdf_rg.plot(ax=ax, facecolor='none', edgecolor='red', marker='o', markersize=20, linewidth=1.5, zorder=6)
        handles.append(mlines.Line2D([0], [0], marker='o', linestyle='None', markerfacecolor='none', markeredgecolor='red', markeredgewidth=1.8, markersize=7, label="Rain gauges"))
    except Exception as e: pass

    show_unclassified_points = False
    station_dir = os.path.join(project_root, "domain", "NorthMor", "ABH_data")
    all_station_files = glob.glob(os.path.join(station_dir, "Stations_hydro_*.shp"))
    
    allowed_station_layers = {
        "Stations_hydro_ABHT.shp",
        "Stations_hydro_ABHBC.shp"
    }
    
    for s_file in all_station_files:
        if not show_unclassified_points and os.path.basename(s_file) not in allowed_station_layers:
            continue
        try:
            gdf_s = gpd.read_file(s_file)
            if gdf_s.crs is None or gdf_s.crs.to_string() != "EPSG:4326": gdf_s = gdf_s.to_crs("EPSG:4326")
            gdf_s.plot(ax=ax, marker='^', color='darkblue', markersize=60, edgecolor='white', linewidth=0.8, zorder=6)
        except Exception as e: pass
        
    handles.append(mlines.Line2D([0], [0], color='white', marker='^', markerfacecolor='darkblue', markersize=10, label='In-situ hydrological stations'))
    
    ax.legend(handles=handles, title="Legend", loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0.0, frameon=True, framealpha=0.95, fontsize=9, title_fontsize=10)
    plt.title("Study Area: Hydrological Basins, Rain Gauges, and In-Situ Stations", fontsize=11, fontweight="bold", pad=15)
    
    add_geospatial_context(ax, fig, discreet_cities=True)
    
    # Check for unauthorized black markers
    for child in ax.get_children():
        if isinstance(child, matplotlib.lines.Line2D):
            marker = child.get_marker()
            if marker not in ['', 'None', None, ' ']:
                c = child.get_color()
                mfc = child.get_markerfacecolor()
                if c in ['k', 'black', '#000000'] or mfc in ['k', 'black', '#000000']:
                    raise ValueError("UNEXPECTED_BLACK_POINT_LAYER:\nAn unexplained black point or diamond layer remains in the study-area map.")
        elif isinstance(child, matplotlib.collections.PathCollection):
            facecolors = child.get_facecolors()
            if facecolors is not None and len(facecolors) > 0:
                for fc in facecolors:
                    if fc[0] < 0.1 and fc[1] < 0.1 and fc[2] < 0.1 and fc[3] > 0.0:
                        raise ValueError("UNEXPECTED_BLACK_POINT_LAYER:\nAn unexplained black point or diamond layer remains in the study-area map.")

    f_out = os.path.join(out_dir, "Fig0_d_basins_and_insitudata.png")
    plt.savefig(f_out, bbox_inches="tight", facecolor="white")
    plt.close()
    generated.append(f_out)

    ds_ldt.close()
    return generated
