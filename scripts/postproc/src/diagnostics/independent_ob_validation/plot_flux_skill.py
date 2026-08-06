#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# -*- coding: utf-8 -*-

"""
Script to plot the spatial changes in flux correlation skill (ΔR and ΔAnomalyR)
analogous to Figure 2 of Nie et al. (2022).
"""

import xarray as xr
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import csv
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

from matplotlib.colors import ListedColormap, BoundaryNorm

def create_nie_colormap():
    """Create a discrete symmetric colormap matching Nie et al. 2022."""
    colors = [
        '#7a00cc',   # deep purple (-0.4 to -0.3)
        '#1f7fff',   # blue (-0.3 to -0.2)
        '#38d6e6',   # cyan (-0.2 to -0.1)
        '#e0f7fa',   # light cyan / neutral (-0.1 to 0.0)
        '#fff3b0',   # pale yellow (0.0 to 0.1)
        '#f7a53a',   # yellow-orange (0.1 to 0.2)
        '#ff6b2d',   # orange (0.2 to 0.3)
        '#ff2a1f'    # red (0.3 to 0.4)
    ]
    cmap = ListedColormap(colors)
    cmap.set_over('#ff2a1f')
    cmap.set_under('#7a00cc')
    
    # 8 colors require 9 boundaries exactly.
    boundaries = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4]
    norm = BoundaryNorm(boundaries, cmap.N, clip=True)
    
    return cmap, norm

def compute_significance_mask(r_da, r_ol, n_samples):
    """
    Fisher's z-transform test to compare two correlations.
    Returns a boolean mask where True means the difference is statistically significant (95%).
    """
    # Clip correlations to avoid log(0)
    r_da_clip = np.clip(r_da, -0.999, 0.999)
    r_ol_clip = np.clip(r_ol, -0.999, 0.999)
    
    z_da = 0.5 * np.log((1 + r_da_clip) / (1 - r_da_clip))
    z_ol = 0.5 * np.log((1 + r_ol_clip) / (1 - r_ol_clip))
    
    # Test statistic Z
    std_err = np.sqrt(2.0 / (n_samples - 3))
    z_stat = (z_da - z_ol) / std_err
    
    # Significant at 95% level (|Z| > 1.96)
    return np.abs(z_stat) > 1.96

def format_map(ax):
    """Apply consistent geographic formatting to a Cartopy axis."""
    ax.set_facecolor('white')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='#333333')
    ax.add_feature(cfeature.BORDERS, linewidth=0.6, linestyle=':', edgecolor='#555555')
    
    # Reduced map extent to focus on land and minimize the Atlantic Ocean
    ax.set_extent([-13.5, -1.0, 27.5, 36.0], crs=ccrs.PlateCarree())
    
    gl = ax.gridlines(draw_labels=False, linewidth=0.4, color='#DADADA', alpha=0.4, linestyle='--')

def plot_flux_skill(exp_da_name, title, datasets, out_prefix, csv_rows):
    """
    datasets: dict of {'Column Name': {'file': path, 'n': months}}
    exp_da_name: 'DA_NoCDF' or 'DA_CDF'
    csv_rows: list to append dictionary of stats for CSV export
    """
    fig, axes = plt.subplots(2, len(datasets), figsize=(5 * len(datasets), 8), 
                             subplot_kw={'projection': ccrs.PlateCarree()})
    fig.patch.set_facecolor('white')
    
    # Handle single column case properly
    if len(datasets) == 1:
        axes = np.expand_dims(axes, axis=1)
        
    cmap, norm = create_nie_colormap()
    
    col_idx = 0
    for col_title, info in datasets.items():
        nc_file = info['file']
        n_months = info['n']
        
        if not nc_file.exists():
            print(f"WARNING: File {nc_file} not found. Skipping column {col_title}.")
            col_idx += 1
            continue
            
        ds = xr.open_dataset(nc_file)
        
        for row_idx, metric in enumerate(['R', 'Anomaly R']):
            ax = axes[row_idx, col_idx]
            format_map(ax)
            
            # Extract maps
            r_da = ds[metric].sel(exp=exp_da_name).values
            r_ol = ds[metric].sel(exp='OPL').values
            
            # Compute difference and significance
            delta_r = r_da - r_ol
            sig_mask = compute_significance_mask(r_da, r_ol, n_months)
            
            delta_r_sig = np.where(sig_mask, delta_r, np.nan)
            
            lon = ds.coords.get('lon', ds.coords.get('longitude')).values
            lat = ds.coords.get('lat', ds.coords.get('latitude')).values
            
            # Plot base land mask for valid pixels (non-significant regions will show this)
            land_mask = np.where(~np.isnan(r_ol), 1, np.nan)
            ax.pcolormesh(lon, lat, land_mask, transform=ccrs.PlateCarree(),
                          cmap=ListedColormap(['#F2F2F2']), shading='auto', zorder=1)
            
            # Calculate un-clipped statistics
            valid_mask = ~np.isnan(r_ol)
            delta_valid = delta_r[valid_mask]
            sig_mask_valid = sig_mask[valid_mask]
            
            n_valid = len(delta_valid)
            n_sig = np.sum(sig_mask_valid)
            
            if n_valid > 0:
                median_delta_all = float(np.nanmedian(delta_valid))
                
                sig_improved_mask = sig_mask_valid & (delta_valid > 0)
                sig_degraded_mask = sig_mask_valid & (delta_valid < 0)
                
                n_sig_imp = np.sum(sig_improved_mask)
                n_sig_deg = np.sum(sig_degraded_mask)
                
                pct_imp = (n_sig_imp / n_valid) * 100.0
                pct_deg = (n_sig_deg / n_valid) * 100.0
                pct_nonsig = 100.0 - pct_imp - pct_deg
                
                median_delta_sig = float(np.nanmedian(delta_valid[sig_mask_valid])) if n_sig > 0 else np.nan
            else:
                median_delta_all = np.nan
                median_delta_sig = np.nan
                pct_imp = pct_deg = pct_nonsig = 0.0
                n_sig_imp = n_sig_deg = 0
                
            csv_rows.append({
                'experiment': exp_da_name,
                'variable': col_title,
                'metric': metric,
                'median_delta_all_valid': median_delta_all,
                'median_delta_significant_only': median_delta_sig,
                'significant_positive_percent': pct_imp,
                'significant_negative_percent': pct_deg,
                'nonsignificant_percent': pct_nonsig,
                'N_valid': n_valid,
                'N_significant': n_sig
            })
            
            # Print QC info
            print(f"--- {exp_da_name} vs OL | {col_title} | {metric} ---")
            print(f"Total valid pixels: {n_valid}")
            if n_valid > 0:
                print(f"Significant Improvement: {pct_imp:.1f}%")
                print(f"Significant Degradation: {pct_deg:.1f}%")
            
            im = ax.pcolormesh(lon, lat, delta_r_sig, transform=ccrs.PlateCarree(),
                               cmap=cmap, norm=norm, shading='auto', zorder=2)
                               
            # Add compact annotation box in bottom-left (ocean area)
            metric_str = "ΔR" if metric == 'R' else "ΔanomR"
            line1 = f"Med. {metric_str} = {median_delta_all:+.2f}"
            line2 = f"Sig. +{pct_imp:.1f}% | −{pct_deg:.1f}%"
            # Append N significant for sparse coverage like GPP
            if col_title == 'GPP' or n_sig < 100:
                line2 += f" (n={n_sig})"
                
            ax.text(0.03, 0.05, f"{line1}\n{line2}", transform=ax.transAxes,
                    fontsize=8.5, va='bottom', ha='left',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cccccc', linewidth=0.5, boxstyle='round,pad=0.3'),
                    zorder=3)
                               
            if row_idx == 0:
                ax.set_title(col_title, fontsize=14, fontweight='bold', pad=10)
                
            if col_idx == 0:
                # Add row labels
                row_label = "R (DA − OL)" if metric == 'R' else "Anomaly R (DA − OL)"
                ax.text(-0.15, 0.5, row_label, va='center', ha='center', rotation='vertical',
                        transform=ax.transAxes, fontsize=14, fontweight='bold')
                        
        col_idx += 1
        ds.close()
        
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # Add shared colorbar, slightly shorter in height
    cbar_ax = fig.add_axes([0.25, 0.06, 0.5, 0.025])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', 
                        ticks=[-0.4, -0.2, 0.0, 0.2, 0.4])
    cbar.set_label("Δ correlation skill (DA − OL)", fontsize=13)
    cbar.ax.tick_params(labelsize=11)
    
    # Adjust layout
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15, wspace=0.1, hspace=0.1)
    
    fig.savefig(f"{out_prefix}_styled.png", dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(f"{out_prefix}_styled.pdf", bbox_inches='tight', facecolor='white')
    print(f"Saved {out_prefix}_styled.[png|pdf]")

def main():
    out_dir = Path("outputs/independent_ob_validation")
    
    datasets = {
        'ET': {
            'file': out_dir / 'skill_maps_gleam.nc',
            'n': 60 # 5 years
        },
        'GPP': {
            'file': out_dir / 'skill_maps_fluxsat_gpp.nc',
            'n': 60
        }
    }
    
    csv_rows = []
    
    # Plot NoCDF
    plot_flux_skill(
        'DA_NoCDF',
        'Impact of DA-NoCDF on Flux Correlation Skill (2016–2020)',
        datasets,
        out_dir / 'figure_flux_skillchange_NoCDF_vs_OL',
        csv_rows
    )
    
    # Plot CDF
    plot_flux_skill(
        'DA_CDF',
        'Impact of DA-CDF on Flux Correlation Skill (2016–2020)',
        datasets,
        out_dir / 'figure_flux_skillchange_CDF_vs_OL',
        csv_rows
    )
    
    # Export CSV
    csv_path = out_dir / 'skill_change_statistics.csv'
    fieldnames = ['experiment', 'variable', 'metric', 'median_delta_all_valid', 
                  'median_delta_significant_only', 'significant_positive_percent', 
                  'significant_negative_percent', 'nonsignificant_percent', 
                  'N_valid', 'N_significant']
                  
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Exported statistics to {csv_path}")

if __name__ == "__main__":
    main()
