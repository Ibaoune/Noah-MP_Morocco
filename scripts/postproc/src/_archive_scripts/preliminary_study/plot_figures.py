import os
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from utils_eval import load_lis_variable, calculate_basin_average

def _get_lat_lon(files):
    if not files: return None, None
    import netCDF4 as nc
    try:
        ds = nc.Dataset(files[0], 'r')
        lat = ds.variables['lat'][:]
        lon = ds.variables['lon'][:]
        ds.close()
        return lat, lon
    except:
        return None, None

def _get_landmask(files):
    if not files: return None
    import netCDF4 as nc
    try:
        ds = nc.Dataset(files[0], 'r')
        if 'SoilMoist_tavg' in ds.variables:
            var_data = ds.variables['SoilMoist_tavg']
            if len(var_data.shape) == 4:
                sm = var_data[0, 0, :, :]
            else:
                sm = var_data[0, :, :]
            mask = np.where(sm > -9000, 1, 0)
        else:
            mask = np.ones(ds.variables['lat'].shape)
        ds.close()
        return mask
    except Exception as e:
        print(f"Error getting landmask: {e}")
        return None

def plot_fig1_assimilation_diagnostics(config, out_dir, log_warnings, data_dict):
    """
    Figure 1: SMAP assimilation diagnostics
    """
    print("Generating Figure 1: Assimilation Diagnostics...")
    files_cdf = data_dict.get('files_da_cdf', [])
    if not files_cdf:
        log_warnings.append("Fig 1: No DA_cdf files found.")
        return None
        
    lat, lon = _get_lat_lon(files_cdf)
    if lat is None: return None
    
    # Base directory for EnKF
    # The SURFACEMODEL files are like: .../output/2016-01/SURFACEMODEL/201601/LIS_HIST_...
    # The EnKF files are like: .../output/2016-01/EnKF/201601/LIS_DA_EnKF_..._innov.a01.d01.nc
    import glob
    import netCDF4 as nc
    import calendar
    from datetime import timedelta
    
    # We reconstruct the base directory (e.g. experiments/NorthMor/matrix_2016/DA_cdf_noirr_2016/output)
    # files_cdf[0] looks like: /path/to/.../output/2016-01/SURFACEMODEL/201601/LIS_HIST...
    base_dir_da = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(files_cdf[0]))))
    
    grid_shape = (len(lat), len(lon))
    innov_sum = np.zeros(grid_shape)
    ninnov_sum = np.zeros(grid_shape)
    incr_sum = np.zeros(grid_shape)
    counts_innov = np.zeros(grid_shape)
    counts_incr = np.zeros(grid_shape)
    
    monthly_counts = {}
    
    curr_date = data_dict['start_date']
    end_date = data_dict['end_date']
    
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        # Find innov and incr files for this month
        innov_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
        incr_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_incr.a01.d01.nc"))
        
        monthly_count = 0
        
        for f in innov_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'ninnov_01' in ds.variables:
                    n = ds.variables['ninnov_01'][:]
                    valid_n = np.where(n > -9000, n, 0)
                    ninnov_sum += valid_n
                    monthly_count += np.sum(valid_n)
                if 'innov_01' in ds.variables:
                    inv = ds.variables['innov_01'][:]
                    valid_inv = np.where(inv > -9000, inv, 0)
                    mask_inv = np.where(inv > -9000, 1, 0)
                    innov_sum += valid_inv
                    counts_innov += mask_inv
                ds.close()
            except:
                pass
                
        for f in incr_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'anlys_incr_Soil Moisture Layer 1_01' in ds.variables:
                    inc = ds.variables['anlys_incr_Soil Moisture Layer 1_01'][:]
                    valid_inc = np.where(inc > -9000, inc, 0)
                    mask_inc = np.where(inc > -9000, 1, 0)
                    incr_sum += valid_inc
                    counts_incr += mask_inc
                ds.close()
            except:
                pass
                
        month_label = curr_date.strftime("%Y-%m")
        if month_label not in monthly_counts:
            monthly_counts[month_label] = 0
        monthly_counts[month_label] += monthly_count
        
        # Advance month
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    mean_innov = np.where(counts_innov > 0, innov_sum / counts_innov, np.nan)
    mean_incr = np.where(counts_incr > 0, incr_sum / counts_incr, np.nan)
    sum_ninnov = np.where(counts_innov > 0, counts_innov, np.nan)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Figure 1 - SMAP Assimilation Diagnostics (Jan-Jun 2016)", fontsize=16)
    
    # 1. Spatial Coverage (ninnov_sum)
    ax1 = axes[0, 0]
    ax1 = plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
    pcm1 = _plot_map_diff(ax1, sum_ninnov, lat, lon, "Total Assimilated Obs", 0, np.nanmax(sum_ninnov), 'viridis')
    if pcm1: plt.colorbar(pcm1, ax=ax1, orientation='horizontal', pad=0.05)
    
    # 2. Mean Innovation
    ax2 = axes[0, 1]
    ax2 = plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
    vmax = max(0.01, np.nanmax(np.abs(mean_innov))) if not np.all(np.isnan(mean_innov)) else 0.05
    pcm2 = _plot_map_diff(ax2, mean_innov, lat, lon, "Mean Innovation (Obs - Forecast)", -vmax, vmax, 'RdBu')
    if pcm2: plt.colorbar(pcm2, ax=ax2, orientation='horizontal', pad=0.05)
    
    # 3. Mean Increment
    ax3 = axes[1, 0]
    ax3 = plt.subplot(2, 2, 3, projection=ccrs.PlateCarree())
    vmax = max(0.01, np.nanmax(np.abs(mean_incr))) if not np.all(np.isnan(mean_incr)) else 0.05
    pcm3 = _plot_map_diff(ax3, mean_incr, lat, lon, "Mean Increment (Analysis - Forecast)", -vmax, vmax, 'RdBu')
    if pcm3: plt.colorbar(pcm3, ax=ax3, orientation='horizontal', pad=0.05)
    
    # 4. Monthly Counts
    ax4 = axes[1, 1]
    months = list(monthly_counts.keys())
    counts = [monthly_counts[m] for m in months]
    ax4.bar(months, counts, color='steelblue')
    ax4.set_title("Monthly Total Assimilated Obs")
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_file = os.path.join(out_dir, "fig01_assimilation_diagnostics_2016." + config['features']['figure_format'])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file

def _plot_map_diff(ax, diff_data, lat, lon, title, vmin, vmax, cmap):
    if diff_data is None: return
    # Mask invalid data
    valid_data = np.ma.masked_where(diff_data < -9000, diff_data)
    pcm = ax.pcolormesh(lon, lat, valid_data, cmap=cmap, vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_title(title, fontsize=10)
    return pcm

def plot_fig2_cdf_sensitivity(config, out_dir, log_warnings, data_dict):
    """
    Figure 2: Sensibilite CDF vs no-CDF
    """
    print("Generating Figure 2: CDF vs no-CDF Sensitivity...")
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    lat, lon = _get_lat_lon(files_ol)
    if lat is None:
        log_warnings.append("Fig 2: Could not load lat/lon coordinates.")
        return None
        
    variables_to_plot = {
        'SoilMoist_tavg': {'layer': 0, 'vmax': 0.05, 'cmap': 'RdBu', 'name': 'Surface SM (m3/m3)', 'mult': 1.0},
        'Evap_tavg': {'layer': None, 'vmax': 1.0, 'cmap': 'RdBu', 'name': 'ET (mm/day)', 'mult': 86400.0},
        'Qs_tavg': {'layer': None, 'vmax': 0.5, 'cmap': 'RdBu', 'name': 'Surface Runoff (mm/day)', 'mult': 86400.0}
    }
    
    fig, axes = plt.subplots(len(variables_to_plot), 3, figsize=(12, 4*len(variables_to_plot)), subplot_kw={'projection': ccrs.PlateCarree()})
    fig.suptitle("Figure 2 - Sensibilité CDF vs no-CDF (Jan-Jun 2016)", fontsize=16)
    
    for i, (var, meta) in enumerate(variables_to_plot.items()):
        layer = meta['layer']
        # Load and mean
        ol_data = load_lis_variable(files_ol, var, extract_layer=layer)
        nocdf_data = load_lis_variable(files_nocdf, var, extract_layer=layer)
        cdf_data = load_lis_variable(files_cdf, var, extract_layer=layer)
        
        if ol_data is None or nocdf_data is None or cdf_data is None:
            log_warnings.append(f"Fig 2: Variable {var} missing from some experiments.")
            continue
            
        ol_data = ol_data * meta['mult']
        nocdf_data = nocdf_data * meta['mult']
        cdf_data = cdf_data * meta['mult']
        
        ol_mean = np.nanmean(np.where(ol_data > -9000, ol_data, np.nan), axis=0)
        nocdf_mean = np.nanmean(np.where(nocdf_data > -9000, nocdf_data, np.nan), axis=0)
        cdf_mean = np.nanmean(np.where(cdf_data > -9000, cdf_data, np.nan), axis=0)
        
        diff1 = nocdf_mean - ol_mean
        diff2 = cdf_mean - ol_mean
        diff3 = nocdf_mean - cdf_mean
        
        pcm1 = _plot_map_diff(axes[i, 0], diff1, lat, lon, f"DA_nocdf - OPL\n{meta['name']}", -meta['vmax'], meta['vmax'], meta['cmap'])
        pcm2 = _plot_map_diff(axes[i, 1], diff2, lat, lon, f"DA_cdf - OPL\n{meta['name']}", -meta['vmax'], meta['vmax'], meta['cmap'])
        pcm3 = _plot_map_diff(axes[i, 2], diff3, lat, lon, f"DA_nocdf - DA_cdf\n{meta['name']}", -meta['vmax'], meta['vmax'], meta['cmap'])
        
        if pcm1: plt.colorbar(pcm1, ax=axes[i, :], orientation='horizontal', pad=0.05, fraction=0.05)
        
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    out_file = os.path.join(out_dir, "fig02_cdf_sensitivity_2016." + config['features']['figure_format'])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file

def plot_fig3_vertical_propagation(config, out_dir, log_warnings, data_dict):
    """
    Figure 3: Propagation verticale et cohérence flux de surface
    """
    print("Generating Figure 3: Vertical Propagation & Surface Fluxes...")
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    mask = _get_landmask(files_ol)
    
    variables = {
        'Surface SM (m3/m3)': ('SoilMoist_tavg', 0, 1.0),
        'Root Zone SM (m3/m3)': ('SoilMoist_tavg', 1, 1.0),
        'Evapotranspiration (mm/day)': ('Evap_tavg', None, 86400.0)
    }
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle("Figure 3 - Vertical Propagation & Surface Flux Coherence (Jan-Jun 2016)", fontsize=16)
    
    for i, (title, (var, layer, mult)) in enumerate(variables.items()):
        ax = axes[i]
        for exp_name, flist, color in [('OPL', files_ol, 'black'), ('DA_nocdf', files_nocdf, 'blue'), ('DA_cdf', files_cdf, 'red')]:
            data = load_lis_variable(flist, var, extract_layer=layer)
            if data is not None:
                data = data * mult
                ts = calculate_basin_average(data, mask)
                ax.plot(ts, label=exp_name, color=color)
            else:
                log_warnings.append(f"Fig 3: {var} missing for {exp_name}")
        ax.set_title(f"{title} (Basin Average)")
        ax.legend()
        ax.grid(True)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_file = os.path.join(out_dir, "fig03_vertical_propagation_et_2016." + config['features']['figure_format'])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file

def plot_fig4_runoff_partitioning(config, out_dir, log_warnings, data_dict):
    """
    Figure 4: Impact sur runoff partitioning
    """
    print("Generating Figure 4: Runoff Partitioning...")
    # Time series of basin averages for Runoff
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    mask = _get_landmask(files_ol)
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle("Figure 4 - Runoff Partitioning (Jan-Jun 2016)", fontsize=16)
    
    variables = {'Surface Runoff (Qs) [mm/day]': 'Qs_tavg', 'Baseflow (Qsb) [mm/day]': 'Qsb_tavg'}
    
    for i, (title, var) in enumerate(variables.items()):
        ax = axes[i]
        for exp_name, flist, color in [('OPL', files_ol, 'black'), ('DA_nocdf', files_nocdf, 'blue'), ('DA_cdf', files_cdf, 'red')]:
            data = load_lis_variable(flist, var, extract_layer=None)
            if data is not None:
                data = data * 86400.0
                ts = calculate_basin_average(data, mask)
                ax.plot(ts, label=exp_name, color=color)
            else:
                log_warnings.append(f"Fig 4: {var} missing for {exp_name}")
        ax.set_title(f"{title} (Basin Average)")
        ax.legend()
        ax.grid(True)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_file = os.path.join(out_dir, "fig04_runoff_partitioning_2016." + config['features']['figure_format'])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file

def plot_fig5_hymap_streamflow(config, out_dir, log_warnings, data_dict):
    if not config['features'].get('evaluate_hymap', False):
        return None
    
    print("Generating Figure 5: HyMAP Streamflow...")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle("Figure 5 - HyMAP Streamflow Evaluation", fontsize=16)
    ax.text(0.5, 0.5, 'HyMAP streamflow routing data not implemented in script yet', ha='center', va='center')
    plt.tight_layout()
    out_file = os.path.join(out_dir, "fig05_hymap_streamflow_2016." + config['features']['figure_format'])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file
