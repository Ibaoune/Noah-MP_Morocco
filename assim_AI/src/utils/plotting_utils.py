# Author: M. EL Aabaribaoune (@um6p)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os

def check_dir(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def plot_map(ds, var_name, title, output_path, cmap='viridis'):
    """Plot a basic spatial map using Cartopy."""
    check_dir(output_path)
    
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    
    if var_name in ds:
        data = ds[var_name]
        im = ax.pcolormesh(ds.lon, ds.lat, data, transform=ccrs.PlateCarree(), cmap=cmap)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.COASTLINE)
        plt.colorbar(im, ax=ax, label=var_name, shrink=0.7)
        ax.set_title(title)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_scatter(y_true, y_pred, title, output_path):
    """Plot True vs Predicted scatter plot."""
    check_dir(output_path)
    
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, alpha=0.3, s=5)
    
    # 1:1 line
    min_val = min(np.nanmin(y_true), np.nanmin(y_pred))
    max_val = max(np.nanmax(y_true), np.nanmax(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--')
    
    plt.xlabel('Observed (LIS/SMAP)')
    plt.ylabel('RF Predicted')
    plt.title(title)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_feature_importance(importances, feature_names, title, output_path):
    """Plot horizontal bar chart for feature importances."""
    check_dir(output_path)
    
    # Sort
    idx = np.argsort(importances)
    
    plt.figure(figsize=(8, max(6, len(feature_names)*0.3)))
    plt.barh(np.array(feature_names)[idx], importances[idx], align='center')
    plt.xlabel('Permutation Importance')
    plt.title(title)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
