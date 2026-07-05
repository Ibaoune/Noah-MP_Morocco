import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def plot_vertical_propagation(data_dict, out_file):
    print("Generating Vertical Propagation & Surface Fluxes figure...")
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    
    mask = get_landmask(files_ol)
    
    variables = {
        'Surface SM (m3/m3)': ('SoilMoist_tavg', 0, 1.0),
        'Root Zone SM (m3/m3)': ('SoilMoist_tavg', 1, 1.0),
        'Evapotranspiration (mm/day)': ('Evap_tavg', None, 86400.0)
    }
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle("Vertical Propagation & Surface Flux Coherence", fontsize=16)
    
    for i, (title, (var, layer, mult)) in enumerate(variables.items()):
        ax = axes[i]
        
        # OPL
        data_ol = load_lis_variable(files_ol, var, extract_layer=layer)
        if data_ol is not None:
            ts_ol = calculate_basin_average(data_ol * mult, mask)
            ax.plot(ts_ol, label='OPL', color='black')
            
        # DA_nocdf
        data_da = load_lis_variable(files_nocdf, var, extract_layer=layer)
        if data_da is not None:
            ts_da = calculate_basin_average(data_da * mult, mask)
            ax.plot(ts_da, label='DA_nocdf', color='blue')
            
        ax.set_title(f"{title} (Basin Average)")
        ax.legend()
        ax.grid(True)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file
