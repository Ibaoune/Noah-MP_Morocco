import os
from .plot_basin_timeseries import plot_vertical_propagation

def run_opl_vs_da(data_dict, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    f1 = os.path.join(out_dir, "04_vertical_propagation.png")
    plot_vertical_propagation(data_dict, f1)
    
    return [f1]
