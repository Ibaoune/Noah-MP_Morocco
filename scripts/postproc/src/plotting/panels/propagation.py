# Author: M. EL Aabaribaoune (@um6p)

"""
Builder for the propagation manuscript figure (PROP-01).
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_prop_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the PROP-01 figure showing drought propagation (P -> SSM -> RZSM -> Q).
    """
    logger.info("Building PROP-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    fig.suptitle("PROP-01: Hydrological Drought Propagation", fontsize=16)
    
    titles = [
        "a. Normalized Time Series OPL", "b. Propagation Matrix OPL", 
        "c. Lag Matrix OPL", "d. Lag Changes (DA - OPL)",
        "e. Dominant Lag Map", "f. Wet vs Dry Season Synthesis"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "PROP-01_drought_propagation.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
