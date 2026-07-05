"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.assimilation.plot_assimilation
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.io_da import load_da_variable
from utils.masking import get_landmask

def run_assimilation_diagnostics(data_dict, out_dir):
    """
    Bloc 1: Assimilation Diagnostics
    Objectif: Répondre à la question "Le CDF change-t-il réellement le signal d'assimilation ?"
    """
    generated_figures = []
    
    da_nocdf = data_dict.get('da_nocdf', {})
    da_cdf = data_dict.get('da_cdf', {})
    
    # We will use the landmask from LIS files (OL or DA doesn't matter for mask)
    files_nocdf = data_dict.get('files_da_nocdf', [])
    mask = get_landmask(files_nocdf) if files_nocdf else None

    if not da_nocdf.get('innov') and not da_cdf.get('innov'):
        print("Warning: No DA EnKF files found for assimilation diagnostics.")
        return generated_figures

    # Load Variables
    print("Loading DA variables... This may take a moment.")
    innov_cdf = load_da_variable(da_cdf.get('innov', []), 'innov_01')
    innov_nocdf = load_da_variable(da_nocdf.get('innov', []), 'innov_01')
    
    incr_cdf = load_da_variable(da_cdf.get('incr', []), 'anlys_incr_Soil Moisture Layer 1_01', extract_layer=0)
    incr_nocdf = load_da_variable(da_nocdf.get('incr', []), 'anlys_incr_Soil Moisture Layer 1_01', extract_layer=0)
    
    spread_cdf = load_da_variable(da_cdf.get('spread', []), 'ensspread_Soil Moisture Layer 1_01', extract_layer=0)
    spread_nocdf = load_da_variable(da_nocdf.get('spread', []), 'ensspread_Soil Moisture Layer 1_01', extract_layer=0)
    
    # Optional DAOBS file parsing not fully implemented here as it requires reading 1gs4r formats.
    # We will estimate obs from innov (innov exists where obs exist).

    # Helper function
    def apply_mask(data, mask):
        if data is None or mask is None:
            return None
        return np.where(mask, data, np.nan)

    # 01
    print("  -> Generating 01_assimilated_observations_coverage_2016.png")
    f1 = os.path.join(out_dir, "01_assimilated_observations_coverage_2016.png")
    if innov_cdf is not None:
        obs_count = np.sum(~np.isnan(innov_cdf), axis=0)
        plt.figure(figsize=(8, 6))
        plt.imshow(apply_mask(obs_count, mask), cmap='viridis', origin='lower')
        plt.colorbar(label='Frequency')
        plt.title('Spatial coverage and frequency of assimilated SMAP observations in 2016')
        plt.savefig(f1, dpi=150)
        plt.close()
        generated_figures.append(f1)

    # 02
    print("  -> Generating 02_monthly_assimilated_observations_2016.png")
    f2 = os.path.join(out_dir, "02_monthly_assimilated_observations_2016.png")
    if innov_cdf is not None:
        obs_ts = np.sum(~np.isnan(innov_cdf), axis=(1, 2))
        plt.figure(figsize=(10, 4))
        plt.plot(obs_ts, label='Assimilated Obs Count')
        plt.xlabel('Assimilation Cycles')
        plt.ylabel('Count')
        plt.title('Monthly number of assimilated SMAP observations in 2016')
        plt.grid(True)
        plt.savefig(f2, dpi=150)
        plt.close()
        generated_figures.append(f2)

    # 03
    print("  -> Generating 03_mean_innovation_nocdf_vs_cdf_2016.png")
    f3 = os.path.join(out_dir, "03_mean_innovation_nocdf_vs_cdf_2016.png")
    if innov_cdf is not None and innov_nocdf is not None:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(innov_nocdf, axis=0), mask), cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower')
        axes[0].set_title('NoCDF Mean Innovation')
        im2 = axes[1].imshow(apply_mask(np.nanmean(innov_cdf, axis=0), mask), cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower')
        axes[1].set_title('CDF Mean Innovation')
        fig.colorbar(im2, ax=axes, label='m3/m3')
        plt.suptitle('Mean SMAP innovation for No-CDF and CDF assimilation experiments in 2016')
        plt.savefig(f3, dpi=150)
        plt.close()
        generated_figures.append(f3)

    # 04
    print("  -> Generating 04_mean_increment_nocdf_vs_cdf_2016.png")
    f4 = os.path.join(out_dir, "04_mean_increment_nocdf_vs_cdf_2016.png")
    if incr_cdf is not None and incr_nocdf is not None:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(incr_nocdf, axis=0), mask), cmap='RdBu', vmin=-0.02, vmax=0.02, origin='lower')
        axes[0].set_title('NoCDF Mean Increment')
        im2 = axes[1].imshow(apply_mask(np.nanmean(incr_cdf, axis=0), mask), cmap='RdBu', vmin=-0.02, vmax=0.02, origin='lower')
        axes[1].set_title('CDF Mean Increment')
        fig.colorbar(im2, ax=axes, label='m3/m3')
        plt.suptitle('Mean soil moisture analysis increments for No-CDF and CDF assimilation experiments in 2016')
        plt.savefig(f4, dpi=150)
        plt.close()
        generated_figures.append(f4)

    # 05
    print("  -> Generating 05_increment_histogram_nocdf_vs_cdf_2016.png")
    f5 = os.path.join(out_dir, "05_increment_histogram_nocdf_vs_cdf_2016.png")
    if incr_cdf is not None and incr_nocdf is not None:
        plt.figure(figsize=(8, 6))
        c_flat = incr_cdf[~np.isnan(incr_cdf)].flatten()
        n_flat = incr_nocdf[~np.isnan(incr_nocdf)].flatten()
        plt.hist(n_flat, bins=50, alpha=0.5, label='NoCDF', density=True)
        plt.hist(c_flat, bins=50, alpha=0.5, label='CDF', density=True)
        plt.xlabel('Increment (m3/m3)')
        plt.ylabel('Density')
        plt.title('Distribution of soil moisture analysis increments under No-CDF and CDF assimilation')
        plt.legend()
        plt.savefig(f5, dpi=150)
        plt.close()
        generated_figures.append(f5)

    # 06
    print("  -> Generating 06_monthly_increment_boxplots_nocdf_vs_cdf_2016.png")
    f6 = os.path.join(out_dir, "06_monthly_increment_boxplots_nocdf_vs_cdf_2016.png")
    # Placeholder boxplot
    plt.figure(figsize=(10, 5))
    plt.text(0.5, 0.5, "Monthly Boxplots Placeholder", ha='center')
    plt.title('Monthly variability of SMAP-induced soil moisture increments under No-CDF and CDF assimilation')
    plt.savefig(f6, dpi=150)
    plt.close()
    generated_figures.append(f6)

    # 07
    print("  -> Generating 07_seasonal_increment_wet_dry_nocdf_vs_cdf_2016.png")
    f7 = os.path.join(out_dir, "07_seasonal_increment_wet_dry_nocdf_vs_cdf_2016.png")
    # Placeholder seasonal plot
    plt.figure(figsize=(10, 5))
    plt.text(0.5, 0.5, "Seasonal Wet/Dry Placeholder", ha='center')
    plt.title('Wet- and dry-season soil moisture increments under No-CDF and CDF assimilation')
    plt.savefig(f7, dpi=150)
    plt.close()
    generated_figures.append(f7)

    # 08
    print("  -> Generating 08_prior_ensemble_spread_nocdf_vs_cdf_2016.png")
    f8 = os.path.join(out_dir, "08_prior_ensemble_spread_nocdf_vs_cdf_2016.png")
    if spread_cdf is not None and spread_nocdf is not None:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(spread_nocdf, axis=0), mask), cmap='viridis', origin='lower')
        axes[0].set_title('NoCDF Prior Spread')
        im2 = axes[1].imshow(apply_mask(np.nanmean(spread_cdf, axis=0), mask), cmap='viridis', origin='lower')
        axes[1].set_title('CDF Prior Spread')
        fig.colorbar(im2, ax=axes, label='m3/m3')
        plt.suptitle('Prior ensemble spread for No-CDF and CDF assimilation experiments')
        plt.savefig(f8, dpi=150)
        plt.close()
        generated_figures.append(f8)

    # 09, 10, 11, 12 - Placeholders to complete the catalog logic without breaking due to missing posterior vars
    figures_to_stub = [
        ("09_posterior_ensemble_spread_nocdf_vs_cdf_2016.png", "Posterior ensemble spread after SMAP assimilation under No-CDF and CDF configurations"),
        ("10_spread_reduction_nocdf_vs_cdf_2016.png", "Reduction of ensemble spread after SMAP assimilation under No-CDF and CDF configurations"),
        ("11_normalized_innovation_nocdf_vs_cdf_2016.png", "Normalized innovation statistics for No-CDF and CDF SMAP assimilation"),
        ("12_innovation_increment_scatter_nocdf_vs_cdf_2016.png", "Relationship between SMAP innovations and analysis increments under No-CDF and CDF assimilation")
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
