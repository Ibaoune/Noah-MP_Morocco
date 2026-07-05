import os
from .plot_hydrographs import plot_hymap_streamflow

def run_hymap_validation(data_dict, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    f1 = os.path.join(out_dir, "06_hymap_streamflow.png")
    plot_hymap_streamflow(data_dict, f1)
    
    return [f1]
