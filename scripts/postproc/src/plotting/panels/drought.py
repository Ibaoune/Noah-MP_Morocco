# Author: M. EL Aabaribaoune (@um6p)

"""
Builder for the DROUGHT-01 manuscript figure.
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_drought_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the DROUGHT-01 figure showing drought frequency, anomalies, and transitions.
    """
    logger.info("Building DROUGHT-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    fig.suptitle("DROUGHT-01: Drought Frequency and Transitions", fontsize=16)
    
    titles = [
        "a. Drought Freq OPL", "b. Transition Matrix", 
        "c. Drought Freq DA-CDF", "d. DA-CDF minus OPL",
        "e. Drought Freq DA-NoCDF", "f. DA-NoCDF minus OPL"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "DROUGHT-01_drought_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
