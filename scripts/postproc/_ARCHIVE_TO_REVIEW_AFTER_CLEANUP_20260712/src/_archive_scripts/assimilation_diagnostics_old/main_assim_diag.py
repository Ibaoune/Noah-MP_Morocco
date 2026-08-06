# Author: M. EL Aabaribaoune (@um6p)

import os
import sys

from .plot_obs_coverage import plot_smap_obs_coverage
from .plot_innovation import plot_innovation_increment

def run_assimilation_diagnostics(data_dict, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    f_list = plot_smap_obs_coverage(data_dict, out_dir)
    if not f_list: f_list = []
    
    f2_list = plot_innovation_increment(data_dict, out_dir)
    if not f2_list: f2_list = []
    
    return f_list + f2_list
