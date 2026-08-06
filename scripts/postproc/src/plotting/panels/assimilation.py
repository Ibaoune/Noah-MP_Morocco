# Author: M. EL Aabaribaoune (@um6p)

"""
Builder for the ASSIM-01 manuscript figure.
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_assim_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the ASSIM-01 figure showing assimilation diagnostics.
    Panels:
    a. nombre ou fréquence d'observations assimilées
    b. innovation moyenne NoCDF
    c. innovation moyenne CDF
    d. incrément moyen NoCDF
    e. incrément moyen CDF
    f. distribution des incréments
    g. incréments pendant la saison humide
    h. incréments pendant la saison sèche
    """
    logger.info("Building ASSIM-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a placeholder figure for now
    fig, axes = plt.subplots(4, 2, figsize=(10, 15))
    fig.suptitle("ASSIM-01: Assimilation Diagnostics", fontsize=16)
    
    titles = [
        "a. Obs assimilated", "b. Mean Innov NoCDF", 
        "c. Mean Innov CDF", "d. Mean Incr NoCDF",
        "e. Mean Incr CDF", "f. Increment Dist",
        "g. Wet Season Incr", "h. Dry Season Incr"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    
    output_path = os.path.join(out_dir, "ASSIM-01_assimilation_diagnostics.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
