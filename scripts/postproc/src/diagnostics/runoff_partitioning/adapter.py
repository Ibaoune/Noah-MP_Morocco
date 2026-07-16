# Author: M. El Aabaribaoune (@um6p)
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

# A dummy variable class to pass to load_variable_for_experiment
class DummyVar:
    def __init__(self, name):
        self.lis_variable_names = [name]
        self.operation = 'direct'
        self.scale_factor = 86400.0  # Convert kg m-2 s-1 to mm/day
        self.unit = 'mm/day'
        self.layer = None
        self.variable_id = name

def get_landmask(data):
    if data is None:
        return None
    # Data is (T, lat, lon). Get first time step.
    d0 = data[0, :, :]
    mask = ~np.isnan(d0) & (d0 > -100)
    return mask

def run_runoff_partitioning_diagnostics(recipe, experiments_catalog, out_dir):
    logger.info("--- Running Runoff Partitioning Diagnostics ---")
    generated_files = []
    
    start_date = datetime(recipe.year, 1, 1)
    end_date = datetime(recipe.year, 12, 31)
    
    # We expect OPL as baseline and DA as subsequent experiments
    baseline_id = recipe.experiments[0] if len(recipe.experiments) > 0 else None
    
    data_cache = {}
    
    var_qs = DummyVar('Qs_tavg')
    var_qsb = DummyVar('Qsb_tavg')
    
    mask = None
    for exp_id in recipe.experiments:
        exp_info = experiments_catalog.get(exp_id)
        if not exp_info: continue
        
        qs_data = load_variable_for_experiment(exp_info, var_qs, start_date, end_date)
        qsb_data = load_variable_for_experiment(exp_info, var_qsb, start_date, end_date)
        
        if qs_data is not None and qsb_data is not None:
            data_cache[exp_id] = {'Qs': qs_data, 'Qsb': qsb_data}
            if mask is None:
                mask = get_landmask(qs_data)
                
    if len(data_cache) == 0:
        logger.warning("No data loaded for Runoff Partitioning. Skipping.")
        return []
        
    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle(f"Runoff Partitioning — {recipe.domain}, {recipe.year}", fontsize=16)
    
    for exp_id, data in data_cache.items():
        exp_info = experiments_catalog.get(exp_id, {})
        label = exp_info.get('label', exp_id)
        color = '#333333' if 'opl' in exp_id.lower() else ('#E69F00' if 'nocdf' in exp_id.lower() else '#0072B2')
        linewidth = 2.0
        
        # Calculate Basin Averages
        T = data['Qs'].shape[0]
        qs_ts = []
        qsb_ts = []
        for t in range(T):
            qs_slice = data['Qs'][t, :, :]
            qsb_slice = data['Qsb'][t, :, :]
            if mask is not None:
                qs_slice = np.where(mask, qs_slice, np.nan)
                qsb_slice = np.where(mask, qsb_slice, np.nan)
            qs_ts.append(np.nanmean(qs_slice))
            qsb_ts.append(np.nanmean(qsb_slice))
            
        qs_ts = np.array(qs_ts)
        qsb_ts = np.array(qsb_ts)
        
        # 7-day smoothing
        qs_series = pd.Series(qs_ts).rolling(window=7, center=True, min_periods=1).mean()
        qsb_series = pd.Series(qsb_ts).rolling(window=7, center=True, min_periods=1).mean()
        
        days = [start_date + timedelta(days=i) for i in range(T)]
        
        # Plot Qs
        axes[0].plot(days, qs_series, label=label, color=color, linewidth=linewidth)
        
        # Plot Qsb
        axes[1].plot(days, qsb_series, label=label, color=color, linewidth=linewidth)
        
        # Plot Fraction
        total_runoff = qs_series + qsb_series
        fraction = np.where(total_runoff > 0, qsb_series / total_runoff, np.nan)
        axes[2].plot(days, fraction, label=label, color=color, linewidth=linewidth)
        
    axes[0].set_title("Surface Runoff (Qs) [mm/day] (Basin Average)")
    axes[0].set_ylabel("mm/day")
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.5)
    
    axes[1].set_title("Baseflow (Qsb) [mm/day] (Basin Average)")
    axes[1].set_ylabel("mm/day")
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.5)
    
    axes[2].set_title("Baseflow Fraction (Qsb / Total Runoff)")
    axes[2].set_ylabel("Fraction")
    axes[2].set_ylim(0, 1)
    axes[2].legend()
    axes[2].grid(True, linestyle='--', alpha=0.5)
    
    import matplotlib.dates as mdates
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_file = os.path.join(out_dir, "runoff_partitioning_timeseries.png")
    fig.savefig(out_file, dpi=300)
    plt.close(fig)
    
    generated_files.append(out_file)
    logger.info(f"  -> Saved {out_file}")
    
    return generated_files
