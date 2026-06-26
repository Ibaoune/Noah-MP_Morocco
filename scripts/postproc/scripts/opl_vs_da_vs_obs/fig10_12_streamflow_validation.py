"""
fig10_12_streamflow_validation.py

Objective: Generate Figures 10 to 12 for the publication.
Compare simulated streamflow (HyMAP OL and DA) to in-situ observations.
Quantify the improvement brought by assimilation.
Calculates KGE, NSE, RMSE, Pearson correlation, and Relative Bias.

NOTE: HyMAP routing output and in-situ streamflow data are currently missing.
This script provides the skeleton workflow.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import config_postproc as config

def load_hymap_streamflow(dir_path, station_coords):
    """
    Placeholder to load HyMAP daily routed discharge.
    Needs to extract discharge at the specific grid cell closest to the station.
    """
    # e.g., ds = xr.open_mfdataset(dir_path + "/*.nc")
    # flow = ds['RiverFlow_tavg'].sel(lon=station_coords[0], lat=station_coords[1], method='nearest')
    # return flow.to_dataframe()
    return None

def load_insitu_streamflow(file_path):
    """
    Placeholder to load in-situ discharge timeseries.
    """
    # return pd.read_csv(file_path, index_col='Date', parse_dates=True)
    return None

def plot_hydrographs_and_metrics():
    print("This script is a skeleton. HyMAP and In-situ data must be present.")
    
    # -------------------------------------------------------------
    # Example Workflow (Uncomment when data is ready)
    # -------------------------------------------------------------
    # stations = {'Station_A': (-5.5, 34.0), 'Station_B': (-6.0, 33.5)}
    
    # for name, coords in stations.items():
    #     obs = load_insitu_streamflow(f"{config.DIR_OBS_INSITU}/{name}.csv")
    #     ol_flow = load_hymap_streamflow(config.DIR_OUTPUT_ROUTING_OL, coords)
    #     da_flow = load_hymap_streamflow(config.DIR_OUTPUT_ROUTING_DA, coords)
        
    #     if obs is not None and ol_flow is not None and da_flow is not None:
    #         # Align timeseries
    #         df = pd.concat([obs['Q'], ol_flow['Q'], da_flow['Q']], axis=1, keys=['OBS', 'OL', 'DA']).dropna()
            
    #         # Calculate Metrics
    #         kge_ol = config.calc_kge(df['OL'].values, df['OBS'].values)
    #         kge_da = config.calc_kge(df['DA'].values, df['OBS'].values)
    #         nse_ol = config.calc_nse(df['OL'].values, df['OBS'].values)
    #         nse_da = config.calc_nse(df['DA'].values, df['OBS'].values)
            
    #         # Plot Hydrograph
    #         plt.figure(figsize=(12, 6))
    #         plt.plot(df.index, df['OBS'], label='In Situ', color=config.COLORS['OBS'], linewidth=2)
    #         plt.plot(df.index, df['OL'], label=f'OL (KGE={kge_ol:.2f})', color=config.COLORS['OL'], linestyle='--')
    #         plt.plot(df.index, df['DA'], label=f'DA (KGE={kge_da:.2f})', color=config.COLORS['DA'])
            
    #         plt.title(f"Streamflow Validation at {name}", fontweight='bold')
    #         plt.ylabel("Discharge (m³/s)")
    #         plt.legend()
    #         plt.grid(True, linestyle='--', alpha=0.6)
    #         plt.tight_layout()
            
    #         output_path = os.path.join(config.DIR_FIGURES, f"fig10_12_hydrograph_{name}.png")
    #         plt.savefig(output_path)

    # Placeholder graphic
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, "Figures 10-12: Streamflow Validation\n(Requires HyMAP and In-situ data)", 
             ha='center', va='center', size=14)
    plt.axis('off')
    
    output_path = os.path.join(config.DIR_FIGURES_OPL_VS_DA, "fig10_12_streamflow_validation_placeholder.png")
    plt.savefig(output_path)
    print(f"Placeholder saved to: {output_path}")

if __name__ == "__main__":
    plot_hydrographs_and_metrics()
