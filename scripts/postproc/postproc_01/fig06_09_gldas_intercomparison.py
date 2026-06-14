"""
fig06_09_gldas_intercomparison.py

Objective: Generate Figures 6 to 9 for the publication.
Compare local LIS simulations to reference models: GLDAS_NOAH, GLDAS_VIC, GLDAS_CLSM, GLDAS_CLSM_DA.
Produces spatial maps, scatter plots, and spatial statistics (Bias, RMSE, Correlation).

NOTE: GLDAS data is currently missing. Please ensure the data is downloaded
to the path specified in config.py before running this script for the full period.
"""

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config

def load_gldas(model_name):
    """
    Placeholder to load GLDAS data.
    """
    # path = os.path.join(config.DIR_OBS_GLDAS, model_name, "*.nc4")
    # ds = xr.open_mfdataset(path)
    # return ds
    print(f"GLDAS data for {model_name} not found in {config.DIR_OBS_GLDAS}")
    return None

def regrid_to_gldas(lis_ds, gldas_ds):
    """
    Upscale high-resolution LIS outputs to GLDAS resolution (e.25 or 1 degree).
    Requires xesmf or simple xarray interp.
    """
    # Example using xarray interp:
    # return lis_ds.interp(lat=gldas_ds.lat, lon=gldas_ds.lon, method='linear')
    pass

def plot_gldas_intercomparison():
    print("This script is a skeleton. GLDAS data must be downloaded first.")
    
    # -------------------------------------------------------------
    # Example Logic (Uncomment and adapt when data is available)
    # -------------------------------------------------------------
    
    # models = ['NOAH025', 'VIC10', 'CLSM10', 'CLSM025_DA']
    # gldas_data = {m: load_gldas(m) for m in models}
    
    # lis_ol = load_lis_outputs(config.DIR_OUTPUT_OL)
    # lis_da = load_lis_outputs(config.DIR_OUTPUT_DA)
    
    # for model in models:
    #     if gldas_data[model] is not None:
    #         # Regrid LIS to GLDAS grid
    #         lis_da_regridded = regrid_to_gldas(lis_da, gldas_data[model])
            
    #         # Calculate metrics
    #         bias = config.calc_bias(lis_da_regridded['SoilMoist_tavg'], gldas_data[model]['SoilMoi0_10cm_inst'])
    #         rmse = config.calc_rmse(lis_da_regridded['SoilMoist_tavg'], gldas_data[model]['SoilMoi0_10cm_inst'])
            
    #         # Plotting Logic Here
    #         # ...
    
    # Create an empty placeholder figure to indicate the script exists
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, "Figures 6-9: GLDAS Intercomparison\n(Requires GLDAS NetCDF data)", 
             ha='center', va='center', size=14)
    plt.axis('off')
    
    output_path = os.path.join(config.DIR_FIGURES, "fig06_09_gldas_intercomparison_placeholder.png")
    plt.savefig(output_path)
    print(f"Placeholder saved to: {output_path}")

if __name__ == "__main__":
    plot_gldas_intercomparison()
