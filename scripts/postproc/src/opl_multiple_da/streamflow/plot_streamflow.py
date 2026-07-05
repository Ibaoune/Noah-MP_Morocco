import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def run_streamflow_diagnostics(data_dict, out_dir):
    """
    Bloc 6: Streamflow
    Objectif: Répondre à la question "Les différences sont-elles visibles jusqu'au débit ?"
    """
    generated_figures = []
    
    figures_to_stub = [
        ("49_selected_station_daily_hydrographs_2016.png", "Daily HyMAP-routed streamflow at selected gauges: observations, OPL, DA-NoCDF and DA-CDF"),
        ("50_selected_station_monthly_hydrographs_2016.png", "Monthly HyMAP-routed streamflow at selected gauges under OPL and SMAP assimilation experiments"),
        ("51_flow_duration_curves_selected_stations_2016.png", "Flow duration curves for observed and simulated streamflow at selected gauges"),
        ("52_streamflow_scatter_obs_vs_sim_2016.png", "Observed versus simulated daily streamflow for OPL, DA-NoCDF and DA-CDF"),
        ("53_streamflow_skill_metrics_by_station_2016.png", "Streamflow skill metrics by station for OPL, DA-NoCDF and DA-CDF"),
        ("54_station_map_streamflow_skill_improvement_2016.png", "Spatial distribution of streamflow skill changes induced by SMAP assimilation"),
        ("55_low_flow_high_flow_bias_2016.png", "Low-flow and high-flow bias diagnostics for HyMAP-routed streamflow"),
        ("56_cumulative_streamflow_volume_2016.png", "Cumulative streamflow volume at selected gauges under OPL, DA-NoCDF and DA-CDF"),
        ("57_hydrographs_by_station_typology_2016.png", "Streamflow response to SMAP assimilation across station typologies")
    ]
    
    print("  -> Generating placeholders for Streamflow (Data missing)")
    for fn, title in figures_to_stub:
        p = os.path.join(out_dir, fn)
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, "Placeholder\n(Awaiting HyMAP / Station Data)", ha='center', va='center')
        plt.title(title)
        plt.savefig(p, dpi=150)
        plt.close()
        generated_figures.append(p)

    return generated_figures
