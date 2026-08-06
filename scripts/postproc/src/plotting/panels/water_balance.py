# Author: M. EL Aabaribaoune (@um6p)

"""
Builder for the water balance manuscript figure (WB-01).
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_wb_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the WB-01 figure showing water balance and plausibility flags.
    """
    logger.info("Building WB-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    fig.suptitle("WB-01: Water Balance and DA Plausibility", fontsize=16)
    
    titles = [
        "a. Mean Budget OPL", "b. Mean Budget DA-CDF", 
        "c. Annual Residual", "d. Seasonal Residual",
        "e. DA-NoCDF Residual Map", "f. Hydrologically Ambiguous Zones"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "WB-01_water_balance.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
