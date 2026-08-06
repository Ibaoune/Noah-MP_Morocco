# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: lis_postproc.diagnostics.hydrology.generator
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import os
import json
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

from ...io.lis import load_variable_for_experiment

logger = logging.getLogger(__name__)

def print_variable_statistics(var_id, var_cfg, exp_id, data):
    if data is None:
        return
        
    valid_data = data[~np.isnan(data)]
    n_total = data.size
    n_nan = n_total - valid_data.size
    pct_valid = (valid_data.size / n_total) * 100 if n_total > 0 else 0
    
    if valid_data.size == 0:
        logger.warning(f"[{var_id}] {exp_id} - ALL NaN values!")
        return
        
    d_min = np.min(valid_data)
    d_max = np.max(valid_data)
    d_mean = np.mean(valid_data)
    d_median = np.median(valid_data)
    
    unit = var_cfg.unit
    
    logger.info(f"[{var_id}] STATS {exp_id}: Min={d_min:.3f}, Max={d_max:.3f}, Mean={d_mean:.3f}, Median={d_median:.3f} | NaNs={n_nan} ({pct_valid:.1f}% valid) | Unit: {unit}")
    
    # Anomaly checks
    if 'soil_moisture' in var_id.lower() or 'rzsm' in var_id.lower() or 'ssm' in var_id.lower():
        if d_min < -0.01:
            logger.warning(f"[{var_id}] {exp_id} - SUSPECT: Negative soil moisture ({d_min:.3f})")
        if d_max > 0.8:
            logger.warning(f"[{var_id}] {exp_id} - SUSPECT: Extremely high soil moisture ({d_max:.3f} m3/m3)")
            
    if 'evapotranspiration' in var_id.lower() or 'et' in var_id.lower():
        if d_max > 25:
            logger.warning(f"[{var_id}] {exp_id} - SUSPECT: ET > 25 mm/day ({d_max:.3f})")
            
    if 'runoff' in var_id.lower() or 'qtotal' in var_id.lower():
        if d_min < -0.01:
            logger.warning(f"[{var_id}] {exp_id} - SUSPECT: Negative runoff ({d_min:.3f})")

def check_difference_magnitude(var_id, diff_data, abs_data):
    if diff_data is None or abs_data is None:
        return
        
    valid_diff = diff_data[~np.isnan(diff_data)]
    valid_abs = abs_data[~np.isnan(abs_data)]
    
    if valid_diff.size == 0 or valid_abs.size == 0:
        return
        
    max_diff = np.max(np.abs(valid_diff))
    mean_abs = np.mean(np.abs(valid_abs))
    
    if max_diff > mean_abs * 2 and mean_abs > 0.01:
        logger.warning(f"[{var_id}] SUSPECT DIFFERENCE: Max difference ({max_diff:.3f}) is more than 2x the absolute mean ({mean_abs:.3f}).")

import copy
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

def make_3panel_map(data_list, titles, out_path, var_cfg, main_title, mask=None, diff=False):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    
    valid_data = [d[~np.isnan(d)] for d in data_list if d is not None]
    if not valid_data:
        plt.close(fig)
        return
        
    if diff:
        cmap_name = var_cfg.difference_cmap
        vmin = var_cfg.difference_vmin
        vmax = var_cfg.difference_vmax
        levels = var_cfg.difference_levels
        label = var_cfg.difference_label
    else:
        cmap_name = var_cfg.cmap
        vmin = var_cfg.vmin
        vmax = var_cfg.vmax
        levels = var_cfg.levels
        label = var_cfg.colorbar_label
        
    if vmin is None or vmax is None:
        all_vals = np.concatenate(valid_data)
        if diff:
            vmax = max(abs(np.nanpercentile(all_vals, 2)), abs(np.nanpercentile(all_vals, 98)))
            vmin = -vmax
        else:
            vmin = np.nanpercentile(all_vals, 2)
            vmax = np.nanpercentile(all_vals, 98)
            
    if vmin == vmax:
        vmin -= 0.01
        vmax += 0.01

    if levels is None:
        levels = np.linspace(vmin, vmax, 11)

    cmap = copy.copy(plt.get_cmap(cmap_name))
    cmap.set_bad(color='#f0f0f0')
    
    if diff:
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
        if len(levels) > 2:
            norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N, extend='both')
    else:
        norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N, extend='both')

    ims = []
    letters = ['(a)', '(b)', '(c)']
    
    for ax, data, title, letter in zip(axes, data_list, titles, letters):
        if data is None:
            ax.set_title(f"{letter} {title} (No Data)", fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
            continue
            
        masked_data = np.where(mask, data, np.nan) if mask is not None else data
        
        im = ax.imshow(masked_data, cmap=cmap, norm=norm, origin='lower')
        ims.append(im)
        
        ax.set_title(f"{letter} {title}", fontsize=10, loc='center', fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        
        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color('gray')

    if ims:
        cbar = fig.colorbar(ims[0], ax=axes, orientation='vertical', fraction=0.02, pad=0.02, extend='both')
        cbar.set_label(label, fontsize=10)
        fmt = var_cfg.tick_format if var_cfg.tick_format else '%.2f'
        try:
            cbar.set_ticks(levels)
            cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(fmt))
        except Exception as e:
            logger.warning(f"Failed to set custom colorbar ticks: {e}")

    fig.suptitle(main_title, fontsize=13, fontweight='bold')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.05, dpi=300)
    plt.close(fig)

def make_timeseries(data_dict, recipe, experiments_catalog, var_cfg, mask, out_path, start_date, period):
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    
    for exp_id in recipe.experiments:
        if exp_id not in data_dict or data_dict[exp_id] is None:
            continue
            
        data = data_dict[exp_id]
        
        ts = []
        for t in range(data.shape[0]):
            slice_t = data[t, :, :]
            if mask is not None:
                slice_t = np.where(mask, slice_t, np.nan)
            ts.append(np.nanmean(slice_t))
            
        days = [start_date + timedelta(days=i) for i in range(len(ts))]
        ts_series = pd.Series(ts, index=days)
        ts_smooth = ts_series.rolling(window=7, center=True, min_periods=1).mean()
        
        exp_info = experiments_catalog.get(exp_id, {})
        label = exp_info.get('label', exp_id)
        
        color = '#333333' if 'opl' in exp_id.lower() else ('#E69F00' if 'nocdf' in exp_id.lower() else '#0072B2')
        
        ax.plot(days, ts_series.to_numpy(), color=color, alpha=0.3, linewidth=1.0)
        ax.plot(days, ts_smooth.to_numpy(), label=label, color=color, linewidth=2.0)
        
    unit_label = var_cfg.unit_label if var_cfg.unit_label else var_cfg.unit
    ax.set_ylabel(f"{var_cfg.long_name} ({unit_label})", fontsize=10)
    ax.set_title(f"Domain-average {var_cfg.long_name.lower()} — {recipe.domain}, {period}", fontsize=12, fontweight='bold')
    
    if var_cfg.y_min is not None and var_cfg.y_max is not None:
        ax.set_ylim(var_cfg.y_min, var_cfg.y_max)
        
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 3, 5, 7, 9, 11]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.25)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.05, dpi=300)
    plt.close(fig)

def run_hydrology_diagnostics(recipe, experiments_catalog, global_cfg, variables_data, out_base_dir):
    logger.info("--- Running Hydrology Diagnostics ---")
    generated_files = []
    
    target_vars = [v for v in recipe.variables if v not in ['obs_count', 'innovations', 'increments', 'spread', 'runoff_partitioning']]
    
    year = getattr(recipe, 'year', 2016)
    period = getattr(recipe, 'period', str(year))
    if "-" in str(period):
        start_year, end_year = str(period).split('-')
        start_date = datetime(int(start_year), 1, 1)
        end_date = datetime(int(end_year), 12, 31)
    else:
        start_date = datetime(int(period), 1, 1)
        end_date = datetime(int(period), 12, 31)
    
    # Create mask based on the first experiment's LIS output
    mask = None
    if len(recipe.experiments) > 0:
        exp_id = recipe.experiments[0]
        # Just quickly load one variable to get a mask
        sample_var = None
        from ...core.variables import Variable
        for v_raw in variables_data.values():
            v = Variable.from_dict(v_raw) if isinstance(v_raw, dict) else v_raw
            if 'SoilMoist' in str(v.lis_variable_names):
                sample_var = v
                break
        if sample_var is None:
            first_raw = next(iter(variables_data.values()))
            sample_var = Variable.from_dict(first_raw) if isinstance(first_raw, dict) else first_raw
            
        sample_data = load_variable_for_experiment(experiments_catalog[exp_id], sample_var, start_date, start_date + timedelta(days=2))
        if sample_data is not None:
            mask = ~np.isnan(sample_data[0, :, :])
            # Assuming values < -100 are missing/ocean
            mask = mask & (sample_data[0, :, :] > -100)
    
    for var_id in target_vars:
        if var_id not in variables_data:
            logger.warning(f"  -> Skipping {var_id}: Not defined in variables_data")
            continue
            
        raw_cfg = variables_data[var_id]
        from ...core.variables import Variable
        var_cfg = Variable.from_dict(raw_cfg) if isinstance(raw_cfg, dict) else raw_cfg
        
        logger.info(f"Generating hydrology diagnostics for {var_id}")
        logger.info(f"  -> LIS variables sought: {var_cfg.lis_variable_names}")
        
        data_cache = {}
        for exp_id in recipe.experiments:
            exp_info = experiments_catalog[exp_id]
            data = load_variable_for_experiment(exp_info, var_cfg, start_date, end_date)
            if data is not None:
                data_cache[exp_id] = data
                logger.info(f"  -> Loaded for {exp_id}: shape={data.shape}")
                print_variable_statistics(var_id, var_cfg, exp_id, data)
            else:
                logger.warning(f"  -> Skipping {exp_id} for {var_id}: Data not found in NetCDF")
                
        if len(data_cache) < 1:
            logger.warning(f"Not enough data for {var_id}. Skipping figures.")
            continue
            
        out_dir = os.path.join(out_base_dir, "hydrology", var_id)
        os.makedirs(out_dir, exist_ok=True)
        
        baseline_id = recipe.experiments[0]
        da_ids = recipe.experiments[1:]
        
        baseline_data = data_cache.get(baseline_id)
        if baseline_data is None:
            logger.warning(f"Baseline data {baseline_id} missing for {var_id}. Skipping maps.")
            continue
            
        # 1. Annual Mean Maps
        mean_opl = np.nanmean(baseline_data, axis=0)
        mean_da1 = np.nanmean(data_cache.get(da_ids[0]), axis=0) if len(da_ids) > 0 and da_ids[0] in data_cache else None
        mean_da2 = np.nanmean(data_cache.get(da_ids[1]), axis=0) if len(da_ids) > 1 and da_ids[1] in data_cache else None
        
        label_baseline = experiments_catalog.get(baseline_id, {}).get('label', baseline_id)
        label_da1 = experiments_catalog.get(da_ids[0], {}).get('label', da_ids[0]) if len(da_ids) > 0 else ""
        label_da2 = experiments_catalog.get(da_ids[1], {}).get('label', da_ids[1]) if len(da_ids) > 1 else ""

        map_png = os.path.join(out_dir, f"{var_id}_annual_mean_{period}.png")
        make_3panel_map(
            [mean_opl, mean_da1, mean_da2], 
            [label_baseline, label_da1, label_da2],
            map_png,
            var_cfg,
            f"Annual mean {var_cfg.long_name.lower()} — {recipe.domain}, {period}",
            mask=mask,
            diff=False
        )
        
        caption_mean = f"Annual mean spatial distribution of {var_cfg.long_name.lower()}."
        json_mean = map_png.replace('.png', '.json')
        with open(json_mean, 'w') as f:
            json.dump({
                "experiment": "OPL_noCDF_CDF",
                "variable": var_id,
                "diagnostic_type": "annual_mean",
                "filename": os.path.basename(map_png),
                "title": f"Annual mean {var_cfg.long_name.lower()} — {recipe.domain}, {period}",
                "caption": caption_mean
            }, f, indent=4)
        generated_files.extend([map_png, json_mean])
        logger.info(f"  -> Saved {map_png}")

        # 2. Difference Maps
        if mean_da1 is not None and mean_da2 is not None:
            diff1 = mean_da1 - mean_opl
            diff2 = mean_da2 - mean_opl
            diff3 = mean_da2 - mean_da1
            
            if getattr(var_cfg, 'difference_type', None) == 'reverse':
                diff1 = -diff1
                diff2 = -diff2
                diff3 = -diff3
                
            check_difference_magnitude(var_id, diff1, mean_opl)
            check_difference_magnitude(var_id, diff2, mean_opl)
            
            diff_png = os.path.join(out_dir, f"{var_id}_differences_{period}.png")
            make_3panel_map(
                [diff1, diff2, diff3], 
                [f"{label_da1} − {label_baseline}", f"{label_da2} − {label_baseline}", f"{label_da2} − {label_da1}"],
                diff_png,
                var_cfg,
                f"{var_cfg.long_name} response to assimilation — {period}",
                mask=mask,
                diff=True
            )
            
            json_diff = diff_png.replace('.png', '.json')
            with open(json_diff, 'w') as f:
                json.dump({
                    "experiment": "DA_Differences",
                    "variable": var_id,
                    "diagnostic_type": "difference",
                    "filename": os.path.basename(diff_png),
                    "title": f"{var_cfg.long_name} response to assimilation — {period}",
                    "caption": f"Impact of SMAP assimilation on {var_cfg.long_name.lower()}."
                }, f, indent=4)
            generated_files.extend([diff_png, json_diff])
            logger.info(f"  -> Saved {diff_png}")

        # 3. Domain-Averaged Timeseries
        ts_png = os.path.join(out_dir, f"{var_id}_domain_mean_timeseries_{period}.png")
        make_timeseries(data_cache, recipe, experiments_catalog, var_cfg, mask, ts_png, start_date, period)
        
        json_ts = ts_png.replace('.png', '.json')
        with open(json_ts, 'w') as f:
            json.dump({
                "experiment": "OPL_noCDF_CDF",
                "variable": var_id,
                "diagnostic_type": "timeseries",
                "filename": os.path.basename(ts_png),
                "title": f"Domain-average {var_cfg.long_name.lower()} time series — {period}",
                "caption": f"Daily domain-averaged timeseries of {var_cfg.long_name.lower()}."
            }, f, indent=4)
        generated_files.extend([ts_png, json_ts])
        logger.info(f"  -> Saved {ts_png}")

    logger.info("--- Hydrology Diagnostics Completed ---")
    return generated_files
