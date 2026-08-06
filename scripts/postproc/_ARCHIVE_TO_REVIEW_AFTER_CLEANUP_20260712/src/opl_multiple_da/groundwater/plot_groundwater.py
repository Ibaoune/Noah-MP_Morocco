# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.groundwater.plot_groundwater
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def run_groundwater_diagnostics(data_dict, out_dir):
    """
    Bloc 4: Groundwater
    Objectif: Évaluer la propagation vers les stockages profonds.
    """
    generated_figures = []
    
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    if not files_ol:
        return generated_figures

    mask = get_landmask(files_ol)
    var_gws = 'GWS_tavg'
    
    print("Loading GWS_tavg...")
    data_gws_ol = load_lis_variable(files_ol, var_gws)
    data_gws_nocdf = load_lis_variable(files_nocdf, var_gws) if files_nocdf else None
    data_gws_cdf = load_lis_variable(files_cdf, var_gws) if files_cdf else None

    def apply_mask(data, mask):
        if data is None or mask is None:
            return None
        return np.where(mask, data, np.nan)

    if data_gws_ol is not None:
        # 31: Mean GWS
        print("  -> Generating 31_groundwater_storage_mean_opl_nocdf_cdf_2016.png")
        f31 = os.path.join(out_dir, "31_groundwater_storage_mean_opl_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(data_gws_ol, axis=0), mask), cmap='Blues', origin='lower')
        axes[0].set_title('OPL GWS')
        if data_gws_nocdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(data_gws_nocdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[1].set_title('NoCDF GWS')
        if data_gws_cdf is not None:
            im3 = axes[2].imshow(apply_mask(np.nanmean(data_gws_cdf, axis=0), mask), cmap='Blues', origin='lower')
            axes[2].set_title('CDF GWS')
        fig.colorbar(im1, ax=axes, label='GWS (mm)')
        plt.suptitle('Mean groundwater storage in OPL, DA-NoCDF and DA-CDF experiments')
        plt.savefig(f31, dpi=150)
        plt.close()
        generated_figures.append(f31)

        # 32: GWS Differences
        print("  -> Generating 32_groundwater_storage_differences_2016.png")
        f32 = os.path.join(out_dir, "32_groundwater_storage_differences_2016.png")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if data_gws_nocdf is not None:
            im1 = axes[0].imshow(apply_mask(np.nanmean(data_gws_nocdf - data_gws_ol, axis=0), mask), cmap='RdBu', origin='lower')
            axes[0].set_title('NoCDF - OPL GWS')
        if data_gws_cdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(data_gws_cdf - data_gws_ol, axis=0), mask), cmap='RdBu', origin='lower')
            axes[1].set_title('CDF - OPL GWS')
        fig.colorbar(im1, ax=axes, label='Delta GWS (mm)')
        plt.suptitle('Groundwater storage response to No-CDF and CDF SMAP assimilation')
        plt.savefig(f32, dpi=150)
        plt.close()
        generated_figures.append(f32)

        # 33: GWS Timeseries
        print("  -> Generating 33_groundwater_storage_timeseries_2016.png")
        f33 = os.path.join(out_dir, "33_groundwater_storage_timeseries_2016.png")
        plt.figure(figsize=(10, 4))
        plt.plot(calculate_basin_average(data_gws_ol, mask), label='OPL')
        if data_gws_nocdf is not None:
            plt.plot(calculate_basin_average(data_gws_nocdf, mask), label='NoCDF')
        if data_gws_cdf is not None:
            plt.plot(calculate_basin_average(data_gws_cdf, mask), label='CDF')
        plt.legend()
        plt.title('Basin-averaged groundwater storage response to SMAP assimilation')
        plt.grid(True)
        plt.savefig(f33, dpi=150)
        plt.close()
        generated_figures.append(f33)

    # 34, 35 - Placeholders
    figures_to_stub = [
        ("34_water_table_depth_response_2016.png", "Water table depth response to No-CDF and CDF SMAP assimilation"),
        ("35_rzsm_vs_groundwater_storage_scatter_2016.png", "Relationship between root-zone soil moisture changes and groundwater storage response")
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
