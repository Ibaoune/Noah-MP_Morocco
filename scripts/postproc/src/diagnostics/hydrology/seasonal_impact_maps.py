# Author: M. EL Aabaribaoune (@um6p)

import os
import glob
import yaml
import logging
import copy
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
import rasterio
import argparse

from src.core.config import load_yaml, load_global_config, load_experiments_catalog, load_variable
from src.io.lis import load_lis_variable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constants
DOMAIN_BBOX = [-13.5, -1.0, 27.5, 36.0]
MONTHS_IN_YEAR = 12

class ObjDict(dict):
    """Utility class to allow dot notation access to dictionary attributes."""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

def get_files_for_season(exp_path, start_year, end_year, season_months):
    """Collect all LIS history NetCDF files for the specified years and months."""
    files = []
    for year in range(start_year, end_year + 1):
        for month in season_months:
            # LIS_HIST daily output pattern in NorthMor experiments
            pattern = os.path.join(exp_path, f"{year}-{month:02d}", "SURFACEMODEL", f"{year}{month:02d}", "LIS_HIST_*.nc")
            month_files = sorted(glob.glob(pattern))
            if month_files:
                files.extend(month_files)
    return files

def compute_seasonal_climatologies(config_path):
    """Extract and aggregate the seasonal data required for plotting."""
    cfg = load_yaml(config_path)
    
    postproc_dir = Path(config_path).parent.parent.parent
    global_cfg = load_global_config(str(postproc_dir / 'configs' / 'global.yaml'))
    experiments = load_experiments_catalog(str(postproc_dir / 'configs' / 'experiments.yaml'), global_cfg)
    variables_dir = str(postproc_dir / 'configs' / 'variables')
    
    out_dir = postproc_dir / cfg['paths']['output_dir']
    out_dir_nc = out_dir / 'climatology_nc'
    out_dir_nc.mkdir(parents=True, exist_ok=True)
    
    start_year = cfg['period']['start_year']
    end_year = cfg['period']['end_year']
    
    req_exps = [cfg['experiments']['reference'], cfg['experiments']['assimilation']]
    req_seasons = cfg['seasons']
    req_vars = cfg['variables_required']
    
    for var_id in req_vars:
        # Load variable definition
        var_cfg_dict = load_variable(var_id, variables_dir)
        if not var_cfg_dict:
            logger.error(f"Variable config not found for {var_id}")
            continue
            
        var_cfg = ObjDict(var_cfg_dict)
        op = var_cfg.input.get('operation', 'direct')
        var_names = var_cfg.input.get('lis_variable_names', [])
        
        for exp_id in req_exps:
            exp_path = experiments[exp_id]['path_abs']
            if not exp_path:
                logger.error(f"Experiment path not resolved for {exp_id}")
                continue
                
            # Define the temporal aggregations needed
            temporal_agg = list(req_seasons.items())
            if var_id == 'total_runoff':
                for m in range(1, 13):
                    temporal_agg.append((f"M{m:02d}", [m]))
                    
            for season_name, season_months in temporal_agg:
                out_nc = out_dir_nc / f"{var_id}_{exp_id}_{season_name}_{start_year}_{end_year}.nc"
                if out_nc.exists():
                    logger.info(f"Using cached file: {out_nc}")
                    continue
                    
                logger.info(f"Computing climatology for {var_id} | {exp_id} | {season_name} ...")
                files = get_files_for_season(exp_path, start_year, end_year, season_months)
                
                if not files:
                    logger.warning(f"No files found for {exp_id} season {season_name}")
                    continue
                    
                # Implement YAML variable operations (since load_lis_variable only takes files and var_name)
                # First, parse scale_factor and unit conversions manually if needed for precip/runoff
                scale_factor = 1.0
                unit = var_cfg.get('unit', '')
                nc_unit = None
                
                # Check unit in first file
                try:
                    with xr.open_dataset(files[0]) as ds_test:
                        if var_names[0] in ds_test.variables:
                            nc_unit = ds_test.variables[var_names[0]].attrs.get('units', None)
                except:
                    pass
                    
                if unit in ['mm/day', 'mm day-1'] and nc_unit:
                    if nc_unit.strip() in ['kg m-2 s-1', 'kg/m2/s']:
                        scale_factor = 86400.0
                        
                layer_yaml = var_cfg.input.get('layer', None)
                layer_idx = layer_yaml - 1 if layer_yaml is not None else None
                
                if op in ['direct', 'extract_layer', 'identity']:
                    data_3d = load_lis_variable(files, var_names[0], extract_layer=layer_idx)
                elif op == 'sum':
                    arrays = [load_lis_variable(files, vn) for vn in var_names]
                    arrays = [a for a in arrays if a is not None]
                    data_3d = np.sum(arrays, axis=0) if arrays else None
                else:
                    data_3d = load_lis_variable(files, var_names[0], extract_layer=layer_idx)
                
                if data_3d is None:
                    logger.warning(f"Failed to load data for {var_id}")
                    continue
                    
                data_3d = np.where(data_3d <= -9000, np.nan, data_3d)
                if scale_factor != 1.0:
                    data_3d = data_3d * scale_factor
                    
                # Time mean
                climatology = np.nanmean(data_3d, axis=0)
                
                # Extract lat/lon from the first file to save NetCDF
                with xr.open_dataset(files[0]) as ds0:
                    lat = ds0.lat.values
                    lon = ds0.lon.values
                
                # Save NetCDF
                ds_out = xr.Dataset(
                    {var_id: (["lat", "lon"], climatology)},
                    coords={"lon": (["lon"], lon[0,:] if lat.ndim==2 else lon), 
                            "lat": (["lat"], lat[:,0] if lat.ndim==2 else lat)}
                )
                ds_out.to_netcdf(out_nc)
                logger.info(f"Saved {out_nc}")

def get_map_axis(fig, row, col, n_rows, n_cols):
    ax = fig.add_subplot(n_rows, n_cols, (row * n_cols) + col + 1, projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='#333333')
    ax.add_feature(cfeature.BORDERS, linewidth=0.6, linestyle=':', edgecolor='#555555')
    ax.set_extent(DOMAIN_BBOX, crs=ccrs.PlateCarree())
    return ax

def add_colorbar(fig, im, ax_list, label, diff=False):
    cbar = fig.colorbar(im, ax=ax_list, orientation='horizontal', fraction=0.04, pad=0.08, extend='both')
    cbar.set_label(label, fontsize=10, fontweight='bold')
    return cbar

def load_nc(out_dir_nc, var_id, exp_id, season_name, start_year, end_year):
    path = out_dir_nc / f"{var_id}_{exp_id}_{season_name}_{start_year}_{end_year}.nc"
    if path.exists():
        with xr.open_dataset(path) as ds:
            # Squeeze to ensure 2D in case of spurious dimensions
            return ds[var_id].values.squeeze(), ds.lon.values, ds.lat.values
    return None, None, None

def _get_norm_cmap(var_cfg, diff=False, cmap_override=None):
    if diff:
        cmap_name = cmap_override or var_cfg.get('plotting', {}).get('difference_cmap', 'RdBu')
        vmin = var_cfg.get('plotting', {}).get('difference_vmin', -0.05)
        vmax = var_cfg.get('plotting', {}).get('difference_vmax', 0.05)
        levels = var_cfg.get('plotting', {}).get('difference_levels', None)
    else:
        cmap_name = cmap_override or var_cfg.get('plotting', {}).get('cmap', 'viridis')
        vmin = var_cfg.get('plotting', {}).get('vmin', 0)
        vmax = var_cfg.get('plotting', {}).get('vmax', 1)
        levels = var_cfg.get('plotting', {}).get('levels', None)
        
    cmap = copy.copy(plt.get_cmap(cmap_name))
    cmap.set_bad(color='white')
    
    if levels:
        norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N, extend='both')
    elif diff:
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
    else:
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        
    return cmap, norm

def plot_family_a_soil_moisture(cfg, out_dir, out_dir_nc, variables_dir):
    logger.info("Plotting Family A: Soil Moisture...")
    
    var_id = 'surface_soil_moisture'
    var_cfg_dict = load_variable(var_id, variables_dir)
    if not var_cfg_dict:
        return
    
    var_cfg = ObjDict(var_cfg_dict)
    start_year = cfg['period']['start_year']
    end_year = cfg['period']['end_year']
    ref_exp = cfg['experiments']['reference']
    da_exp = cfg['experiments']['assimilation']
    
    fig = plt.figure(figsize=(12, 8))
    
    seasons = ['DJF', 'JJA']
    ims_abs = []
    ims_diff = []
    ax_abs = []
    ax_diff = []
    
    letters = [['a', 'b', 'c'], ['d', 'e', 'f']]
    
    cmap_abs, _ = _get_norm_cmap(var_cfg, diff=False, cmap_override=cfg['style']['cmap_soil_moisture'])
    cmap_diff, _ = _get_norm_cmap(var_cfg, diff=True, cmap_override='RdBu_r')
    
    # Updated limits based on QC
    norm_abs = mcolors.Normalize(vmin=0.05, vmax=0.30)
    norm_diff = mcolors.TwoSlopeNorm(vmin=-0.10, vcenter=0.0, vmax=0.10)
    
    for row, season in enumerate(seasons):
        ol_data, lon, lat = load_nc(out_dir_nc, var_id, ref_exp, season, start_year, end_year)
        da_data, _, _ = load_nc(out_dir_nc, var_id, da_exp, season, start_year, end_year)
        
        if ol_data is None or da_data is None:
            continue
            
        diff_data = da_data - ol_data
        
        # 1. OL
        ax1 = get_map_axis(fig, row, 0, 2, 3)
        im1 = ax1.pcolormesh(lon, lat, ol_data, transform=ccrs.PlateCarree(), cmap=cmap_abs, norm=norm_abs, shading='auto')
        ax1.set_title(f"OL — {season}", fontweight='bold', fontsize=10)
        ax_abs.append(ax1)
        ims_abs.append(im1)
        
        # 2. DA
        ax2 = get_map_axis(fig, row, 1, 2, 3)
        im2 = ax2.pcolormesh(lon, lat, da_data, transform=ccrs.PlateCarree(), cmap=cmap_abs, norm=norm_abs, shading='auto')
        ax2.set_title(f"DA-NoCDF — {season}", fontweight='bold', fontsize=10)
        ax_abs.append(ax2)
        
        # 3. Diff
        ax3 = get_map_axis(fig, row, 2, 2, 3)
        im3 = ax3.pcolormesh(lon, lat, diff_data, transform=ccrs.PlateCarree(), cmap=cmap_diff, norm=norm_diff, shading='auto')
        ax3.set_title(f"DA-NoCDF − OL — {season}", fontweight='bold', fontsize=10)
        
        # Add compact annotations
        valid_diff = diff_data[~np.isnan(diff_data)]
        if len(valid_diff) > 0:
            median_val = np.median(valid_diff)
            pct_dry = np.sum(valid_diff < 0) / len(valid_diff) * 100
            pct_wet = np.sum(valid_diff > 0) / len(valid_diff) * 100
            annot_text = f"Median ΔSM: {median_val:.3f}\nDrying: {pct_dry:.1f}%\nWetting: {pct_wet:.1f}%"
            ax3.text(0.02, 0.05, annot_text, transform=ax3.transAxes, fontsize=8,
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
        
        ax_diff.append(ax3)
        ims_diff.append(im3)

    if ims_abs:
        add_colorbar(fig, ims_abs[0], ax_abs, var_cfg.plotting.get('colorbar_label', 'Soil Moisture'))
    if ims_diff:
        add_colorbar(fig, ims_diff[0], ax_diff, var_cfg.plotting.get('difference_label', 'Difference'), diff=True)
        
    plt.savefig(out_dir / f"fig_sm_seasonal_{ref_exp}_vs_{da_exp}_{start_year}_{end_year}.png", dpi=cfg['style']['dpi'], bbox_inches='tight')
    plt.close(fig)

def load_gmia_mask(gmia_path, lats, lons):
    """Load GMIA ASCII grid and interpolate to model grid using scipy griddata."""
    if not os.path.exists(gmia_path):
        logger.warning(f"GMIA file not found: {gmia_path}")
        if lats.ndim == 1:
            return np.zeros((len(lats), len(lons)))
        return np.zeros(lats.shape)
        
    with rasterio.open(gmia_path) as src:
        data = src.read(1)
        data = np.where(data == src.nodata, np.nan, data)
        # Create meshgrid for interpolation
        row_indices, col_indices = np.indices(data.shape)
        xs, ys = rasterio.transform.xy(src.transform, row_indices, col_indices)
        pts = np.column_stack([np.array(xs).flatten(), np.array(ys).flatten()])
        vals = data.flatten()
        
        valid = ~np.isnan(vals)
        from scipy.interpolate import griddata
        
        if lats.ndim == 1:
            lons_2d, lats_2d = np.meshgrid(lons, lats)
        else:
            lons_2d, lats_2d = lons, lats
            
        # Griddata to model grid
        model_pts = np.column_stack([lons_2d.flatten(), lats_2d.flatten()])
        interp = griddata(pts[valid], vals[valid], model_pts, method='nearest')
        
        return interp.reshape(lats_2d.shape)

def plot_family_b_runoff_irrigation(cfg, out_dir, out_dir_nc, variables_dir):
    logger.info("Plotting Family B: Total Runoff + Irrigation...")
    
    var_id = 'total_runoff'
    var_cfg_dict = load_variable(var_id, variables_dir)
    if not var_cfg_dict:
        return
        
    var_cfg = ObjDict(var_cfg_dict)
    start_year = cfg['period']['start_year']
    end_year = cfg['period']['end_year']
    ref_exp = cfg['experiments']['reference']
    da_exp = cfg['experiments']['assimilation']
    irr_threshold = cfg['parameters']['highly_irrigated_threshold_pct']
    
    fig = plt.figure(figsize=(12, 12))
    seasons = ['DJF', 'JJA']
    ims_abs = []
    ims_diff = []
    ax_abs = []
    ax_diff = []
    
    letters = [['a', 'b', 'c'], ['d', 'e', 'f']]
    
    cmap_abs, _ = _get_norm_cmap(var_cfg, diff=False, cmap_override=cfg['style']['cmap_runoff'])
    cmap_diff, _ = _get_norm_cmap(var_cfg, diff=True, cmap_override='RdBu_r')
    
    # Updated limits based on QC
    norm_abs = mcolors.Normalize(vmin=0.0, vmax=0.50)
    norm_diff = mcolors.TwoSlopeNorm(vmin=-0.50, vcenter=0.0, vmax=0.50)
    
    global_lats, global_lons = None, None
    global_land_mask = None
    
    for row, season in enumerate(seasons):
        ol_data, lon, lat = load_nc(out_dir_nc, var_id, ref_exp, season, start_year, end_year)
        da_data, _, _ = load_nc(out_dir_nc, var_id, da_exp, season, start_year, end_year)
        
        if ol_data is None or da_data is None:
            continue
            
        global_lons, global_lats = lon, lat
        if global_land_mask is None:
            global_land_mask = np.isnan(ol_data)
            
        diff_data = da_data - ol_data
        
        # 1. OL
        ax1 = get_map_axis(fig, row, 0, 3, 3)
        im1 = ax1.pcolormesh(lon, lat, ol_data, transform=ccrs.PlateCarree(), cmap=cmap_abs, norm=norm_abs, shading='auto')
        ax1.set_title(f"OL — {season}", fontweight='bold', fontsize=10)
        ax_abs.append(ax1)
        ims_abs.append(im1)
        
        # 2. DA
        ax2 = get_map_axis(fig, row, 1, 3, 3)
        im2 = ax2.pcolormesh(lon, lat, da_data, transform=ccrs.PlateCarree(), cmap=cmap_abs, norm=norm_abs, shading='auto')
        ax2.set_title(f"DA-NoCDF — {season}", fontweight='bold', fontsize=10)
        ax_abs.append(ax2)
        
        # 3. Diff
        ax3 = get_map_axis(fig, row, 2, 3, 3)
        im3 = ax3.pcolormesh(lon, lat, diff_data, transform=ccrs.PlateCarree(), cmap=cmap_diff, norm=norm_diff, shading='auto')
        ax3.set_title(f"DA-NoCDF − OL — {season}", fontweight='bold', fontsize=10)
        ax_diff.append(ax3)
        ims_diff.append(im3)
        
    if global_lats is not None:
        # Load irrigation map
        gmia_mask = load_gmia_mask(cfg['paths']['gmia_mask'], global_lats, global_lons)
        
        # Apply LIS land mask to GMIA so it doesn't show rectangular footprint
        if global_land_mask is not None:
            gmia_mask = np.where(global_land_mask, np.nan, gmia_mask)
        
        ax_irr = get_map_axis(fig, 2, 0, 3, 3)
        cmap_irr = copy.copy(plt.get_cmap('YlGn'))
        cmap_irr.set_bad('white')
        
        if global_lons.ndim == 1:
            X, Y = np.meshgrid(global_lons, global_lats)
        else:
            X, Y = global_lons, global_lats
            
        im_irr = ax_irr.pcolormesh(X, Y, gmia_mask, transform=ccrs.PlateCarree(), cmap=cmap_irr, shading='auto', vmin=0, vmax=100)
        
        # Add contour for > 30%
        ax_irr.contour(X, Y, gmia_mask, levels=[irr_threshold], colors=['red'], linewidths=0.8, transform=ccrs.PlateCarree())
        
        ax_irr.set_title("Irrigated Area % (GMIA)", fontweight='bold', fontsize=10)
        cbar_irr = fig.colorbar(im_irr, ax=ax_irr, orientation='horizontal', pad=0.08, fraction=0.06)
        cbar_irr.set_label("Irrigation Fraction (%)", fontsize=9, fontweight='bold')
        
        # Bar plot (12-month extraction)
        ax_bar = fig.add_subplot(3, 3, (2*3) + 2 + 1)
        ax_bar.set_position([ax_bar.get_position().x0 - 0.15, ax_bar.get_position().y0, 
                             0.4, ax_bar.get_position().height])
        
        high_irr_mask = (gmia_mask > irr_threshold) & ~np.isnan(gmia_mask)
        logger.info(f"High-irrigation pixels (>{irr_threshold}%): {np.sum(high_irr_mask)}")
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_diffs = []
        
        for m in range(1, 13):
            da_m, _, _ = load_nc(out_dir_nc, var_id, da_exp, f"M{m:02d}", start_year, end_year)
            ol_m, _, _ = load_nc(out_dir_nc, var_id, ref_exp, f"M{m:02d}", start_year, end_year)
            if da_m is not None and ol_m is not None:
                diff_m = (da_m - ol_m)[high_irr_mask]
                valid_diff = diff_m[~np.isnan(diff_m)]
                val = np.nanmean(valid_diff) if len(valid_diff) > 0 else 0
                logger.info(f"  Month {m:02d}: mean ΔQ = {val:.5f} mm/day (N={len(valid_diff)})")
                monthly_diffs.append(val)
            else:
                logger.warning(f"  Month {m:02d}: missing data")
                monthly_diffs.append(0)
        
        bar_colors = ['#1f77b4' if v >= 0 else '#d62728' for v in monthly_diffs]
        ax_bar.bar(months, monthly_diffs, color=bar_colors)
        ax_bar.axhline(0, color='black', linewidth=1.2)
        ax_bar.set_title(f"Δ Qtotal Climatology (Irrigation > {irr_threshold}%)", fontweight='bold', fontsize=10)
        ax_bar.set_ylabel("Δ Runoff (mm/day)", fontsize=9, fontweight='bold')
        ax_bar.grid(axis='y', alpha=0.3)
        plt.setp(ax_bar.get_xticklabels(), rotation=45, ha='right')
        
    if ims_abs:
        add_colorbar(fig, ims_abs[0], ax_abs, var_cfg.plotting.get('colorbar_label', 'Total Runoff (mm/day)'))
    if ims_diff:
        add_colorbar(fig, ims_diff[0], ax_diff, var_cfg.plotting.get('difference_label', 'Difference'), diff=True)

    plt.savefig(out_dir / f"fig_total_runoff_irrigation_{ref_exp}_vs_{da_exp}_{start_year}_{end_year}.png", dpi=cfg['style']['dpi'], bbox_inches='tight')
    plt.close(fig)


def plot_family_c_precip_runoff(cfg, out_dir, out_dir_nc, variables_dir):
    logger.info("Plotting Family C: Precip + Runoff components...")
    
    start_year = cfg['period']['start_year']
    end_year = cfg['period']['end_year']
    ref_exp = cfg['experiments']['reference']
    da_exp = cfg['experiments']['assimilation']
    
    fig = plt.figure(figsize=(16, 8))
    seasons = ['DJF', 'JJA']
    letters = [['a', 'b', 'c', 'd'], ['e', 'f', 'g', 'h']]
    
    precip_cfg = ObjDict(load_variable('precipitation', variables_dir) or {})
    runoff_cfg = ObjDict(load_variable('total_runoff', variables_dir) or {})
    
    cmap_precip, _ = _get_norm_cmap(precip_cfg, diff=False, cmap_override=cfg['style']['cmap_precip'])
    cmap_diff, _ = _get_norm_cmap(runoff_cfg, diff=True, cmap_override='RdBu_r')
    
    # Updated limits based on QC
    norm_precip = mcolors.Normalize(vmin=0.0, vmax=3.0)
    norm_diff = mcolors.TwoSlopeNorm(vmin=-0.50, vcenter=0.0, vmax=0.50)
    
    ims_diff = []
    ax_diff = []
    ax_precip = []
    im_precip = None
    
    for row, season in enumerate(seasons):
        # Precip (using Ref exp as the source)
        precip, lon, lat = load_nc(out_dir_nc, 'precipitation', ref_exp, season, start_year, end_year)
        if precip is not None:
            ax1 = get_map_axis(fig, row, 0, 2, 4)
            im1 = ax1.pcolormesh(lon, lat, precip, transform=ccrs.PlateCarree(), cmap=cmap_precip, norm=norm_precip, shading='auto')
            ax1.set_title(f"Precipitation — {season}", fontweight='bold', fontsize=10)
            ax_precip.append(ax1)
            im_precip = im1
        
        # Component differences
        components = ['total_runoff', 'surface_runoff', 'baseflow']
        comp_labels = ['Total Runoff', 'Surface Runoff', 'Baseflow']
        
        for col, (comp, label) in enumerate(zip(components, comp_labels)):
            ol_data, _, _ = load_nc(out_dir_nc, comp, ref_exp, season, start_year, end_year)
            da_data, _, _ = load_nc(out_dir_nc, comp, da_exp, season, start_year, end_year)
            
            if ol_data is None or da_data is None:
                continue
                
            diff_data = da_data - ol_data
            ax_c = get_map_axis(fig, row, col+1, 2, 4)
            im_c = ax_c.pcolormesh(lon, lat, diff_data, transform=ccrs.PlateCarree(), cmap=cmap_diff, norm=norm_diff, shading='auto')
            ax_c.set_title(f"Δ {label} — {season}", fontweight='bold', fontsize=10)
            
            ax_diff.append(ax_c)
            ims_diff.append(im_c)

    # 2 Separate Colorbars
    if im_precip and ax_precip:
        cbar1 = fig.colorbar(im_precip, ax=ax_precip, orientation='horizontal', fraction=0.04, pad=0.08, extend='max')
        cbar1.set_label("Precipitation (mm/day)", fontsize=10, fontweight='bold')
        
    if ims_diff and ax_diff:
        cbar2 = fig.colorbar(ims_diff[0], ax=ax_diff, orientation='horizontal', fraction=0.04, pad=0.08, extend='both')
        cbar2.set_label("Difference (DA-NoCDF − OL) [mm/day]", fontsize=10, fontweight='bold')
        
    plt.savefig(out_dir / f"fig_precip_runoff_components_{ref_exp}_vs_{da_exp}_{start_year}_{end_year}.png", dpi=cfg['style']['dpi'], bbox_inches='tight')
    plt.close(fig)
        

def generate_qc_report(out_dir_nc, start_year, end_year, ref_exp, da_exp):
    logger.info("\n" + "="*50 + "\n--- QC REPORT: PERCENTILES & CLOSURE ---\n" + "="*50)
    
    def print_stats(name, data, current_vmin=None, current_vmax=None):
        valid = data[~np.isnan(data)]
        if len(valid) == 0:
            logger.info(f"{name} | NO VALID DATA")
            return
            
        p01, p05, median, p95, p99 = np.percentile(valid, [1, 5, 50, 95, 99])
        min_val, max_val, mean_val = valid.min(), valid.max(), valid.mean()
        
        frac_below = np.sum(valid < current_vmin) / len(valid) * 100 if current_vmin is not None else 0.0
        frac_above = np.sum(valid > current_vmax) / len(valid) * 100 if current_vmax is not None else 0.0
            
        logger.info(f"\n{name}")
        logger.info(f"  Min: {min_val:.5f} | Max: {max_val:.5f} | Mean: {mean_val:.5f} | Median: {median:.5f}")
        logger.info(f"  P01: {p01:.5f} | P05: {p05:.5f} | P95: {p95:.5f} | P99: {p99:.5f}")
        if current_vmin is not None:
            logger.info(f"  Fraction below {current_vmin}: {frac_below:.2f}%")
            logger.info(f"  Fraction above {current_vmax}: {frac_above:.2f}%")

    for s in ['DJF', 'JJA']:
        ol_q, _, _ = load_nc(out_dir_nc, 'total_runoff', ref_exp, s, start_year, end_year)
        da_q, _, _ = load_nc(out_dir_nc, 'total_runoff', da_exp, s, start_year, end_year)
        if ol_q is not None and da_q is not None:
            print_stats(f"Total Runoff OL {s} (Current: 0 to 0.25)", ol_q, 0.0, 0.25)
            print_stats(f"Total Runoff DA-OL {s} (Current: -0.05 to 0.05)", da_q - ol_q, -0.05, 0.05)
            
        ol_sm, _, _ = load_nc(out_dir_nc, 'surface_soil_moisture', ref_exp, s, start_year, end_year)
        da_sm, _, _ = load_nc(out_dir_nc, 'surface_soil_moisture', da_exp, s, start_year, end_year)
        if ol_sm is not None and da_sm is not None:
            print_stats(f"Soil Moisture OL {s} (Current: 0.05 to 0.25)", ol_sm, 0.05, 0.25)
            print_stats(f"Soil Moisture DA-OL {s} (Current: -0.03 to 0.03)", da_sm - ol_sm, -0.03, 0.03)
            
        p, _, _ = load_nc(out_dir_nc, 'precipitation', ref_exp, s, start_year, end_year)
        if p is not None:
            print_stats(f"Precipitation {s}", p)
            
        ol_surf, _, _ = load_nc(out_dir_nc, 'surface_runoff', ref_exp, s, start_year, end_year)
        da_surf, _, _ = load_nc(out_dir_nc, 'surface_runoff', da_exp, s, start_year, end_year)
        if ol_surf is not None and da_surf is not None:
            print_stats(f"Surface Runoff DA-OL {s} (Current: -0.05 to 0.05)", da_surf - ol_surf, -0.05, 0.05)
            
        ol_base, _, _ = load_nc(out_dir_nc, 'baseflow', ref_exp, s, start_year, end_year)
        da_base, _, _ = load_nc(out_dir_nc, 'baseflow', da_exp, s, start_year, end_year)
        if ol_base is not None and da_base is not None:
            print_stats(f"Baseflow DA-OL {s} (Current: -0.05 to 0.05)", da_base - ol_base, -0.05, 0.05)
            
        if ol_q is not None and da_q is not None and ol_surf is not None and da_surf is not None and ol_base is not None and da_base is not None:
            dtot = da_q - ol_q
            dsurf = da_surf - ol_surf
            dbase = da_base - ol_base
            closure = dtot - (dsurf + dbase)
            valid_closure = closure[~np.isnan(closure)]
            logger.info(f"\n--- Closure Error {s} ---")
            logger.info(f"  Mean error: {np.mean(valid_closure):.2e}")
            logger.info(f"  Median error: {np.median(valid_closure):.2e}")
            logger.info(f"  P95 absolute error: {np.percentile(np.abs(valid_closure), 95):.2e}")
            logger.info(f"  Max absolute error: {np.max(np.abs(valid_closure)):.2e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qc-only', action='store_true', help='Only generate QC report, skip plotting')
    args = parser.parse_args()

    postproc_dir = Path("/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc")
    config_path = postproc_dir / "configs/manuscripts/hydrology_seasonal_impact.yaml"
    cfg = load_yaml(str(config_path))
    
    base_out_dir = postproc_dir / cfg['paths']['output_dir']
    manuscript_id = cfg.get('manuscript_id', 'hydrology_seasonal_impact')
    
    out_dir = base_out_dir / 'figures' / manuscript_id
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_dir_nc = base_out_dir / 'climatology_nc' / manuscript_id
    out_dir_nc.mkdir(parents=True, exist_ok=True)
    variables_dir = str(postproc_dir / 'configs' / 'variables')
    
    logger.info("--- Step 1: Compute Seasonal Climatologies ---")
    compute_seasonal_climatologies(str(config_path))
    
    if args.qc_only:
        generate_qc_report(out_dir_nc, cfg['period']['start_year'], cfg['period']['end_year'], cfg['experiments']['reference'], cfg['experiments']['assimilation'])
        return
        
    logger.info("--- Step 2: Generate Figures ---")
    plot_family_a_soil_moisture(cfg, out_dir, out_dir_nc, variables_dir)
    plot_family_b_runoff_irrigation(cfg, out_dir, out_dir_nc, variables_dir)
    plot_family_c_precip_runoff(cfg, out_dir, out_dir_nc, variables_dir)
    
    logger.info(f"Done. Outputs saved to {out_dir}")

if __name__ == "__main__":
    main()
