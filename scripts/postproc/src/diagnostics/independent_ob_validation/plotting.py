# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, LogNorm
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from scipy import stats

class Plotting:
    """Handles all generic and specific plotting for validation, with strict standard compliance."""
    
    @staticmethod
    def setup_style():
        sns.set_theme(style="white", font_scale=1.0)
        plt.rcParams.update({
            'axes.labelsize': 12,
            'axes.titlesize': 13,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'figure.titlesize': 16,
            'figure.titleweight': 'semibold',
            'axes.grid': True,
            'grid.color': 'lightgray',
            'grid.linewidth': 0.5,
            'grid.alpha': 0.7,
            'legend.fontsize': 11
        })
        
    @staticmethod
    def save_figure(fig, out_path, metrics_dict=None):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if out_path.endswith('.png') or out_path.endswith('.pdf'):
            base_out = out_path.rsplit('.', 1)[0]
        else:
            base_out = out_path
            
        fig.savefig(f"{base_out}.png", dpi=300, bbox_inches='tight', facecolor='white')
        fig.savefig(f"{base_out}.pdf", bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        if metrics_dict is not None:
            if "filename" not in metrics_dict:
                metrics_dict["filename"] = os.path.basename(f"{base_out}.png")
            with open(f"{base_out}.json", "w") as f:
                json.dump(metrics_dict, f, indent=4)
                
    @staticmethod
    def add_map_features(ax, bounds, margin=0.5):
        ax.set_extent([bounds[0]-margin, bounds[1]+margin, bounds[2]-margin, bounds[3]+margin], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.8, linestyle=':')
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='lightgray', alpha=0.7, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        return gl
        
    # =========================================================================
    # NEW SPECIFIC PLOTTING METHODS
    # =========================================================================

    @staticmethod
    def plot_tws_time_series(df, title, subtitle, out_path, metrics_dict=None):
        fig = plt.figure(figsize=(10, 7))
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.1)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        obs_col = next((c for c in df.columns if 'obs' in c.lower()), None)
        opl_col = next((c for c in df.columns if 'opl' in c.lower()), None)
        
        if obs_col:
            ax1.plot(df.index, df[obs_col], color='black', marker='o', markersize=5, linestyle='-', linewidth=1, label='GRACE')
        if opl_col:
            ax1.plot(df.index, df[opl_col], color='#1f77b4', marker='o', markersize=4, linestyle='-', linewidth=1.5, label='LIS open loop')
            
        ax1.axhline(0, color='gray', linestyle='-', linewidth=1)
        
        max_val = np.nanmax(np.abs(df.values))
        max_val = np.ceil(max_val / 10) * 10
        ax1.set_ylim(-max_val, max_val)
        ax1.set_ylabel("TWS anomaly [mm]")
        ax1.legend(loc='upper right')
        
        if obs_col and opl_col:
            valid = df.dropna()
            if len(valid) > 2:
                r, _ = stats.pearsonr(valid[obs_col], valid[opl_col])
                bias = (valid[opl_col] - valid[obs_col]).mean()
                rmse = np.sqrt(((valid[opl_col] - valid[obs_col])**2).mean())
                std_ratio = valid[opl_col].std() / valid[obs_col].std()
                stats_str = f"N = {len(valid)}\nr = {r:.2f}\nbias = {bias:.1f}\nRMSE = {rmse:.1f}\nσ ratio = {std_ratio:.2f}"
                ax1.text(0.02, 0.95, stats_str, transform=ax1.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
        if obs_col and opl_col:
            diff = df[opl_col] - df[obs_col]
            ax2.plot(df.index, diff, color='black', linewidth=1.2)
            ax2.fill_between(df.index, 0, diff, where=diff>=0, color='red', alpha=0.3)
            ax2.fill_between(df.index, 0, diff, where=diff<0, color='blue', alpha=0.3)
            ax2.axhline(0, color='gray', linestyle='-', linewidth=1)
            ax2.set_ylabel("LIS − GRACE [mm]")
            max_diff = np.nanmax(np.abs(diff))
            max_diff = np.ceil(max_diff / 5) * 5
            ax2.set_ylim(-max_diff, max_diff)
            
        plt.setp(ax1.get_xticklabels(), visible=False)
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        fig.suptitle(title, y=0.96)
        ax1.set_title(subtitle, fontsize=12, pad=10)
        
        Plotting.save_figure(fig, out_path, metrics_dict)

    @staticmethod
    def plot_tws_mean_panels(grace_da, lis_da, diff_da, title, out_path, bounds, n_matched=None, metrics_dict=None):
        fig = plt.figure(figsize=(15, 6.5))
        gs = gridspec.GridSpec(1, 3, wspace=0.1, top=0.85, bottom=0.25)
        
        axes = [fig.add_subplot(gs[i], projection=ccrs.PlateCarree()) for i in range(3)]
        
        all_vals = np.concatenate([grace_da.values.flatten(), lis_da.values.flatten()])
        all_vals = all_vals[~np.isnan(all_vals)]
        if len(all_vals) > 0:
            vmax = np.ceil(np.nanquantile(np.abs(all_vals), 0.98) / 5) * 5
        else:
            vmax = 50
        vmin = -vmax
        levels = np.linspace(vmin, vmax, 13)
        cmap = sns.color_palette("vlag", as_cmap=True)
        
        diff_vals = diff_da.values.flatten()
        diff_vals = diff_vals[~np.isnan(diff_vals)]
        if len(diff_vals) > 0:
            diff_max = np.ceil(np.nanquantile(np.abs(diff_vals), 0.98) / 5) * 5
        else:
            diff_max = 50
        diff_levels = np.linspace(-diff_max, diff_max, 11)
        diff_cmap = sns.color_palette("vlag", as_cmap=True)
        
        lon = grace_da.coords.get('lon', grace_da.coords.get('longitude')).values
        lat = grace_da.coords.get('lat', grace_da.coords.get('latitude')).values
        
        im1 = axes[0].pcolormesh(lon, lat, grace_da.values, transform=ccrs.PlateCarree(), cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
        axes[1].pcolormesh(lon, lat, lis_da.values, transform=ccrs.PlateCarree(), cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
        im3 = axes[2].pcolormesh(lon, lat, diff_da.values, transform=ccrs.PlateCarree(), cmap=diff_cmap, vmin=-diff_max, vmax=diff_max, shading='auto')
        
        subtitles = ["(a) GRACE", "(b) LIS open loop", "(c) LIS − GRACE"]
        for i, ax in enumerate(axes):
            Plotting.add_map_features(ax, bounds, margin=0.5)
            ax.set_title(subtitles[i], fontsize=13)
            
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='lightgray', alpha=0.7, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            if i > 0:
                gl.left_labels = False
                
        cbar_ax1 = fig.add_axes([0.15, 0.1, 0.4, 0.03])
        cbar1 = fig.colorbar(im1, cax=cbar_ax1, orientation='horizontal')
        cbar1.set_label("TWS Anomaly [mm]")
        
        cbar_ax2 = fig.add_axes([0.65, 0.1, 0.2, 0.03])
        cbar2 = fig.colorbar(im3, cax=cbar_ax2, orientation='horizontal')
        cbar2.set_label("LIS − GRACE [mm]")
        
        fig.suptitle(title, y=0.98)
        if n_matched:
            fig.text(0.5, 0.93, f"Based on {n_matched} matched months in 2016", ha='center', fontsize=12)
            
        Plotting.save_figure(fig, out_path, metrics_dict)

    @staticmethod
    def plot_alignment_smoke_test_map(lis_mask, esa_mask, common_mask, out_path, bounds, qc_text):
        if 'lat' in lis_mask.dims and 'lon' in lis_mask.dims:
            lis_mask = lis_mask.transpose(..., 'lat', 'lon')
        if 'lat' in esa_mask.dims and 'lon' in esa_mask.dims:
            esa_mask = esa_mask.transpose(..., 'lat', 'lon')
            
        fig = plt.figure(figsize=(12, 6), constrained_layout=True)
        gs = gridspec.GridSpec(1, 2)
        axes = [fig.add_subplot(gs[i], projection=ccrs.PlateCarree()) for i in range(2)]
        
        lis_mask.plot.pcolormesh(ax=axes[0], transform=ccrs.PlateCarree(), cmap='Greens', add_colorbar=False, vmin=0, vmax=1)
        axes[0].set_title("(a) LIS Valid Mask", fontsize=13)
        
        common_mask.plot.pcolormesh(ax=axes[1], transform=ccrs.PlateCarree(), cmap='Blues', add_colorbar=False, vmin=0, vmax=1)
        axes[1].set_title("(b) Common Valid Mask with ESA CCI", fontsize=13)
        
        for ax in axes:
            Plotting.add_map_features(ax, bounds, margin=0.5)
            
        fig.suptitle("Spatial Extents (Smoke Test)", fontsize=16, fontweight='semibold')
        plt.figtext(0.5, -0.05, qc_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray'))
        
        plt.savefig(out_path + ".png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        
    @staticmethod
    def plot_spatial_rmse(rmse_da, out_path, bounds, qc_text, metrics_dict=None):
        fig = plt.figure(figsize=(8, 6.5))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        
        levels = [0.025, 0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060, 0.065, 0.070]
        cmap = plt.get_cmap("YlOrRd").resampled(len(levels)+1)
        norm = BoundaryNorm(levels, ncolors=cmap.N, extend='both')
        
        lon = rmse_da.coords.get('lon', rmse_da.coords.get('longitude')).values
        lat = rmse_da.coords.get('lat', rmse_da.coords.get('latitude')).values
        
        im = ax.pcolormesh(lon, lat, rmse_da.values, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto')
        
        Plotting.add_map_features(ax, bounds, margin=0.5)
        
        cbar_ax = fig.add_axes([0.15, 0.08, 0.7, 0.03])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both', ticks=levels)
        cbar.set_label("RMSE [m³ m⁻³]")
        
        ax.set_title("LIS open loop versus ESA CCI Combined — NorthMor, 2016", fontsize=13, pad=10)
        fig.suptitle("Spatial RMSE of daily surface soil moisture", y=0.96)
        
        ax.text(0.02, 0.02, qc_text, transform=ax.transAxes, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=10)
        
        Plotting.save_figure(fig, out_path, metrics_dict)
        
    @staticmethod
    def plot_spatial_bias(bias_da, out_path, bounds, qc_text, metrics_dict=None):
        fig = plt.figure(figsize=(8, 6.5))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        
        levels = [-0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06]
        cmap = plt.get_cmap("RdBu_r").resampled(len(levels)+1)
        norm = BoundaryNorm(levels, ncolors=cmap.N, extend='both')
        
        lon = bias_da.coords.get('lon', bias_da.coords.get('longitude')).values
        lat = bias_da.coords.get('lat', bias_da.coords.get('latitude')).values
        
        im = ax.pcolormesh(lon, lat, bias_da.values, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto')
        
        Plotting.add_map_features(ax, bounds, margin=0.5)
        
        cbar_ax = fig.add_axes([0.15, 0.08, 0.7, 0.03])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both', ticks=[-0.06, -0.04, -0.02, 0.00, 0.02, 0.04, 0.06])
        cbar.set_label("Bias, LIS − ESA CCI [m³ m⁻³]")
        
        ax.set_title("LIS open loop minus ESA CCI Combined — NorthMor, 2016", fontsize=13, pad=10)
        fig.suptitle("Surface soil-moisture bias", y=0.96)
        
        qc_full = "Blue: LIS drier\nRed: LIS wetter\n\n" + qc_text
        ax.text(0.02, 0.02, qc_full, transform=ax.transAxes, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=10)
        
        Plotting.save_figure(fig, out_path, metrics_dict)
        
    @staticmethod
    def plot_pooled_scatterplots(obs_da, lis_datasets, out_path, metrics_dict=None):
        experiments = list(lis_datasets.keys())
        n_exp = len(experiments)
        fig = plt.figure(figsize=(6 * n_exp, 6))
        gs = gridspec.GridSpec(1, n_exp, wspace=0.15)
        
        obs_flat = obs_da.values.flatten()
        
        for i, exp_name in enumerate(experiments):
            ax = fig.add_subplot(gs[i])
            lis_flat = lis_datasets[exp_name].values.flatten()
            valid = ~np.isnan(obs_flat) & ~np.isnan(lis_flat)
            x = obs_flat[valid]
            y = lis_flat[valid]
            
            if len(x) == 0: continue
            
            hb = ax.hexbin(x, y, gridsize=50, cmap='viridis', norm=LogNorm(), mincnt=1)
            
            ax.plot([0, 0.6], [0, 0.6], 'k--', lw=1)
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            ax.plot([0, 0.6], [intercept, slope*0.6 + intercept], 'r-', lw=1.5, alpha=0.8)
            
            axis_max = min(0.6, max(np.percentile(x, 99.9), np.percentile(y, 99.9)) + 0.05)
            ax.set_xlim(0, axis_max)
            ax.set_ylim(0, axis_max)
            ax.set_aspect('equal')
            
            ax.set_title(f"{exp_name}", fontsize=13)
            ax.set_xlabel("ESA CCI Combined [m³ m⁻³]")
            if i == 0: ax.set_ylabel("LIS [m³ m⁻³]")
            
            bias = (y - x).mean()
            rmse = np.sqrt(((y - x)**2).mean())
            ubrmse = np.sqrt(max(0, rmse**2 - bias**2))
            rho, _ = stats.spearmanr(x, y)
            
            stats_str = f"N = {len(x)}\nr = {r_value:.2f}\nρ = {rho:.2f}\nbias = {bias:.3f}\nRMSE = {rmse:.3f}\nubRMSE = {ubrmse:.3f}\ny = {slope:.2f}x + {intercept:.2f}"
            ax.text(0.05, 0.95, stats_str, transform=ax.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=10)
            
            if i == n_exp - 1:
                cbar = fig.colorbar(hb, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
                cbar.set_label("Matched pairs per bin")
                
        fig.suptitle("Daily surface soil moisture: LIS versus ESA CCI Combined\nSubtitle: Pooled matched grid-cell observations — NorthMor, 2016", y=1.02)
        
        Plotting.save_figure(fig, out_path, metrics_dict)

    @staticmethod
    def plot_domain_time_series(df, out_path, metrics_dict=None):
        fig = plt.figure(figsize=(10, 7))
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.1)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        opl_col = next((c for c in df.columns if 'opl' in c.lower()), None)
        obs_col = 'OBS'
        
        ax1.plot(df.index, df[obs_col], color='black', marker='o', markersize=4, linestyle='-', linewidth=0.5, label='ESA CCI Combined')
        if opl_col:
            ax1.plot(df.index, df[opl_col], color='#1f77b4', linestyle='-', linewidth=1.8, label='LIS open loop')
        
        valid = df.dropna()
        if opl_col and len(valid) > 2:
            r, _ = stats.pearsonr(valid[obs_col], valid[opl_col])
            bias = (valid[opl_col] - valid[obs_col]).mean()
            rmse = np.sqrt(((valid[opl_col] - valid[obs_col])**2).mean())
            ubrmse = np.sqrt(max(0, rmse**2 - bias**2))
            stats_str = f"N = {len(valid)}\nr = {r:.2f}\nbias = {bias:.3f}\nRMSE = {rmse:.3f}\nubRMSE = {ubrmse:.3f}"
            ax1.text(0.02, 0.95, stats_str, transform=ax1.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=10)
            
        ax1.set_ylabel("Surface soil moisture [m³ m⁻³]")
        ax1.legend(loc='upper right')
        
        if opl_col:
            diff = df[opl_col] - df[obs_col]
            ax2.plot(df.index, diff, color='#333333', linewidth=1.2)
            ax2.fill_between(df.index, 0, diff, where=diff>=0, color='red', alpha=0.3)
            ax2.fill_between(df.index, 0, diff, where=diff<0, color='blue', alpha=0.3)
            ax2.axhline(0, color='gray', linestyle='-', linewidth=1)
            ax2.set_ylabel("LIS − ESA CCI [m³ m⁻³]")
            
            max_diff = np.nanmax(np.abs(diff))
            max_diff = np.ceil(max_diff / 0.01) * 0.01
            if max_diff > 0:
                ax2.set_ylim(-max_diff, max_diff)
        
        plt.setp(ax1.get_xticklabels(), visible=False)
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        ax1.grid(axis='x', color='lightgray', linestyle='-', alpha=0.5)
        ax2.grid(axis='x', color='lightgray', linestyle='-', alpha=0.5)
        
        fig.suptitle("Domain-mean surface soil moisture over NorthMor — 2016", y=0.96)
        ax1.set_title("Area-weighted LIS open loop and ESA CCI Combined", fontsize=12, pad=10)
        
        Plotting.save_figure(fig, out_path, metrics_dict)

    @staticmethod
    def plot_annual_mean_and_bias(obs_da, lis_da, bias_da, out_path, bounds, metrics_dict=None):
        fig = plt.figure(figsize=(15, 6))
        gs = gridspec.GridSpec(1, 3, wspace=0.1)
        axes = [fig.add_subplot(gs[i], projection=ccrs.PlateCarree()) for i in range(3)]
        
        levels = [0.075, 0.100, 0.125, 0.150, 0.175, 0.200, 0.225, 0.250]
        cmap = plt.get_cmap("YlGnBu").resampled(len(levels)+1)
        norm = BoundaryNorm(levels, ncolors=cmap.N, extend='both')
        
        lon = obs_da.coords.get('lon', obs_da.coords.get('longitude')).values
        lat = obs_da.coords.get('lat', obs_da.coords.get('latitude')).values
        
        im1 = axes[0].pcolormesh(lon, lat, obs_da.values, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto')
        axes[1].pcolormesh(lon, lat, lis_da.values, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto')
        
        bias_levels = [-0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06]
        bias_cmap = plt.get_cmap("RdBu_r").resampled(len(bias_levels)+1)
        bias_norm = BoundaryNorm(bias_levels, ncolors=bias_cmap.N, extend='both')
        
        im3 = axes[2].pcolormesh(lon, lat, bias_da.values, transform=ccrs.PlateCarree(), cmap=bias_cmap, norm=bias_norm, shading='auto')
        
        subtitles = ["(a) ESA CCI Combined", "(b) LIS open loop", "(c) LIS − ESA CCI"]
        for i, ax in enumerate(axes):
            Plotting.add_map_features(ax, bounds, margin=0.5)
            ax.set_title(subtitles[i], fontsize=13)
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='lightgray', alpha=0.7, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            if i > 0:
                gl.left_labels = False
                
        cbar_ax1 = fig.add_axes([0.15, 0.08, 0.4, 0.03])
        cbar1 = fig.colorbar(im1, cax=cbar_ax1, orientation='horizontal', extend='both', ticks=levels)
        cbar1.set_label("Mean surface soil moisture [m³ m⁻³]")
        
        cbar_ax2 = fig.add_axes([0.65, 0.08, 0.2, 0.03])
        cbar2 = fig.colorbar(im3, cax=cbar_ax2, orientation='horizontal', extend='both', ticks=[-0.06, -0.04, -0.02, 0.00, 0.02, 0.04, 0.06])
        cbar2.set_label("Mean bias [m³ m⁻³]")
        
        fig.suptitle("Annual mean surface soil moisture over NorthMor — 2016", y=0.98)
        
        Plotting.save_figure(fig, out_path, metrics_dict)

    @staticmethod
    def plot_data_coverage(valid_count, total_days, out_path, bounds, threshold, metrics_dict=None):
        fig = plt.figure(figsize=(8, 6.5))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        
        percentage = valid_count / total_days * 100.0
        
        levels = [0, 20, 40, 60, 80, 90, 95, 100]
        cmap = plt.get_cmap("viridis").resampled(len(levels)-1)
        norm = BoundaryNorm(levels, ncolors=cmap.N)
        
        lon = valid_count.coords.get('lon', valid_count.coords.get('longitude')).values
        lat = valid_count.coords.get('lat', valid_count.coords.get('latitude')).values
        
        im = ax.pcolormesh(lon, lat, percentage.values, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm, shading='auto')
        
        fail_mask = (valid_count.values < threshold) & (valid_count.values > 0)
        if fail_mask.any():
            ax.pcolormesh(lon, lat, np.where(fail_mask, 1, np.nan), transform=ccrs.PlateCarree(), hatch='///', alpha=0)
        
        Plotting.add_map_features(ax, bounds, margin=0.5)
        
        cbar_ax = fig.add_axes([0.15, 0.08, 0.7, 0.03])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', ticks=levels)
        cbar.set_label("Temporal coverage [% of matched days]")
        
        ax.set_title("NorthMor, 2016", fontsize=13, pad=10)
        fig.suptitle("Temporal coverage of matched LIS–ESA CCI observations", y=0.96)
        
        median_pct = np.nanmedian(percentage.values[percentage.values > 0])
        valid_land_cells = np.sum(valid_count.values > 0)
        passing_cells = np.sum(valid_count.values >= threshold)
        pass_pct = passing_cells / valid_land_cells * 100 if valid_land_cells > 0 else 0
        
        stats_str = f"Total candidate days = {total_days}\nMedian coverage = {median_pct:.1f}%\nCells ≥ {threshold} pairs = {pass_pct:.1f}%\n(Hatched regions fail QC)"
        ax.text(0.02, 0.02, stats_str, transform=ax.transAxes, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=10)
        
        Plotting.save_figure(fig, out_path, metrics_dict)

    # =========================================================================
    # PRESERVED LEGACY METHODS (do not touch except save_figure changes)
    # =========================================================================

    @staticmethod
    def plot_time_series(df, title, ylabel, out_path, metrics=None):
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
        colors = {'OBS': 'black', 'OPL': '#1f77b4', 'DA_nocdf': '#ff7f0e', 'DA_cdf': '#2ca02c'}
        styles = {'OBS': 'o', 'OPL': '-', 'DA_nocdf': '--', 'DA_cdf': '-.'}
        labels = {'OBS': 'ESA CCI Combined', 'OPL': 'Open loop', 'DA_nocdf': 'SMAP-DA without CDF', 'DA_cdf': 'SMAP-DA with CDF'}
        ax1 = axes[0]
        ax2 = axes[1]
        obs_col = next((c for c in df.columns if 'obs' in c.lower()), None)
        opl_col = next((c for c in df.columns if 'opl' in c.lower()), None)
        nocdf_col = next((c for c in df.columns if 'nocdf' in c.lower()), None)
        cdf_col = next((c for c in df.columns if 'cdf' in c.lower() and 'nocdf' not in c.lower()), None)
        if obs_col:
            ax1.plot(df.index, df[obs_col], label=labels['OBS'], color=colors['OBS'], marker=styles['OBS'], markersize=4, linestyle='none')
        if opl_col:
            ax1.plot(df.index, df[opl_col], label=labels['OPL'], color=colors['OPL'], linestyle=styles['OPL'], linewidth=2)
        if nocdf_col:
            ax1.plot(df.index, df[nocdf_col], label=labels['DA_nocdf'], color=colors['DA_nocdf'], linestyle=styles['DA_nocdf'], linewidth=2)
        if cdf_col:
            ax1.plot(df.index, df[cdf_col], label=labels['DA_cdf'], color=colors['DA_cdf'], linestyle=styles['DA_cdf'], linewidth=2)
        ax1.set_title(title, fontweight='bold', fontsize=12)
        ax1.set_ylabel(ylabel)
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        if opl_col:
            if nocdf_col:
                ax2.plot(df.index, df[nocdf_col] - df[opl_col], color=colors['DA_nocdf'], linestyle=styles['DA_nocdf'], linewidth=2, label=f"{labels['DA_nocdf']} - OPL")
            if cdf_col:
                ax2.plot(df.index, df[cdf_col] - df[opl_col], color=colors['DA_cdf'], linestyle=styles['DA_cdf'], linewidth=2, label=f"{labels['DA_cdf']} - OPL")
            ax2.axhline(0, color='gray', linestyle='-', linewidth=1)
            ax2.set_ylabel("Diff vs OPL")
            ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        import matplotlib.dates as mdates
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()
        Plotting.save_figure(fig, out_path, metrics)

    @staticmethod
    def plot_map_panels(data_dict, title, out_path, cbar_label, cmap='RdBu', divergent=True, metrics_dict=None):
        n_panels = len(data_dict)
        fig = plt.figure(figsize=(18, 6))
        all_vals = []
        for da in data_dict.values():
            all_vals.append(da.values.flatten())
        all_vals = np.concatenate(all_vals)
        all_vals = all_vals[~np.isnan(all_vals)]
        if len(all_vals) == 0:
            return
        if divergent:
            vmax = np.nanquantile(np.abs(all_vals), 0.98)
            vmin = -vmax
        else:
            vmin = np.nanquantile(all_vals, 0.02)
            vmax = np.nanquantile(all_vals, 0.98)
        axes = []
        for i, (panel_title, da) in enumerate(data_dict.items()):
            ax = fig.add_subplot(1, n_panels, i+1, projection=ccrs.PlateCarree())
            axes.append(ax)
            lon_name = 'lon' if 'lon' in da.coords else 'longitude'
            lat_name = 'lat' if 'lat' in da.coords else 'latitude'
            lon = da[lon_name].values
            lat = da[lat_name].values
            valid_mask = da.notnull().compute()
            if valid_mask.any():
                dropped = valid_mask.where(valid_mask, drop=True)
                valid_lats = dropped[lat_name].values
                valid_lons = dropped[lon_name].values
                lat_min, lat_max = np.nanmin(valid_lats), np.nanmax(valid_lats)
                lon_min, lon_max = np.nanmin(valid_lons), np.nanmax(valid_lons)
                margin = 0.5
                ax.set_extent([lon_min - margin, lon_max + margin, lat_min - margin, lat_max + margin], crs=ccrs.PlateCarree())
            else:
                ax.set_extent([-10, -1, 30, 36], crs=ccrs.PlateCarree())
            im = ax.pcolormesh(lon, lat, da.values, transform=ccrs.PlateCarree(), cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
            ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.8, linestyle=':')
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            if i > 0:
                gl.left_labels = False
            ax.set_title(panel_title, fontsize=12)
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.05)
        cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.03])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
        cbar.set_label(cbar_label)
        Plotting.save_figure(fig, out_path, metrics_dict)


    @staticmethod
    def plot_smoke_test_timeseries(obs_ds, lis_datasets, obs_var, common_mask, out_path, ylabel="Values"):
        df_data = {}
        obs_lat_name = 'lat' if 'lat' in obs_ds.coords else 'latitude'
        obs_lon_name = 'lon' if 'lon' in obs_ds.coords else 'longitude'
        obs_lat = obs_ds[obs_lat_name]
        weights = np.cos(np.deg2rad(obs_lat))
        weights.name = "weights"
        
        masked_obs = obs_ds.where(common_mask)
        obs_weighted = masked_obs[obs_var].weighted(weights)
        df_data['ESA CCI Combined'] = obs_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()
        
        for exp_name, ds in lis_datasets.items():
            var_name = list(ds.data_vars)[0]
            masked_lis = ds[var_name].where(common_mask)
            lis_weighted = masked_lis.weighted(weights)
            
            label_map = {
                'OPL_noirr_2016': 'Open loop',
                'DA_smap_nocdf_noirr_2016': 'SMAP-DA without CDF',
                'DA_smap_cdf_noirr_2016': 'SMAP-DA with CDF'
            }
            label = label_map.get(exp_name, exp_name)
            df_data[label] = lis_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()
            
        df = pd.DataFrame(df_data).dropna(how='all')
        if len(lis_datasets) == 1:
            Plotting.plot_time_series(df, "Domain-Mean Surface Soil Moisture vs ESA CCI", ylabel, out_path)
        else:
            Plotting.plot_time_series(df, "Domain-Mean Surface Soil Moisture vs ESA CCI", ylabel, out_path)
