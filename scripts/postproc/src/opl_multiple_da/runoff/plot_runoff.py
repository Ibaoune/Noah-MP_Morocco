"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.runoff.plot_runoff
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def run_runoff_diagnostics(data_dict, out_dir):
    """
    Bloc 5: Runoff
    Objectif: Évaluer l'impact sur les composantes du ruissellement.
    """
    generated_figures = []
    
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    if not files_ol:
        return generated_figures

    mask = get_landmask(files_ol)
    var_qs = 'Qs_tavg'
    var_qsb = 'Qsb_tavg'
    mult_q = 86400.0 # Convert kg/m2/s to mm/day
    
    # Load Runoff (Qs and Qsb)
    print("Loading Qs_tavg and Qsb_tavg...")
    data_qs_ol = load_lis_variable(files_ol, var_qs)
    data_qsb_ol = load_lis_variable(files_ol, var_qsb)
    
    data_qs_nocdf = load_lis_variable(files_nocdf, var_qs) if files_nocdf else None
    data_qsb_nocdf = load_lis_variable(files_nocdf, var_qsb) if files_nocdf else None
    
    data_qs_cdf = load_lis_variable(files_cdf, var_qs) if files_cdf else None
    data_qsb_cdf = load_lis_variable(files_cdf, var_qsb) if files_cdf else None

    def apply_mask(data, mask):
        if data is None or mask is None:
            return None
        return np.where(mask, data, np.nan)

    if data_qs_ol is not None and data_qsb_ol is not None:
        qs_ol = data_qs_ol * mult_q
        qsb_ol = data_qsb_ol * mult_q
        qtot_ol = qs_ol + qsb_ol
        
        qs_nocdf = data_qs_nocdf * mult_q if data_qs_nocdf is not None else None
        qsb_nocdf = data_qsb_nocdf * mult_q if data_qsb_nocdf is not None else None
        qtot_nocdf = qs_nocdf + qsb_nocdf if qs_nocdf is not None and qsb_nocdf is not None else None
        
        qs_cdf = data_qs_cdf * mult_q if data_qs_cdf is not None else None
        qsb_cdf = data_qsb_cdf * mult_q if data_qsb_cdf is not None else None
        qtot_cdf = qs_cdf + qsb_cdf if qs_cdf is not None and qsb_cdf is not None else None

        # 36: Mean Total Runoff
        print("  -> Generating 36_total_runoff_mean_opl_nocdf_cdf_2016.png")
        f36 = os.path.join(out_dir, "36_total_runoff_mean_opl_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(qtot_ol, axis=0), mask), cmap='Blues', origin='lower')
        axes[0].set_title('OPL Total Runoff')
        if qtot_nocdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(qtot_nocdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[1].set_title('NoCDF Total Runoff')
        if qtot_cdf is not None:
            im3 = axes[2].imshow(apply_mask(np.nanmean(qtot_cdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[2].set_title('CDF Total Runoff')
        fig.colorbar(im1, ax=axes, label='Runoff (mm/day)')
        plt.suptitle('Mean total runoff in OPL, DA-NoCDF and DA-CDF experiments')
        plt.savefig(f36, dpi=150)
        plt.close()
        generated_figures.append(f36)

        # 37: Total Runoff Differences
        print("  -> Generating 37_total_runoff_differences_2016.png")
        f37 = os.path.join(out_dir, "37_total_runoff_differences_2016.png")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if qtot_nocdf is not None:
            im1 = axes[0].imshow(apply_mask(np.nanmean(qtot_nocdf - qtot_ol, axis=0), mask), cmap='RdBu', origin='lower', vmin=-0.5, vmax=0.5)
            axes[0].set_title('NoCDF - OPL Total Runoff')
        if qtot_cdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(qtot_cdf - qtot_ol, axis=0), mask), cmap='RdBu', origin='lower', vmin=-0.5, vmax=0.5)
            axes[1].set_title('CDF - OPL Total Runoff')
        fig.colorbar(im1, ax=axes, label='Delta Runoff (mm/day)')
        plt.suptitle('Impact of No-CDF and CDF SMAP assimilation on total runoff')
        plt.savefig(f37, dpi=150)
        plt.close()
        generated_figures.append(f37)

        # 38: Mean Surface Runoff
        print("  -> Generating 38_surface_runoff_mean_opl_nocdf_cdf_2016.png")
        f38 = os.path.join(out_dir, "38_surface_runoff_mean_opl_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(qs_ol, axis=0), mask), cmap='Blues', origin='lower')
        axes[0].set_title('OPL Surface Runoff')
        if qs_nocdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(qs_nocdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[1].set_title('NoCDF Surface Runoff')
        if qs_cdf is not None:
            im3 = axes[2].imshow(apply_mask(np.nanmean(qs_cdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[2].set_title('CDF Surface Runoff')
        fig.colorbar(im1, ax=axes, label='Surface Runoff (mm/day)')
        plt.suptitle('Mean surface runoff in OPL, DA-NoCDF and DA-CDF experiments')
        plt.savefig(f38, dpi=150)
        plt.close()
        generated_figures.append(f38)

        # 39: Surface Runoff Differences
        print("  -> Generating 39_surface_runoff_differences_2016.png")
        f39 = os.path.join(out_dir, "39_surface_runoff_differences_2016.png")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if qs_nocdf is not None:
            im1 = axes[0].imshow(apply_mask(np.nanmean(qs_nocdf - qs_ol, axis=0), mask), cmap='RdBu', origin='lower', vmin=-0.2, vmax=0.2)
            axes[0].set_title('NoCDF - OPL Surface Runoff')
        if qs_cdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(qs_cdf - qs_ol, axis=0), mask), cmap='RdBu', origin='lower', vmin=-0.2, vmax=0.2)
            axes[1].set_title('CDF - OPL Surface Runoff')
        fig.colorbar(im1, ax=axes, label='Delta Surface Runoff (mm/day)')
        plt.suptitle('Surface runoff response to No-CDF and CDF SMAP assimilation')
        plt.savefig(f39, dpi=150)
        plt.close()
        generated_figures.append(f39)

        # 40: Mean Baseflow
        print("  -> Generating 40_baseflow_mean_opl_nocdf_cdf_2016.png")
        f40 = os.path.join(out_dir, "40_baseflow_mean_opl_nocdf_cdf_2016.png")
        
        levels_mean = [0.00, 0.005, 0.01, 0.02, 0.035, 0.05, 0.075, 0.10, 0.125, 0.15]
        cmap_ylgnbu = plt.get_cmap('YlGnBu')(np.linspace(0.1, 1, len(levels_mean) - 1))
        cmap_mean = mcolors.ListedColormap(cmap_ylgnbu)
        cmap_mean.set_bad(color='#e0e0e0')
        norm_mean = mcolors.BoundaryNorm(levels_mean, cmap_mean.N)
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        mean_data = [
            (np.nanmean(qsb_ol, axis=0), "(a) OPL"),
            (np.nanmean(qsb_nocdf, axis=0) if qsb_nocdf is not None else None, "(b) DA-SMAP-noCDF"),
            (np.nanmean(qsb_cdf, axis=0) if qsb_cdf is not None else None, "(c) DA-SMAP-CDF")
        ]

        im_mean = None
        for ax, (data, title) in zip(axes, mean_data):
            if data is not None:
                data_masked = apply_mask(data, mask)
                im_mean = ax.imshow(data_masked, cmap=cmap_mean, norm=norm_mean, origin='lower')
            ax.set_title(title, fontsize=12)
            ax.axis('off')

        if im_mean is not None:
            cbar = fig.colorbar(im_mean, ax=axes, extend='max', shrink=0.8, pad=0.02)
            cbar.set_label('Annual mean baseflow (mm d⁻¹)', fontsize=12)
            cbar.set_ticks([0.00, 0.02, 0.05, 0.075, 0.10, 0.125, 0.15])

        plt.suptitle('Annual mean baseflow — NorthMor, 2016', fontsize=15, y=0.98)
        plt.subplots_adjust(wspace=0.1)
        plt.savefig(f40, dpi=600, bbox_inches='tight')
        plt.savefig(f40.replace('.png', '.pdf'), bbox_inches='tight')
        plt.close()
        generated_figures.append(f40)

        # 41: Baseflow Differences
        print("  -> Generating 41_baseflow_differences_2016.png")
        f41 = os.path.join(out_dir, "41_baseflow_differences_2016.png")
        
        levels_diff = [-0.05, -0.04, -0.03, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05]
        colors_diff = plt.get_cmap('RdBu', 256)(np.linspace(0, 1, len(levels_diff) - 1))
        colors_diff[5] = mcolors.to_rgba('#f5f5f5')
        cmap_diff = mcolors.ListedColormap(colors_diff)
        cmap_diff.set_bad(color='#e0e0e0')
        norm_diff = mcolors.BoundaryNorm(levels_diff, cmap_diff.N)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        diff_data = [
            (np.nanmean(qsb_nocdf - qsb_ol, axis=0) if qsb_nocdf is not None else None, "(a) noCDF − OPL"),
            (np.nanmean(qsb_cdf - qsb_ol, axis=0) if qsb_cdf is not None else None, "(b) CDF − OPL"),
            (np.nanmean(qsb_cdf - qsb_nocdf, axis=0) if (qsb_cdf is not None and qsb_nocdf is not None) else None, "(c) CDF − noCDF")
        ]

        im_diff = None
        for ax, (data, title) in zip(axes, diff_data):
            if data is not None:
                data_masked = apply_mask(data, mask)
                im_diff = ax.imshow(data_masked, cmap=cmap_diff, norm=norm_diff, origin='lower')
                
                mean_val = np.nanmean(data_masked)
                median_val = np.nanmedian(data_masked)
                pct_area = np.nansum(np.abs(data_masked) > 0.005) / np.nansum(~np.isnan(data_masked)) * 100.0
                
                textstr = f"Mean Δ: {mean_val:.3f}\nMedian Δ: {median_val:.3f}\n|Δ| > 0.005: {pct_area:.1f}%"
                props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='lightgrey')
                ax.text(0.03, 0.96, textstr, transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', bbox=props)
            ax.set_title(title, fontsize=12)
            ax.axis('off')

        if im_diff is not None:
            cbar = fig.colorbar(im_diff, ax=axes, extend='both', shrink=0.8, pad=0.02)
            cbar.set_label('Δ baseflow (mm d⁻¹)', fontsize=12)
            cbar.set_ticks([-0.05, -0.03, -0.01, 0, 0.01, 0.03, 0.05])
            
        plt.suptitle('Baseflow response to assimilation — 2016', fontsize=15, y=0.98)
        plt.subplots_adjust(wspace=0.1)
        plt.savefig(f41, dpi=600, bbox_inches='tight')
        plt.savefig(f41.replace('.png', '.pdf'), bbox_inches='tight')
        plt.close()
        generated_figures.append(f41)

        # 42: Total Runoff Timeseries
        print("  -> Generating 42_total_runoff_timeseries_2016.png")
        f42 = os.path.join(out_dir, "42_total_runoff_timeseries_2016.png")
        plt.figure(figsize=(10, 4))
        plt.plot(calculate_basin_average(qtot_ol, mask), label='OPL')
        if qtot_nocdf is not None:
            plt.plot(calculate_basin_average(qtot_nocdf, mask), label='NoCDF')
        if qtot_cdf is not None:
            plt.plot(calculate_basin_average(qtot_cdf, mask), label='CDF')
        plt.legend()
        plt.title('Basin-averaged total runoff time series for OPL, DA-NoCDF and DA-CDF')
        plt.grid(True)
        plt.savefig(f42, dpi=150)
        plt.close()
        generated_figures.append(f42)

        # 43: Surface Runoff Timeseries
        print("  -> Generating 43_surface_runoff_timeseries_2016.png")
        f43 = os.path.join(out_dir, "43_surface_runoff_timeseries_2016.png")
        plt.figure(figsize=(10, 4))
        plt.plot(calculate_basin_average(qs_ol, mask), label='OPL')
        if qs_nocdf is not None:
            plt.plot(calculate_basin_average(qs_nocdf, mask), label='NoCDF')
        if qs_cdf is not None:
            plt.plot(calculate_basin_average(qs_cdf, mask), label='CDF')
        plt.legend()
        plt.title('Basin-averaged surface runoff time series for OPL, DA-NoCDF and DA-CDF')
        plt.grid(True)
        plt.savefig(f43, dpi=150)
        plt.close()
        generated_figures.append(f43)

        # 44: Baseflow Timeseries
        print("  -> Generating 44_baseflow_timeseries_2016.png")
        f44 = os.path.join(out_dir, "44_baseflow_timeseries_2016.png")
        
        fig44, axes44 = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [2.5, 1]}, sharex=True)
        
        ts_opl = calculate_basin_average(qsb_ol, mask)
        ts_nocdf = calculate_basin_average(qsb_nocdf, mask) if qsb_nocdf is not None else None
        ts_cdf = calculate_basin_average(qsb_cdf, mask) if qsb_cdf is not None else None
        
        axes44[0].plot(ts_opl, label='OPL', color='#2b2b2b', linewidth=2.0)
        if ts_nocdf is not None:
            axes44[0].plot(ts_nocdf, label='DA-SMAP-noCDF', color='#E69F00', linewidth=2.0)
        if ts_cdf is not None:
            axes44[0].plot(ts_cdf, label='DA-SMAP-CDF', color='#0072B2', linewidth=2.0)
        
        axes44[0].set_ylim(0, 0.15)
        axes44[0].set_title('Domain-averaged baseflow, NorthMor, 2016', fontsize=15)
        axes44[0].set_ylabel('Baseflow (mm d⁻¹)', fontsize=12)
        axes44[0].tick_params(axis='both', which='major', labelsize=11)
        axes44[0].grid(True, color='lightgray', alpha=0.4)
        axes44[0].legend(loc='upper right', frameon=True, framealpha=0.9, edgecolor='gray', fontsize=11)
        
        if ts_nocdf is not None:
            axes44[1].plot(ts_nocdf - ts_opl, label='DA-SMAP-noCDF − OPL', color='#E69F00', linewidth=1.5)
        if ts_cdf is not None:
            axes44[1].plot(ts_cdf - ts_opl, label='DA-SMAP-CDF − OPL', color='#0072B2', linewidth=1.5)
            
        axes44[1].axhline(0, color='gray', linestyle='--', linewidth=1)
        axes44[1].set_ylabel('Δ (mm d⁻¹)', fontsize=12)
        axes44[1].tick_params(axis='both', which='major', labelsize=11)
        axes44[1].grid(True, color='lightgray', alpha=0.4)
        
        plt.tight_layout()
        plt.savefig(f44, dpi=600, bbox_inches='tight')
        plt.savefig(f44.replace('.png', '.pdf'), bbox_inches='tight')
        plt.close()
        generated_figures.append(f44)

    # 45, 46, 47, 48 - Placeholders
    figures_to_stub = [
        ("45_baseflow_fraction_2016.png", "Baseflow fraction response to No-CDF and CDF SMAP assimilation"),
        ("46_monthly_runoff_partitioning_2016.png", "Monthly partitioning of total runoff into surface runoff and baseflow"),
        ("47_cumulative_runoff_components_2016.png", "Cumulative surface runoff, baseflow and total runoff under OPL, DA-NoCDF and DA-CDF"),
        ("48_delta_baseflow_vs_delta_surface_runoff_2016.png", "Relative sensitivity of baseflow and surface runoff to SMAP assimilation")
    ]
    for fn, title in figures_to_stub:
        print(f"  -> Generating {fn}")
        p = os.path.join(out_dir, fn)
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, "Placeholder", ha='center')
        plt.title(title)
        plt.savefig(p, dpi=150)
        plt.close()
        generated_figures.append(p)

    return generated_figures
