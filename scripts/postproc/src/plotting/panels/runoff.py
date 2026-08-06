# Author: M. EL Aabaribaoune (@um6p)

"""
Builders for runoff partitioning and GLDAS intercomparison (RUNOFF-01, GLDAS-01).
"""
import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def build_runoff_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the RUNOFF-01 figure showing runoff partitioning (surface vs baseflow).
    """
    logger.info("Building RUNOFF-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    fig.suptitle("RUNOFF-01: Runoff Partitioning", fontsize=16)
    
    titles = [
        "a. Precipitation", "b. Baseflow Fraction OPL", 
        "c. Total Runoff DA-CDF - OPL", "d. Baseflow DA-CDF - OPL",
        "e. Surface Runoff DA-CDF - OPL", "f. Wet vs Dry Season"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "RUNOFF-01_runoff_partitioning.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]

def build_gldas_01(recipe, experiments_catalog, global_cfg, data_products=None, out_dir=None):
    """
    Builds the GLDAS-01 figure for intercomparison.
    """
    logger.info("Building GLDAS-01 figure")
    if out_dir is None:
        out_dir = global_cfg.get('paths', {}).get('figure_root', 'outputs/figures')
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("GLDAS-01: Intercomparison with GLDAS Products", fontsize=16)
    
    titles = [
        "a. Runoff OPL vs GLDAS Envelope", "b. Runoff DA-CDF vs GLDAS",
        "c. Runoff DA-NoCDF vs GLDAS", "d. Baseflow Comparison"
    ]
    
    for ax, title in zip(axes.flatten(), titles):
        ax.text(0.5, 0.5, title, ha='center', va='center')
        ax.axis('off')
        
    plt.tight_layout()
    output_path = os.path.join(out_dir, "GLDAS-01_gldas_intercomparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    return [output_path]
