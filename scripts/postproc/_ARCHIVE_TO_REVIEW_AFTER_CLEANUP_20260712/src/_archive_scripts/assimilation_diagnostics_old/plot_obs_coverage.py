# Author: M. EL Aabaribaoune (@um6p)

import os
import glob
import netCDF4 as nc
import calendar
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.masking import get_lat_lon

def plot_smap_obs_coverage(data_dict, out_dir):
    """
    Génère 3 figures séparées de niveau publication (Q1) illustrant :
    1. Le nombre total d'observations assimilées par pixel.
    2. La fréquence moyenne d'assimilation (obs/jour).
    3. Le volume mensuel total d'observations assimilées sur le domaine.
    """
    print("Generating SMAP observation coverage figures...")
    files_cdf = data_dict.get('files_da_nocdf', [])
    if not files_cdf:
        print("No DA files found.")
        return None
        
    lat, lon = get_lat_lon(files_cdf)
    if lat is None: return None
    
    base_dir_da = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(files_cdf[0]))))
    
    grid_shape = (len(lat), len(lon))
    ninnov_sum = np.zeros(grid_shape)
    
    monthly_counts = {}
    
    curr_date = data_dict['start_date']
    end_date = data_dict['end_date']
    total_days = (end_date - curr_date).days + 1
    
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        innov_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
        
        monthly_count = 0
        
        for f in innov_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'ninnov_01' in ds.variables:
                    n = ds.variables['ninnov_01'][:]
                    
                    if np.ma.is_masked(n):
                        n = n.filled(0)
                        
                    valid_n = np.where(n > 0, n, 0)
                    ninnov_sum += valid_n
                    monthly_count += np.sum(valid_n)
                ds.close()
            except:
                pass
                
        month_label = curr_date.strftime("%b") # Ex: Jan, Feb
        if month_label not in monthly_counts:
            monthly_counts[month_label] = 0
        monthly_counts[month_label] += monthly_count
        
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    sum_ninnov = np.where(ninnov_sum > 0, ninnov_sum, np.nan)
    freq = np.where(ninnov_sum > 0, ninnov_sum / total_days, np.nan)
    
    start_str = data_dict['start_date'].strftime('%b')
    end_str = data_dict['end_date'].strftime('%b %Y')
    period_str = f"{start_str}–{end_str}"
    
    os.makedirs(out_dir, exist_ok=True)
    
    def add_map_features(ax):
        ax.coastlines(linewidth=0.5, color='black')
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':', color='black')
        ax.set_facecolor('#f0f0f0') # gris clair pour zones sans données
        
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        return gl
    
    # ==============================================================
    # Figure 1: Total assimilated observations
    # ==============================================================
    fig1 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax1 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax1)
    
    ax1.set_title(f"Total assimilated SMAP observations ({period_str})", fontsize=14, fontweight='bold', pad=15)
    
    levels1 = [0, 5, 10, 20, 30, 40, 50, 60, 70]
    cmap1 = plt.get_cmap('YlGnBu').copy()
    cmap1.set_bad('#f0f0f0')
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, sum_ninnov, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation='vertical', shrink=0.8, pad=0.03)
    cbar1.set_label("Assimilated observations count", fontsize=11)
    cbar1.ax.tick_params(labelsize=10)
    
    f1_png = os.path.join(out_dir, "Fig1_total_assimilated_obs_map.png")
    fig1.savefig(f1_png, dpi=300)
    plt.close(fig1)
    
    # ==============================================================
    # Figure 2: Assimilation frequency
    # ==============================================================
    fig2 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax2)
    
    ax2.set_title(f"Assimilation frequency of SMAP observations (obs day⁻¹, {period_str})", fontsize=14, fontweight='bold', pad=15)
    
    levels2 = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    cmap2 = plt.get_cmap('plasma').copy()
    cmap2.set_bad('#f0f0f0')
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap2.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, freq, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    cbar2 = fig2.colorbar(pcm2, ax=ax2, orientation='vertical', shrink=0.8, pad=0.03)
    cbar2.set_label("Assimilation frequency (obs day⁻¹)", fontsize=11)
    cbar2.ax.tick_params(labelsize=10)
    
    f2_png = os.path.join(out_dir, "Fig2_assimilation_frequency_map.png")
    fig2.savefig(f2_png, dpi=300)
    plt.close(fig2)
    
    # ==============================================================
    # Figure 3: Monthly total
    # ==============================================================
    fig3, ax3 = plt.subplots(figsize=(8, 6), constrained_layout=True)
    
    months = list(monthly_counts.keys())
    counts = [monthly_counts[m] for m in months]
    
    bars = ax3.bar(months, counts, color='#4575b4', edgecolor='black', zorder=3)
    
    ax3.set_title("Monthly total assimilated SMAP observations", fontsize=14, fontweight='bold', pad=15)
    ax3.set_ylabel("Total assimilated observations", fontsize=11)
    ax3.tick_params(axis='both', labelsize=10)
    
    # Grid and spines
    ax3.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax3.annotate(f'{int(height)}',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),  # 3 points vertical offset
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=9)
    
    f3_png = os.path.join(out_dir, "Fig3_monthly_total_assimilated_obs.png")
    fig3.savefig(f3_png, dpi=300)
    plt.close(fig3)
    
    return [f1_png, f2_png, f3_png]
