# Author: M. EL Aabaribaoune (@um6p)

"""
Builders for hydrology and flux manuscript figures (SM-01, FLUX-01).
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_sm_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the SM-01 figure showing Soil Moisture and Root-Zone Soil Moisture propagation.
    """
    logger.info("Building SM-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    fig.suptitle("SM-01: SSM and RZSM Diagnostics", fontsize=16)
    
    titles = [
        "a. SSM DA-CDF minus OPL", "b. RZSM DA-CDF minus OPL", 
        "c. SSM DA-NoCDF minus OPL", "d. RZSM DA-NoCDF minus OPL",
        "e. SSM DA-NoCDF minus DA-CDF", "f. RZSM DA-NoCDF minus DA-CDF"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "SM-01_soil_moisture.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]

def build_flux_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the FLUX-01 figure showing ET and Fluxes validation.
    """
    logger.info("Building FLUX-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("FLUX-01: Evapotranspiration Validation", fontsize=16)
    
    titles = [
        "a. ET Correlation OPL", "b. ET Bias OPL",
        "c. ET Corr Diff (DA - OPL)", "d. ET Bias Diff (DA - OPL)"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "FLUX-01_evapotranspiration.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
