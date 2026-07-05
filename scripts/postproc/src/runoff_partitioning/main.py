"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: runoff_partitioning.main
Description: Analysis of runoff partitioning and hydrological water balance.
================================================================================
"""
import os
from .plot_runoff_timeseries import plot_runoff_partitioning

def run_runoff_partitioning(data_dict, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    f1 = os.path.join(out_dir, "05_runoff_partitioning.png")
    plot_runoff_partitioning(data_dict, f1)
    
    return [f1]
