"""
===============================================================================
Script: core.py
Author: M. El Aabaribaoune (@um6p)

Objective: Core processing and visualization engine for OPL vs DA evaluation.

Description:
    This module contains the heavy-lifting functions required to load, 
    process, and plot the NetCDF data. It parses the specific configurations 
    for each variable (such as multipliers, colormaps, and layer indices), 
    computes the required spatial statistics (Min/Max/Mean), and generates 
    the 1x3 Cartesian grid maps (Open Loop, Data Assimilation, and Difference).

Dependencies:
    os, numpy, matplotlib, cartopy, utils
===============================================================================
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from utils import load_variable, setup_map_axis

def fetch_data(config, var_key, season):
    var_conf = config['variables'][var_key]
    layer_index = var_conf.get('layer_index')
    multiplier = var_conf.get('multiplier', 1.0)
    
    if var_conf.get('is_composite', False):
        # Composite variable (e.g. Total Runoff = Qs + Qsb)
        ol_total, da_total, lat, lon = None, None, None, None
        for comp in var_conf['components']:
            ol, lat, lon = load_variable(config['paths']['dir_output_ol'], comp, layer_index, multiplier, season)
            da, _, _ = load_variable(config['paths']['dir_output_da'], comp, layer_index, multiplier, season)
            if ol is not None:
                ol_total = ol if ol_total is None else ol_total + ol
            if da is not None:
                da_total = da if da_total is None else da_total + da
        return ol_total, da_total, lat, lon
    else:
        # Standard variable
        ol, lat, lon = load_variable(config['paths']['dir_output_ol'], var_key, layer_index, multiplier, season)
        da, _, _ = load_variable(config['paths']['dir_output_da'], var_key, layer_index, multiplier, season)
        return ol, da, lat, lon

def plot_variable(config, var_key, season):
    var_conf = config['variables'][var_key]
    print(f"Processing: {var_conf['title_name']} ({season})")
    
    ol_data, da_data, lat, lon = fetch_data(config, var_key, season)
    
    if ol_data is None:
        print(f"Skipping {var_key}: Missing OL data.")
        return
        
    diff_data = da_data - ol_data if da_data is not None else None
    
    num_cols = 3 if da_data is not None else 1
    fig = plt.figure(figsize=(6 * num_cols, 5.5))
    
    vmin, vmax = var_conf['vmin'], var_conf['vmax']
    diff_vmax = var_conf['diff_vmax']
    
    if num_cols == 3:
        axes = [fig.add_subplot(1, 3, i+1, projection=ccrs.PlateCarree()) for i in range(3)]
        titles = ["(a) Open Loop (OL)", "(b) Data Assimilation (DA)", "(c) Difference (DA - OL)"]
        data_list = [ol_data, da_data, diff_data]
        cmaps = [var_conf['cmap'], var_conf['cmap'], var_conf['diff_cmap']]
        vmins = [vmin, vmin, -diff_vmax]
        vmaxs = [vmax, vmax, diff_vmax]
    else:
        axes = [fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())]
        titles = ["(a) Open Loop (OL)"]
        data_list = [ol_data]
        cmaps = [var_conf['cmap']]
        vmins = [vmin]
        vmaxs = [vmax]
        
    for ax, title, data, cmap_name, val_min, val_max in zip(axes, titles, data_list, cmaps, vmins, vmaxs):
        setup_map_axis(ax, config['domain']['lon_min'], config['domain']['lon_max'],
                       config['domain']['lat_min'], config['domain']['lat_max'])
                       
        # Mask invalid/negative data slightly below zero
        data_plot = np.ma.masked_where(data < -999, data)
        
        pcm = ax.pcolormesh(lon, lat, data_plot, cmap=cmap_name, 
                            vmin=val_min, vmax=val_max, transform=ccrs.PlateCarree())
        
        cbar = plt.colorbar(pcm, ax=ax, orientation='horizontal', pad=0.08, fraction=0.046)
        label_unit = var_conf['unit']
        cbar.set_label(f"{var_conf['title_name']} ({label_unit})" if "Difference" not in title else f"$\Delta$ {var_conf['title_name']} ({label_unit})")
        
        # Stats
        d_min = np.nanmin(data_plot)
        d_max = np.nanmax(data_plot)
        d_mean = np.nanmean(data_plot)
        full_title = f"{title}\nMin: {d_min:.3f} | Max: {d_max:.3f} | Mean: {d_mean:.3f}"
        
        ax.set_title(full_title, fontsize=12, fontweight='bold')

    period_str = "Jan - Dec 2016" if season == 'all-period' else season
    fig.suptitle(f"Spatial Distribution of {var_conf['title_name']}\nOpen Loop vs. Data Assimilation | North Morocco Basin ({period_str})", 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    out_dir = config['paths']['dir_figures']
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{var_key}_{season}.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Saved: {out_file}")
