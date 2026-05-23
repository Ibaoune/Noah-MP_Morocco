#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)
#
# Parse scalability runtimes from logs and plot speedup/scalability curves

import os
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set premium styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['text.color'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, 'experiments/scalability/timing_results.csv')
LOGS_DIR = os.path.join(BASE_DIR, 'logs/slurm')
FIG_DIR = os.path.join(BASE_DIR, 'postproc/figures')
os.makedirs(FIG_DIR, exist_ok=True)

def parse_time(time_str):
    """Convert time string like 12m4.393s or 0m38.813s or 32.043s into seconds"""
    time_str = time_str.strip()
    match = re.search(r'(?:(\d+)m)?([\d\.]+)s?', time_str)
    if not match:
        return None
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = float(match.group(2))
    return minutes * 60 + seconds

def main():
    if not os.path.exists(CSV_FILE):
        print(f"Error: Timing file {CSV_FILE} not found!")
        return

    df = pd.read_csv(CSV_FILE)
    runtimes = []

    for idx, row in df.iterrows():
        job_id = row['job_id']
        log_file = os.path.join(LOGS_DIR, f"lis_scale_{job_id}.log")
        
        runtime = None
        if os.path.exists(log_file):
            try:
                # Open with ignore errors for potential binary characters
                with open(log_file, 'r', errors='ignore') as f:
                    content = f.read()
                    # Find lines like: real    3m59.804s
                    matches = re.findall(r'^real\s+([\d\.ms]+)', content, re.MULTILINE)
                    if matches:
                        runtime = parse_time(matches[0])
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        
        if runtime is None:
            print(f"Warning: Could not parse runtime for job {job_id} ({row['label']})")
            # Fallback to a placeholder or skip
            runtime = np.nan
            
        runtimes.append(runtime)

    df['runtime_seconds'] = runtimes
    df = df.dropna().sort_values(by='ntasks')
    
    # Save the updated data with runtimes
    df.to_csv(os.path.join(BASE_DIR, 'experiments/scalability/timing_results_with_runtimes.csv'), index=False)
    print("\nParsed Timing Results:")
    print(df[['label', 'nodes', 'ntasks', 'runtime_seconds']])

    # Separate OPL and DA
    opl_df = df[df['label'].str.startswith('OPL')].sort_values(by='ntasks')
    da_df = df[df['label'].str.startswith('DA')].sort_values(by='ntasks')

    # Create figure with 2 subplots (Runtime and Speedup)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=150)
    
    colors = {'OPL': '#1f77b4', 'DA': '#ff7f0e'} # Blue and orange
    
    # ----------------------------------------------------
    # Subplot 1: Absolute Runtime
    # ----------------------------------------------------
    if not opl_df.empty:
        ax1.plot(opl_df['ntasks'].to_numpy(), (opl_df['runtime_seconds'] / 60.0).to_numpy(), 
                 marker='o', linewidth=2.5, color=colors['OPL'], label='Open-Loop (OPL)')
    if not da_df.empty:
        ax1.plot(da_df['ntasks'].to_numpy(), (da_df['runtime_seconds'] / 60.0).to_numpy(), 
                 marker='s', linewidth=2.5, color=colors['DA'], label='Data Assimilation (DA)')

    ax1.set_xscale('log', base=2)
    # Set xticks to match our test cases
    xtick_vals = [4, 16, 32, 64, 128, 256, 512, 896]
    ax1.set_xticks(xtick_vals)
    ax1.set_xticklabels([str(x) for x in xtick_vals])
    
    ax1.set_title('Execution Time vs. MPI Tasks (3-Day Run)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Total MPI Tasks', fontsize=11, labelpad=10)
    ax1.set_ylabel('Execution Time (minutes)', fontsize=11, labelpad=10)
    ax1.legend(frameon=True, facecolor='white', edgecolor='none')
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # ----------------------------------------------------
    # Subplot 2: Speedup (relative to 4 tasks)
    # Speedup = Time(4) / Time(N)
    # ----------------------------------------------------
    # Ideal line starts at (4, 1) and scales linearly: Speedup(N) = N / 4
    ax2.plot(xtick_vals, [x / 4.0 for x in xtick_vals], 
             linestyle='--', color='#888888', label='Ideal Scaling (Linear)')
             
    if not opl_df.empty:
        t4_opl = opl_df.loc[opl_df['ntasks'] == 4, 'runtime_seconds'].values
        if len(t4_opl) > 0:
            opl_speedup = t4_opl[0] / opl_df['runtime_seconds'].to_numpy()
            ax2.plot(opl_df['ntasks'].to_numpy(), opl_speedup, 
                     marker='o', linewidth=2.5, color=colors['OPL'], label='OPL Speedup')
            # Print speedups
            print("\nOPL Speedups:")
            for nt, su in zip(opl_df['ntasks'].to_numpy(), opl_speedup):
                print(f"  {nt} tasks: {su:.2f}x speedup")

    if not da_df.empty:
        t4_da = da_df.loc[da_df['ntasks'] == 4, 'runtime_seconds'].values
        if len(t4_da) > 0:
            da_speedup = t4_da[0] / da_df['runtime_seconds'].to_numpy()
            ax2.plot(da_df['ntasks'].to_numpy(), da_speedup, 
                     marker='s', linewidth=2.5, color=colors['DA'], label='DA Speedup')
            # Print speedups
            print("\nDA Speedups:")
            for nt, su in zip(da_df['ntasks'].to_numpy(), da_speedup):
                print(f"  {nt} tasks: {su:.2f}x speedup")


    ax2.set_xscale('log', base=2)
    ax2.set_yscale('log', base=2)
    ax2.set_xticks(xtick_vals)
    ax2.set_xticklabels([str(x) for x in xtick_vals])
    ax2.set_yticks([1, 4, 16, 64, 256])
    ax2.set_yticklabels(['1x', '4x', '16x', '64x', '256x'])
    
    ax2.set_title('Speedup vs. MPI Tasks (Baseline = 4 Tasks)', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xlabel('Total MPI Tasks', fontsize=11, labelpad=10)
    ax2.set_ylabel('Speedup Factor', fontsize=11, labelpad=10)
    ax2.legend(frameon=True, facecolor='white', edgecolor='none')
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    plt.suptitle('LIS NoahMP Morocco Scalability Analysis on Toubkal Cluster\n(Grid: 200x150, Max 32 Tasks/Node)', 
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    plot_path = os.path.join(FIG_DIR, 'lis_scalability_performance.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f"\nFigure saved successfully to: {plot_path}")

if __name__ == '__main__':
    main()
