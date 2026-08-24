# Author: M. EL Aabaribaoune (@um6p)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Create directories
os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('outputs/tables', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# 1. Load Data
df = pd.read_parquet('data/processed/monthly_pixel_dataset_2016_2020_static.parquet')

# Variables mapping & conversion
days_in_month = {1:31, 2:28.25, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
if 'month' not in df.columns:
    df['month'] = pd.to_datetime(df['time']).dt.month
df['days'] = df['month'].map(days_in_month)

var_map = {
    'ET': ('Evap_tavg_OPL', 'Evap_tavg_DA_NoCDF', 'Evap_tavg_DA_CDF'),
    'Qs': ('Qs_tavg_OPL', 'Qs_tavg_DA_NoCDF', 'Qs_tavg_DA_CDF'),
    'Qsb': ('Qsb_tavg_OPL', 'Qsb_tavg_DA_NoCDF', 'Qsb_tavg_DA_CDF'),
}
for v in ['ET', 'Qs', 'Qsb']:
    for c in var_map[v]:
        if c in df.columns:
            df[c + '_mm_day'] = df[c] / df['days']

for exp in ['OPL', 'DA_NoCDF', 'DA_CDF']:
    df[f'Qtotal_{exp}_mm_day'] = df[f'Qs_tavg_{exp}_mm_day'] + df[f'Qsb_tavg_{exp}_mm_day']

df_djf = df[df['month'].isin([12, 1, 2])]
df_jja = df[df['month'].isin([6, 7, 8])]
df_ann = df

# Verify n_grid_cells
n_unique = df[['north_south', 'east_west']].drop_duplicates().shape[0]

# Helper function to plot 2D mesh
def plot_hydrological_figures(subset_df, period_name):
    mean_df = subset_df.groupby(['north_south', 'east_west']).mean().reset_index()
    
    state_vars = [
        ('SSM', 'SSM', 'SSM', 'm3/m3', 0.05),
        ('RZSM', 'RZSM', 'RZSM', 'm3/m3', 0.05),
        ('ET', 'Evap_tavg', '_mm_day', 'mm/day', 0.5)
    ]
    
    runoff_vars = [
        ('Total runoff', 'Qtotal', '_mm_day', 'mm/day', 0.2),
        ('Surface runoff', 'Qs_tavg', '_mm_day', 'mm/day', 0.1),
        ('Baseflow', 'Qsb_tavg', '_mm_day', 'mm/day', 0.2)
    ]
    
    experiments = [
        ('DA_NoCDF - OPL', 'DA_NoCDF', 'OPL'),
        ('DA_CDF - OPL', 'DA_CDF', 'OPL'),
        ('DA_NoCDF - DA_CDF', 'DA_NoCDF', 'DA_CDF')
    ]
    
    def generate_grid_plot(vars_list, filename_suffix):
        fig, axes = plt.subplots(3, 3, figsize=(12, 12))
        for c, (title, base_var, suffix, unit, vmax) in enumerate(vars_list):
            for r, (row_title, exp1, exp2) in enumerate(experiments):
                ax = axes[r, c]
                ax.set_aspect('equal')
                ax.set_facecolor('white')
                ax.axis('off')
                
                if base_var == 'Qtotal':
                    col1 = f'Qtotal_{exp1}{suffix}'
                    col2 = f'Qtotal_{exp2}{suffix}'
                else:
                    col1 = f'{base_var}_{exp1}'
                    if suffix == '_mm_day': col1 += suffix
                    col2 = f'{base_var}_{exp2}'
                    if suffix == '_mm_day': col2 += suffix
                
                diff = mean_df[col1] - mean_df[col2]
                
                grid1 = mean_df.pivot(index='north_south', columns='east_west', values=col1)
                grid2 = mean_df.pivot(index='north_south', columns='east_west', values=col2)
                grid_diff = grid1 - grid2
                
                im = ax.imshow(grid_diff.values, cmap='RdBu', vmin=-vmax, vmax=vmax, origin='lower')
                
                d_min, d_mean, d_max = diff.min(), diff.mean(), diff.max()
                pos_pct = (diff > 0).mean() * 100
                neg_pct = (diff < 0).mean() * 100
                
                ax.set_title(f"{row_title}\nΔ{title}")
                ax.text(0.02, 0.02, f"Min: {d_min:.3f} Mean: {d_mean:.3f} Max: {d_max:.3f}\nPos: {pos_pct:.1f}% Neg: {neg_pct:.1f}%", 
                        transform=ax.transAxes, fontsize=7, bbox=dict(facecolor='white', alpha=0.8, pad=0.5))
                
                if r == 2:
                    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
                    cbar.set_label(f"Δ{title} ({unit})")
        
        plt.tight_layout()
        plt.savefig(f'outputs/figures/q1_fig_hydrological_response_{filename_suffix}_{period_name}_2016_2020.png', dpi=150, facecolor='white')
        plt.close()
        
    generate_grid_plot(state_vars, "states_ET")
    generate_grid_plot(runoff_vars, "runoff")

print("Generating state/ET and runoff specific figures...")
plot_hydrological_figures(df_ann, "annual")
plot_hydrological_figures(df_djf, "DJF")
plot_hydrological_figures(df_jja, "JJA")

print(f"Unique grid cells detected: {n_unique}")
