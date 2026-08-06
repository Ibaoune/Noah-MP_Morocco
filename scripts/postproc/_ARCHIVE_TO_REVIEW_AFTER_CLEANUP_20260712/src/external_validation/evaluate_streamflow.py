# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: external_validation.evaluate_streamflow
Description: Validation of model outputs against external observational datasets.
================================================================================
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Append utils to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
import metrics

def run(cfg):
    print("--- Running Streamflow Validation ---")
    plt.rcParams.update(cfg.PLOT_RC_PARAMS)
    
    if not os.path.exists(cfg.DIR_OBS_INSITU):
        print(f"  -> Warning: Streamflow observations directory not found at {cfg.DIR_OBS_INSITU}. Plotting skeleton.")
    else:
        print(f"  -> Found Streamflow observations directory: {cfg.DIR_OBS_INSITU}")
        
    # Skeleton implementation (ready to be filled with actual data loading)
    
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, "Figures 10-12: Streamflow Validation\n(Requires HyMAP routing outputs and In-situ data matching)", 
             ha='center', va='center', size=14)
    plt.axis('off')
    
    output_path = os.path.join(cfg.DIR_FIGURES, "streamflow_validation_placeholder.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    
    print(f"  -> Saved placeholder: {output_path}")
    print("--- Streamflow Validation Completed ---\n")
