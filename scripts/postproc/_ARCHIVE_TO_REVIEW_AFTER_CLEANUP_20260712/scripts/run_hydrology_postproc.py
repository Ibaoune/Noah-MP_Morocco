#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: run_hydrology_postproc
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import os
import sys
import yaml
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from utils.io_lis import get_lis_files, load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask
import netCDF4 as nc

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(data, filepath):
    with open(filepath, 'w') as f:
        yaml.dump(data, f, sort_keys=False)

def check_netcdf_variables(files, possible_names):
    if not files:
        return None
    ds = nc.Dataset(files[0], 'r')
    available_vars = list(ds.variables.keys())
    ds.close()
    
    for name in possible_names:
        if name in available_vars:
            return name
            
    print(f"Error: None of the possible variables {possible_names} were found in the NetCDF files.")
    print(f"Available variables are: {available_vars}")
    sys.exit(1)

def apply_mask(data, mask):
    if data is None or mask is None:
        return None
    # mask is True for valid land pixels. data is also checked for nan
    return np.where(mask & ~np.isnan(data), data, np.nan)

def mask_invalid_values(data, log_dict):
    if data is None:
        return None
    # Mask out _FillValue, missing_value, and anything <= -9000
    if hasattr(data, 'mask'):
        valid_mask = (~data.mask) & (data > -9000) & (~np.isnan(data))
        data = data.filled(np.nan)
    else:
        valid_mask = (data > -9000) & (~np.isnan(data))
        
    invalid_count = np.sum(~valid_mask)
    log_dict['number_of_fill_values_masked'] = int(invalid_count)
    log_dict['valid_pixel_count'] = int(np.sum(valid_mask))
    
    return np.where(valid_mask, data, np.nan)

def compute_percentiles(data_list, lower=2, upper=98):
    all_data = []
    for d in data_list:
        if d is not None:
            all_data.append(d[~np.isnan(d)])
    if not all_data:
        return 0, 1
    concat_data = np.concatenate(all_data)
    if len(concat_data) == 0:
        return 0, 1
    return np.percentile(concat_data, lower), np.percentile(concat_data, upper)

def get_levels(level_cfg, data_list):
    if isinstance(level_cfg, list):
        return level_cfg
    if level_cfg == "auto_percentile":
        p_min, p_max = compute_percentiles(data_list, 2, 98)
        return np.linspace(p_min, p_max, 10).tolist()
    if level_cfg == "auto_symmetric_percentile_98":
        p_min, p_max = compute_percentiles(data_list, 2, 98)
        max_abs = max(abs(p_min), abs(p_max))
        return np.linspace(-max_abs, max_abs, 10).tolist()
    return level_cfg

def load_and_process_data(files, data_cfg, var_name, log_dict):
    if not files:
        return None
        
    mask = get_landmask(files)
    op = data_cfg.get('operation', 'none')
    multiplier = data_cfg.get('multiplier', 1.0)
    
    log_dict['operation'] = op
    log_dict['multiplier'] = multiplier
    
    # Special logic for rootzone
    if var_name == "RootMoist_tavg" or op == "weighted_mean":
        # Check if RootMoist_tavg exists
        ds = nc.Dataset(files[0], 'r')
        if "RootMoist_tavg" in ds.variables:
            ds.close()
            data = load_lis_variable(files, "RootMoist_tavg")
            log_dict['variable_used'] = "RootMoist_tavg"
            return data * multiplier
        else:
            ds.close()
            # Calculate RZSM from SoilMoist_tavg 0-1m
            print("RootMoist_tavg not found, calculating RZSM from SoilMoist_tavg layers 0, 1, 2")
            sm = load_lis_variable(files, "SoilMoist_tavg")
            if sm is None:
                return None
            weights = [0.10, 0.30, 0.60]
            rzsm = (sm[:, 0, :, :] * weights[0] + sm[:, 1, :, :] * weights[1] + sm[:, 2, :, :] * weights[2]) / sum(weights)
            log_dict['variable_used'] = "SoilMoist_tavg (layers 0,1,2 weighted)"
            return mask_invalid_values(rzsm, log_dict) * multiplier

    if op == "add":
        if "total_runoff" in var_name or "Qs_tavg" in var_name:
            qs = load_lis_variable(files, "Qs_tavg")
            qsb = load_lis_variable(files, "Qsb_tavg")
            qs = mask_invalid_values(qs, {})
            qsb = mask_invalid_values(qsb, {})
            log_dict['variable_used'] = "Qs_tavg + Qsb_tavg"
            return (qs + qsb) * multiplier

    if op == "partitioning":
        qs = load_lis_variable(files, "Qs_tavg")
        qsb = load_lis_variable(files, "Qsb_tavg")
        qs = mask_invalid_values(qs, {})
        qsb = mask_invalid_values(qsb, {})
        qs_ts = calculate_basin_average(qs, mask)
        qsb_ts = calculate_basin_average(qsb, mask)
        log_dict['variable_used'] = "Qs_tavg and Qsb_tavg"
        return {'qs_ts': qs_ts * multiplier, 'qsb_ts': qsb_ts * multiplier}

    # Standard loading
    data = load_lis_variable(files, var_name)
    if data is None:
        return None
        
    data = mask_invalid_values(data, log_dict)
        
    layer = data_cfg.get('layers', None)
    if layer is not None and isinstance(layer, int):
        if len(data.shape) > 3:
            data = data[:, layer, :, :]
            log_dict['layer'] = layer
            
    # Remove the dead code here since we moved it above

    log_dict['variable_used'] = var_name
    return data * multiplier

def get_stats(data, mask):
    if data is None:
        return {}
    if isinstance(data, dict):
        return {'note': 'partitioning dict, skipping spatial stats'}
    data_masked = apply_mask(data, mask)
    valid_data = data_masked[~np.isnan(data_masked)]
    
    if len(valid_data) == 0:
        return {'valid_pixels': 0}
        
    stats = {
        'min': float(np.min(valid_data)),
        'max': float(np.max(valid_data)),
        'mean': float(np.mean(valid_data)),
        'median': float(np.median(valid_data)),
        'valid_pixels': int(len(valid_data)),
        'percentiles': {
            'p2': float(np.percentile(valid_data, 2)),
            'p5': float(np.percentile(valid_data, 5)),
            'p50': float(np.percentile(valid_data, 50)),
            'p95': float(np.percentile(valid_data, 95)),
            'p98': float(np.percentile(valid_data, 98)),
            'p99': float(np.percentile(valid_data, 99))
        },
        'pixel_counts_gt_threshold': {
            'gt_0.001': int(np.sum(valid_data > 0.001)),
            'gt_0.01': int(np.sum(valid_data > 0.01)),
            'gt_0.05': int(np.sum(valid_data > 0.05)),
            'gt_0.10': int(np.sum(valid_data > 0.10))
        }
    }
    return stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--dry-run", action="store_true", help="Do not generate figures, only validate")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    var_name_cfg = cfg['variable']['name']
    period = str(cfg['variable']['period'])
    out_dir = cfg['paths']['output_dir']
    
    os.makedirs(out_dir, exist_ok=True)
    
    start_date = datetime.strptime(f"{period}-01-01", "%Y-%m-%d")
    end_date = datetime.strptime(f"{period}-12-31", "%Y-%m-%d")
    
    print(f"--- Processing {var_name_cfg} ---")
    if args.dry_run:
        print("DRY RUN MODE: No figures will be saved.")

    processing_log = {
        'config_file': args.config,
        'variable': var_name_cfg,
        'period': period,
        'experiments': {}
    }

    # Load data for experiments
    data_cache = {}
    mask = None
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    for exp_key, exp_cfg in cfg['experiments'].items():
        rel_path = exp_cfg.get('path', '')
        search_path = os.path.join(project_root, rel_path)
        
        files = get_lis_files(search_path, start_date, end_date)
        if not files:
            print(f"Warning: No files found for {exp_key} in {search_path}")
            continue
            
        if cfg['data'].get('operation') == 'partitioning':
            actual_var = "partitioning"
        else:
            actual_var = check_netcdf_variables(files, cfg['data']['possible_names'])
        
        log_exp = {'files_found': len(files)}
        data = load_and_process_data(files, cfg['data'], actual_var, log_exp)
        
        if data is not None:
            data_cache[exp_key] = data
            if mask is None:
                mask = get_landmask(files)
            log_exp['stats'] = get_stats(data, mask)
        
        processing_log['experiments'][exp_key] = log_exp

    if args.dry_run:
        print("\nDry-run validation successful.")
        print("Variables detected and data loaded correctly.")
        print(yaml.dump(processing_log))
        sys.exit(0)

    # Plot Annual Mean
    vis_am = cfg['visual'].get('annual_mean', {})
    if vis_am.get('enabled', False):
        fig_name = f"01_{var_name_cfg}_annual_mean_{period}"
        out_path = os.path.join(out_dir, fig_name)
        
        fig, axes = plt.subplots(1, 3, figsize=tuple(cfg['visual']['style']['maps']['figsize']))
        
        exp_keys = ['opl', 'da_smap_nocdf', 'da_smap_cdf']
        mean_data = []
        for ek in exp_keys:
            if ek in data_cache:
                mean_data.append(np.nanmean(data_cache[ek], axis=0))
            else:
                mean_data.append(None)
                
        levels = get_levels(vis_am['colorbar']['levels'], mean_data)
        processing_log['annual_mean_levels_used'] = levels
        
        cmap = plt.get_cmap(vis_am['cmap']['name'])(np.linspace(0.1, 1, len(levels) - 1))
        cmap = mcolors.ListedColormap(cmap)
        cmap.set_bad(color=vis_am['cmap']['bad_color'])
        norm = mcolors.BoundaryNorm(levels, cmap.N)
        
        im = None
        for ax, data, title in zip(axes, mean_data, vis_am['panel_titles']):
            if data is not None:
                ax.imshow(apply_mask(data, mask), cmap=cmap, norm=norm, origin='lower', interpolation='nearest')
                im = ax.images[0]
            ax.contour(mask, levels=[0.5], colors=['#404040'], linewidths=[0.4], alpha=0.8)
            ax.set_title(title, fontsize=cfg['visual']['style']['fonts']['panel_title_size'])
            if cfg['visual']['style']['maps']['axis_off']:
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
        if im is not None:
            fig.subplots_adjust(left=0.02, right=0.88, top=0.82, bottom=0.08, wspace=cfg['visual']['style']['maps']['wspace'])
            cbar_ax = fig.add_axes([0.90, 0.22, 0.015, 0.55])
            cbar = fig.colorbar(im, cax=cbar_ax, extend=vis_am['cmap'].get('extend', 'neither'))
            cbar.set_label(vis_am['colorbar']['label'], fontsize=cfg['visual']['style']['fonts']['colorbar_label_size'])
            if 'ticks' in vis_am['colorbar']:
                cbar.set_ticks(vis_am['colorbar']['ticks'])
            cbar.ax.tick_params(labelsize=cfg['visual']['style']['fonts']['colorbar_tick_size'])

        plt.suptitle(vis_am['title'], fontsize=cfg['visual']['style']['fonts']['main_title_size'], y=0.98)
        
        for fmt in cfg['visual']['style']['figure']['formats']:
            plt.savefig(f"{out_path}.{fmt}", dpi=cfg['visual']['style']['figure']['dpi'], bbox_inches=cfg['visual']['style']['figure']['bbox_inches'])
        plt.close()

    # Plot Differences
    vis_diff = cfg['visual'].get('differences', {})
    if vis_diff.get('enabled', False):
        fig_name = f"02_{var_name_cfg}_differences_{period}"
        out_path = os.path.join(out_dir, fig_name)
        
        fig, axes = plt.subplots(1, 3, figsize=tuple(cfg['visual']['style']['maps']['figsize']))
        
        diff_data = []
        titles = []
        for comp in vis_diff['comparisons']:
            ea = comp['experiment_a']
            eb = comp['experiment_b']
            titles.append(comp['label'])
            if ea in data_cache and eb in data_cache:
                diff_data.append(np.nanmean(data_cache[ea] - data_cache[eb], axis=0))
            else:
                diff_data.append(None)
                
        levels = get_levels(vis_diff['colorbar']['levels'], diff_data)
        processing_log['differences_levels_used'] = levels
        processing_log['differences_stats'] = {}
        
        colors_diff = plt.get_cmap(vis_diff['cmap']['name'], 256)(np.linspace(0, 1, len(levels) - 1))
        # Find middle bin to set neutral color
        mid_idx = len(levels) // 2 - 1
        colors_diff[mid_idx] = mcolors.to_rgba(vis_diff['cmap']['neutral_color'])
        cmap_diff = mcolors.ListedColormap(colors_diff)
        cmap_diff.set_bad(color=vis_diff['cmap']['bad_color'])
        norm_diff = mcolors.BoundaryNorm(levels, cmap_diff.N)

        im = None
        for ax, data, title in zip(axes, diff_data, titles):
            if data is not None:
                data_masked = apply_mask(data, mask)
                ax.imshow(data_masked, cmap=cmap_diff, norm=norm_diff, origin='lower', interpolation='nearest')
                im = ax.images[0]
            ax.contour(mask, levels=[0.5], colors=['#404040'], linewidths=[0.4], alpha=0.8)
                
            if data is not None:
                if vis_diff.get('statistics_box', {}).get('enabled', False):
                    mean_val = np.nanmean(data_masked)
                    median_val = np.nanmedian(data_masked)
                    
                    thresh_cfg = vis_diff['statistics_box'].get('threshold', [0.005])
                    thresholds = thresh_cfg if isinstance(thresh_cfg, list) else [thresh_cfg]
                    
                    log_stats = {'mean': float(mean_val), 'median': float(median_val)}
                    
                    text_lines = [f"Mean Δ: {mean_val:.3f}", f"Median Δ: {median_val:.3f}"]
                    # We compute all requested thresholds for logging, but we can limit display
                    display_thresholds = vis_diff['statistics_box'].get('display_thresholds', thresholds)
                    
                    all_thresholds_to_calc = set(thresholds) | set(display_thresholds) | {0.005, 0.05}
                    for thresh in sorted(list(all_thresholds_to_calc)):
                        pct_area = np.nansum(np.abs(data_masked) > thresh) / np.nansum(~np.isnan(data_masked)) * 100.0
                        log_stats[f"pct_area_gt_{thresh}"] = float(pct_area)
                        if thresh in display_thresholds:
                            text_lines.append(f"|Δ| > {thresh}: {pct_area:.1f}%")
                            
                    processing_log['differences_stats'][comp['name']] = log_stats
                    
                    textstr = "\n".join(text_lines)
                    props = dict(boxstyle='round', facecolor='white', alpha=vis_diff['statistics_box'].get('alpha', 0.8), edgecolor='lightgrey')
                    ax.text(0.03, 0.96, textstr, transform=ax.transAxes, fontsize=vis_diff['statistics_box']['fontsize'],
                            verticalalignment='top', bbox=props)
                            
            ax.set_title(title, fontsize=cfg['visual']['style']['fonts']['panel_title_size'])
            if cfg['visual']['style']['maps']['axis_off']:
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

        if im is not None:
            fig.subplots_adjust(left=0.02, right=0.88, top=0.82, bottom=0.08, wspace=cfg['visual']['style']['maps']['wspace'])
            cbar_ax = fig.add_axes([0.90, 0.22, 0.015, 0.55])
            cbar = fig.colorbar(im, cax=cbar_ax, extend=vis_diff['cmap'].get('extend', 'neither'))
            cbar.set_label(vis_diff['colorbar']['label'], fontsize=cfg['visual']['style']['fonts']['colorbar_label_size'])
            if 'ticks' in vis_diff['colorbar']:
                cbar.set_ticks(vis_diff['colorbar']['ticks'])
            cbar.ax.tick_params(labelsize=cfg['visual']['style']['fonts']['colorbar_tick_size'])

        plt.suptitle(vis_diff['title'], fontsize=cfg['visual']['style']['fonts']['main_title_size'], y=0.98)
        
        for fmt in cfg['visual']['style']['figure']['formats']:
            plt.savefig(f"{out_path}.{fmt}", dpi=cfg['visual']['style']['figure']['dpi'], bbox_inches=cfg['visual']['style']['figure']['bbox_inches'])
        plt.close()

    # Plot Timeseries
    vis_ts = cfg['visual'].get('domain_mean_timeseries', {})
    if vis_ts.get('enabled', False):
        fig_name = f"03_{var_name_cfg}_domain_mean_timeseries_{period}"
        out_path = os.path.join(out_dir, fig_name)
        
        has_anom = vis_ts.get('anomalies_panel', {}).get('enabled', False)
        
        if has_anom:
            fig, axes = plt.subplots(2, 1, figsize=tuple(cfg['visual']['style']['timeseries']['figsize']), gridspec_kw={'height_ratios': [2.5, 1]}, sharex=True)
            ax_main = axes[0]
            ax_anom = axes[1]
        else:
            fig, ax_main = plt.subplots(1, 1, figsize=tuple(cfg['visual']['style']['timeseries']['figsize']))
            ax_anom = None
            
        ts_cache = {}
        plot_abs = vis_ts.get('plot_absolute', True)
        plot_rel = vis_ts.get('plot_relative_to_initial', False)
        
        for ek in ['opl', 'da_smap_nocdf', 'da_smap_cdf']:
            if ek in data_cache:
                ts = calculate_basin_average(data_cache[ek], mask)
                ts_cache[ek] = ts
                dates = [start_date + timedelta(days=i) for i in range(len(ts))]
                exp_cfg = cfg['experiments'][ek]
                
                if plot_rel:
                    plot_data = ts - ts[0]
                else:
                    plot_data = ts
                    
                ax_main.plot(dates, plot_data, label=exp_cfg['label'], color=exp_cfg['color'], 
                             linestyle=exp_cfg.get('linestyle', '-'), linewidth=exp_cfg.get('linewidth', 2.0))
                             
        ax_main.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 3, 5, 7, 9, 11)))
        ax_main.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                             
        if 'limits' in vis_ts['yaxis']:
            ax_main.set_ylim(vis_ts['yaxis']['limits'])
        ax_main.set_title(vis_ts['title'], fontsize=cfg['visual']['style']['fonts']['main_title_size'])
        ax_main.set_ylabel(vis_ts['yaxis']['label'], fontsize=cfg['visual']['style']['fonts']['axis_label_size'])
        if 'ticks' in vis_ts['yaxis']:
            ax_main.set_yticks(vis_ts['yaxis']['ticks'])
        ax_main.tick_params(axis='both', which='major', labelsize=cfg['visual']['style']['fonts']['tick_label_size'])
        
        if cfg['visual']['style']['timeseries']['grid']:
            ax_main.grid(True, color=cfg['visual']['style']['timeseries']['grid_color'], alpha=cfg['visual']['style']['timeseries']['grid_alpha'])
            
        ax_main.legend(loc=cfg['visual']['style']['timeseries']['legend_location'].replace('_', ' '),
                       frameon=cfg['visual']['style']['timeseries']['legend_frame'],
                       framealpha=cfg['visual']['style']['timeseries']['legend_alpha'],
                       fontsize=cfg['visual']['style']['fonts']['legend_size'])
                       
        if has_anom:
            for comp in vis_ts['anomalies_panel']['comparisons']:
                ea = comp['experiment_a']
                eb = comp['experiment_b']
                if ea in ts_cache and eb in ts_cache:
                    ax_anom.plot(dates, ts_cache[ea] - ts_cache[eb], label=comp['label'], color=cfg['experiments'][ea]['color'], linewidth=1.5)
            
            if vis_ts['anomalies_panel'].get('zero_line', True):
                ax_anom.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            ax_anom.set_ylabel(vis_ts['anomalies_panel']['ylabel'], fontsize=cfg['visual']['style']['fonts']['axis_label_size'])
            ax_anom.tick_params(axis='both', which='major', labelsize=cfg['visual']['style']['fonts']['tick_label_size'])
            if 'yaxis' in vis_ts['anomalies_panel']:
                if 'limits' in vis_ts['anomalies_panel']['yaxis']:
                    ax_anom.set_ylim(vis_ts['anomalies_panel']['yaxis']['limits'])
                if 'ticks' in vis_ts['anomalies_panel']['yaxis']:
                    ax_anom.set_yticks(vis_ts['anomalies_panel']['yaxis']['ticks'])
            if cfg['visual']['style']['timeseries']['grid']:
                ax_anom.grid(True, color=cfg['visual']['style']['timeseries']['grid_color'], alpha=cfg['visual']['style']['timeseries']['grid_alpha'])
                
        plt.tight_layout()
        for fmt in cfg['visual']['style']['figure']['formats']:
            plt.savefig(f"{out_path}.{fmt}", dpi=cfg['visual']['style']['figure']['dpi'], bbox_inches=cfg['visual']['style']['figure']['bbox_inches'])
        plt.close()

    # Plot Runoff Partitioning
    vis_part = cfg['visual'].get('runoff_partitioning', {})
    if vis_part.get('enabled', False):
        fig_name = f"04_runoff_partitioning_monthly_{period}"
        out_path = os.path.join(out_dir, fig_name)
        
        fig_name_frac = f"05_runoff_partitioning_fraction_monthly_{period}"
        out_path_frac = os.path.join(out_dir, fig_name_frac)
        
        fig, axes = plt.subplots(1, 3, figsize=tuple(vis_part['layout']['figsize']), sharey=vis_part['layout']['sharey'])
        fig_frac, axes_frac = plt.subplots(1, 3, figsize=tuple(vis_part['layout']['figsize']), sharey=vis_part['layout']['sharey'])
        
        # Monthly aggregation
        months_labels = vis_part['xaxis']['labels']
        
        for ax, ax_frac, ek, title in zip(axes, axes_frac, ['opl', 'da_smap_nocdf', 'da_smap_cdf'], vis_part['panel_titles']):
            if ek in data_cache and isinstance(data_cache[ek], dict):
                qs_ts = data_cache[ek]['qs_ts']
                qsb_ts = data_cache[ek]['qsb_ts']
                
                # Group by month
                monthly_qs = np.zeros(12)
                monthly_qsb = np.zeros(12)
                for i in range(len(qs_ts)):
                    m = (start_date + timedelta(days=i)).month - 1
                    monthly_qs[m] += qs_ts[i]
                    monthly_qsb[m] += qsb_ts[i]
                    
                total_m = monthly_qs + monthly_qsb
                x = np.arange(12)
                
                # Absolute bar plot
                ax.bar(x, monthly_qsb, label=vis_part['components']['baseflow']['label'], 
                       color=vis_part['components']['baseflow']['color'],
                       edgecolor=vis_part['components']['baseflow']['edgecolor'],
                       linewidth=vis_part['components']['baseflow']['linewidth'])
                ax.bar(x, monthly_qs, bottom=monthly_qsb, label=vis_part['components']['surface_runoff']['label'],
                       color=vis_part['components']['surface_runoff']['color'],
                       edgecolor=vis_part['components']['surface_runoff']['edgecolor'],
                       linewidth=vis_part['components']['surface_runoff']['linewidth'])
                       
                if vis_part['total_line']['enabled']:
                    ax.plot(x, total_m, label=vis_part['total_line']['label'],
                            color=vis_part['total_line']['color'],
                            linewidth=vis_part['total_line']['linewidth'],
                            marker=vis_part['total_line']['marker'],
                            markersize=vis_part['total_line']['markersize'])
                            
                ax.set_title(title, fontsize=cfg['visual']['style']['fonts']['panel_title_size'])
                ax.set_xticks(x)
                ax.set_xticklabels(months_labels, rotation=vis_part['xaxis']['rotation'], ha='right', fontsize=cfg['visual']['style']['fonts']['tick_label_size'])
                
                if 'limits' in vis_part.get('yaxis', {}):
                    ax.set_ylim(vis_part['yaxis']['limits'])
                if 'ticks' in vis_part.get('yaxis', {}):
                    ax.set_yticks(vis_part['yaxis']['ticks'])
                    
                if vis_part['layout'].get('grid_axis'):
                    ax.grid(axis=vis_part['layout']['grid_axis'], color='lightgray', alpha=vis_part['layout']['grid_alpha'], linewidth=0.5)
                    
                # Annotations
                ann_str = ""
                ann_total = np.sum(total_m)
                if vis_part['annotations'].get('annual_total'):
                    ann_str += f"Annual total: {ann_total:.1f} mm\n"
                if vis_part['annotations'].get('baseflow_index'):
                    bfi = np.sum(monthly_qsb) / ann_total * 100 if ann_total > 0 else 0
                    ann_str += f"BFI: {bfi:.0f}%"
                    
                if ann_str:
                    props = dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='lightgrey')
                    ax.text(0.05, 0.95, ann_str.strip(), transform=ax.transAxes, fontsize=vis_part['annotations']['fontsize'],
                            verticalalignment='top', bbox=props)
                            
                # Logging
                processing_log['experiments'][ek]['annual_qs'] = float(np.sum(monthly_qs))
                processing_log['experiments'][ek]['annual_qsb'] = float(np.sum(monthly_qsb))
                processing_log['experiments'][ek]['annual_total'] = float(ann_total)
                processing_log['experiments'][ek]['bfi'] = float(np.sum(monthly_qsb) / ann_total if ann_total > 0 else 0)
                processing_log['experiments'][ek]['monthly_qs'] = monthly_qs.tolist()
                processing_log['experiments'][ek]['monthly_qsb'] = monthly_qsb.tolist()
                
                # Fraction bar plot
                frac_qs = np.zeros_like(monthly_qs)
                frac_qsb = np.zeros_like(monthly_qsb)
                for i in range(12):
                    if total_m[i] > 0:
                        frac_qs[i] = monthly_qs[i] / total_m[i] * 100
                        frac_qsb[i] = monthly_qsb[i] / total_m[i] * 100
                
                ax_frac.bar(x, frac_qsb, label=vis_part['components']['baseflow']['label'], 
                       color=vis_part['components']['baseflow']['color'],
                       edgecolor=vis_part['components']['baseflow']['edgecolor'],
                       linewidth=vis_part['components']['baseflow']['linewidth'])
                ax_frac.bar(x, frac_qs, bottom=frac_qsb, label=vis_part['components']['surface_runoff']['label'],
                       color=vis_part['components']['surface_runoff']['color'],
                       edgecolor=vis_part['components']['surface_runoff']['edgecolor'],
                       linewidth=vis_part['components']['surface_runoff']['linewidth'])
                       
                ax_frac.set_title(title, fontsize=cfg['visual']['style']['fonts']['panel_title_size'])
                ax_frac.set_xticks(x)
                ax_frac.set_xticklabels(months_labels, rotation=vis_part['xaxis']['rotation'], ha='right', fontsize=cfg['visual']['style']['fonts']['tick_label_size'])
                ax_frac.set_ylim([0, 100])
                ax_frac.set_yticks([0, 25, 50, 75, 100])
                if vis_part['layout'].get('grid_axis'):
                    ax_frac.grid(axis=vis_part['layout']['grid_axis'], color='lightgray', alpha=vis_part['layout']['grid_alpha'], linewidth=0.5)

        axes[0].set_ylabel(vis_part['yaxis']['label'], fontsize=cfg['visual']['style']['fonts']['axis_label_size'])
        axes_frac[0].set_ylabel("Runoff contribution (%)", fontsize=cfg['visual']['style']['fonts']['axis_label_size'])
        
        # Absolute Legend
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc=vis_part['layout']['legend_location'].replace('_', ' '), 
                   ncol=vis_part['layout']['legend_ncol'], frameon=True, framealpha=0.9,
                   bbox_to_anchor=(0.5, 0.98), fontsize=cfg['visual']['style']['fonts']['legend_size'])
                   
        fig.suptitle(vis_part['title'], fontsize=cfg['visual']['style']['fonts']['main_title_size'], y=1.05)
        fig.subplots_adjust(wspace=vis_part['layout']['wspace'], top=0.85)
        for fmt in cfg['visual']['style']['figure']['formats']:
            fig.savefig(f"{out_path}.{fmt}", dpi=cfg['visual']['style']['figure']['dpi'], bbox_inches=cfg['visual']['style']['figure']['bbox_inches'])
        
        # Fraction Legend
        handles_frac, labels_frac = axes_frac[0].get_legend_handles_labels()
        fig_frac.legend(handles_frac, labels_frac, loc=vis_part['layout']['legend_location'].replace('_', ' '), 
                   ncol=2, frameon=True, framealpha=0.9,
                   bbox_to_anchor=(0.5, 0.98), fontsize=cfg['visual']['style']['fonts']['legend_size'])
                   
        fig_frac.suptitle(vis_part['title'].replace("Monthly runoff partitioning", "Monthly runoff partitioning fraction"), fontsize=cfg['visual']['style']['fonts']['main_title_size'], y=1.05)
        fig_frac.subplots_adjust(wspace=vis_part['layout']['wspace'], top=0.85)
        for fmt in cfg['visual']['style']['figure']['formats']:
            fig_frac.savefig(f"{out_path_frac}.{fmt}", dpi=cfg['visual']['style']['figure']['dpi'], bbox_inches=cfg['visual']['style']['figure']['bbox_inches'])
            
        plt.close(fig)
        plt.close(fig_frac)

    # Save Logs
    save_yaml(processing_log, os.path.join(out_dir, "processing_log.yaml"))
    save_yaml(cfg, os.path.join(out_dir, "resolved_config.yaml"))
    print(f"Done processing {var_name_cfg}. Logs saved.")

if __name__ == "__main__":
    main()
