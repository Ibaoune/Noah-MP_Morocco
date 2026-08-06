# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.fluxes.plot_fluxes
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

def run_fluxes_diagnostics(data_dict, out_dir):
    """
    Bloc 3: Fluxes
    Objectif: Vérifier l'impact sur l'évapotranspiration et ses composantes.
    """
    generated_figures = []
    
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    if not files_ol:
        return generated_figures

    mask = get_landmask(files_ol)
    var_et = 'Evap_tavg'
    mult_et = 86400.0 # Convert kg/m2/s to mm/day
    
    print("Loading Evap_tavg...")
    data_et_ol = load_lis_variable(files_ol, var_et)
    data_et_nocdf = load_lis_variable(files_nocdf, var_et) if files_nocdf else None
    data_et_cdf = load_lis_variable(files_cdf, var_et) if files_cdf else None

    def apply_mask(data, mask):
        if data is None or mask is None:
            return None
        return np.where(mask, data, np.nan)

    if data_et_ol is not None:
        et_ol = data_et_ol * mult_et
        et_nocdf = data_et_nocdf * mult_et if data_et_nocdf is not None else None
        et_cdf = data_et_cdf * mult_et if data_et_cdf is not None else None

        # 23: Mean ET
        print("  -> Generating 23_evapotranspiration_mean_opl_nocdf_cdf_2016.png")
        f23 = os.path.join(out_dir, "23_evapotranspiration_mean_opl_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(et_ol, axis=0), mask), cmap='viridis', origin='lower')
        axes[0].set_title('OPL ET')
        if et_nocdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(et_nocdf, axis=0), mask), cmap='viridis', origin='lower')
            axes[1].set_title('NoCDF ET')
        if et_cdf is not None:
            im3 = axes[2].imshow(apply_mask(np.nanmean(et_cdf, axis=0), mask), cmap='viridis', origin='lower')
            axes[2].set_title('CDF ET')
        fig.colorbar(im1, ax=axes, label='ET (mm/day)')
        plt.suptitle('Mean evapotranspiration in OPL, DA-NoCDF and DA-CDF experiments')
        plt.savefig(f23, dpi=150)
        plt.close()
        generated_figures.append(f23)

        # 24: ET Differences
        print("  -> Generating 24_evapotranspiration_differences_2016.png")
        f24 = os.path.join(out_dir, "24_evapotranspiration_differences_2016.png")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if et_nocdf is not None:
            im1 = axes[0].imshow(apply_mask(np.nanmean(et_nocdf - et_ol, axis=0), mask), cmap='RdBu', vmin=-1, vmax=1, origin='lower')
            axes[0].set_title('NoCDF - OPL ET')
        if et_cdf is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(et_cdf - et_ol, axis=0), mask), cmap='RdBu', vmin=-1, vmax=1, origin='lower')
            axes[1].set_title('CDF - OPL ET')
        fig.colorbar(im1, ax=axes, label='Delta ET (mm/day)')
        plt.suptitle('Impact of No-CDF and CDF SMAP assimilation on evapotranspiration')
        plt.savefig(f24, dpi=150)
        plt.close()
        generated_figures.append(f24)

        # 25: ET Timeseries
        print("  -> Generating 25_evapotranspiration_timeseries_2016.png")
        f25 = os.path.join(out_dir, "25_evapotranspiration_timeseries_2016.png")
        plt.figure(figsize=(10, 4))
        plt.plot(calculate_basin_average(et_ol, mask), label='OPL')
        if et_nocdf is not None:
            plt.plot(calculate_basin_average(et_nocdf, mask), label='NoCDF')
        if et_cdf is not None:
            plt.plot(calculate_basin_average(et_cdf, mask), label='CDF')
        plt.legend()
        plt.title('Basin-averaged evapotranspiration response to SMAP assimilation')
        plt.grid(True)
        plt.savefig(f25, dpi=150)
        plt.close()
        generated_figures.append(f25)

    # 26, 27, 28, 29, 30 - Placeholders
    figures_to_stub = [
        ("26_transpiration_mean_and_differences_2016.png", "Transpiration response to No-CDF and CDF SMAP assimilation"),
        ("27_soil_evaporation_mean_and_differences_2016.png", "Soil evaporation response to No-CDF and CDF SMAP assimilation"),
        ("28_transpiration_fraction_t_over_et_2016.png", "Impact of SMAP assimilation on the transpiration fraction T/ET"),
        ("29_latent_heat_sensible_heat_response_2016.png", "Energy flux response to No-CDF and CDF SMAP assimilation"),
        ("30_water_energy_flux_timeseries_2016.png", "Basin-averaged water and energy fluxes under OPL, DA-NoCDF and DA-CDF experiments")
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
