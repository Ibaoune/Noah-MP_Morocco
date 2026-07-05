import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def run_soil_moisture_diagnostics(data_dict, out_dir):
    """
    Bloc 2: Soil Moisture
    Objectif: Vérifier si les différences NoCDF/CDF se propagent aux états du sol.
    """
    generated_figures = []
    
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    
    if not files_ol:
        return generated_figures

    mask = get_landmask(files_ol)
    var_sm = 'SoilMoist_tavg'
    
    print("Loading SoilMoist_tavg...")
    data_sm_ol = load_lis_variable(files_ol, var_sm)
    data_sm_nocdf = load_lis_variable(files_nocdf, var_sm) if files_nocdf else None
    data_sm_cdf = load_lis_variable(files_cdf, var_sm) if files_cdf else None
    
    def apply_mask(data, mask):
        if data is None or mask is None:
            return None
        return np.where(mask, data, np.nan)

    # L1 represents Surface Soil Moisture
    if data_sm_ol is not None:
        sm_ol_l1 = data_sm_ol[:, 0, :, :]
        sm_nocdf_l1 = data_sm_nocdf[:, 0, :, :] if data_sm_nocdf is not None else None
        sm_cdf_l1 = data_sm_cdf[:, 0, :, :] if data_sm_cdf is not None else None

        # 13: Mean SSM
        print("  -> Generating 13_surface_soil_moisture_mean_opl_nocdf_cdf_2016.png")
        f13 = os.path.join(out_dir, "13_surface_soil_moisture_mean_opl_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        im1 = axes[0].imshow(apply_mask(np.nanmean(sm_ol_l1, axis=0), mask), cmap='viridis', vmin=0, vmax=0.4, origin='lower')
        axes[0].set_title('OPL SSM')
        if sm_nocdf_l1 is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(sm_nocdf_l1, axis=0), mask), cmap='viridis', vmin=0, vmax=0.4, origin='lower')
            axes[1].set_title('NoCDF SSM')
        if sm_cdf_l1 is not None:
            im3 = axes[2].imshow(apply_mask(np.nanmean(sm_cdf_l1, axis=0), mask), cmap='viridis', vmin=0, vmax=0.4, origin='lower')
            axes[2].set_title('CDF SSM')
        fig.colorbar(im1, ax=axes, label='SSM (m3/m3)')
        plt.suptitle('Mean surface soil moisture in OPL, DA-NoCDF and DA-CDF experiments')
        plt.savefig(f13, dpi=150)
        plt.close()
        generated_figures.append(f13)

        # 14: SSM Differences
        print("  -> Generating 14_surface_soil_moisture_differences_nocdf_cdf_2016.png")
        f14 = os.path.join(out_dir, "14_surface_soil_moisture_differences_nocdf_cdf_2016.png")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if sm_nocdf_l1 is not None:
            im1 = axes[0].imshow(apply_mask(np.nanmean(sm_nocdf_l1 - sm_ol_l1, axis=0), mask), cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower')
            axes[0].set_title('NoCDF - OPL SSM')
        if sm_cdf_l1 is not None:
            im2 = axes[1].imshow(apply_mask(np.nanmean(sm_cdf_l1 - sm_ol_l1, axis=0), mask), cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower')
            axes[1].set_title('CDF - OPL SSM')
        fig.colorbar(im1, ax=axes, label='Delta SSM (m3/m3)')
        plt.suptitle('Impact of No-CDF and CDF assimilation on surface soil moisture')
        plt.savefig(f14, dpi=150)
        plt.close()
        generated_figures.append(f14)

        # 15: SSM Timeseries
        print("  -> Generating 15_surface_soil_moisture_timeseries_2016.png")
        f15 = os.path.join(out_dir, "15_surface_soil_moisture_timeseries_2016.png")
        plt.figure(figsize=(10, 4))
        plt.plot(calculate_basin_average(sm_ol_l1, mask), label='OPL')
        if sm_nocdf_l1 is not None:
            plt.plot(calculate_basin_average(sm_nocdf_l1, mask), label='NoCDF')
        if sm_cdf_l1 is not None:
            plt.plot(calculate_basin_average(sm_cdf_l1, mask), label='CDF')
        plt.legend()
        plt.title('Basin-averaged surface soil moisture time series for OPL, DA-NoCDF and DA-CDF')
        plt.grid(True)
        plt.savefig(f15, dpi=150)
        plt.close()
        generated_figures.append(f15)

    # 16, 17, 18, 19, 20, 21, 22 - Placeholders and other logic
    figures_to_stub = [
        ("16_soil_moisture_layer_timeseries_2016.png", "Vertical propagation of SMAP assimilation increments across Noah-MP soil layers"),
        ("17_soil_moisture_layer_differences_2016.png", "Layer-wise soil moisture differences induced by No-CDF and CDF assimilation"),
        ("18_rootzone_soil_moisture_mean_opl_nocdf_cdf_2016.png", "Mean root-zone soil moisture in OPL, DA-NoCDF and DA-CDF experiments"),
        ("19_rootzone_soil_moisture_differences_2016.png", "Root-zone soil moisture response to No-CDF and CDF SMAP assimilation"),
        ("20_rootzone_soil_moisture_timeseries_2016.png", "Basin-averaged root-zone soil moisture response to SMAP assimilation"),
        ("21_vertical_profile_sm_increment_wet_dry_2016.png", "Seasonal vertical profile of soil moisture increments under No-CDF and CDF assimilation"),
        ("22_soil_moisture_variability_violinplots_2016.png", "Seasonal distribution of soil moisture states in OPL, DA-NoCDF and DA-CDF experiments")
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
