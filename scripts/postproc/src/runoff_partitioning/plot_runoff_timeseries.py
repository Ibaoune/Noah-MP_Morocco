import os
import sys
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def plot_runoff_partitioning(data_dict, out_file):
    print("Generating Runoff Partitioning figure...")
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    
    mask = get_landmask(files_ol)
    
    variables = {
        'Surface Runoff (Qs) [mm/day]': 'Qs_tavg', 
        'Baseflow (Qsb) [mm/day]': 'Qsb_tavg'
    }
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle("Runoff Partitioning", fontsize=16)
    
    ol_ts = {}
    da_ts = {}
    
    for i, (title, var) in enumerate(variables.items()):
        ax = axes[i]
        
        # OPL
        data_ol = load_lis_variable(files_ol, var, extract_layer=None)
        if data_ol is not None:
            ts_ol = calculate_basin_average(data_ol * 86400.0, mask)
            ax.plot(ts_ol, label='OPL', color='black')
            ol_ts[var] = ts_ol
            
        # DA_nocdf
        data_da = load_lis_variable(files_nocdf, var, extract_layer=None)
        if data_da is not None:
            ts_da = calculate_basin_average(data_da * 86400.0, mask)
            ax.plot(ts_da, label='DA_nocdf', color='blue')
            da_ts[var] = ts_da
            
        ax.set_title(f"{title} (Basin Average)")
        ax.legend()
        ax.grid(True)
        
    # Baseflow fraction
    ax3 = axes[2]
    if 'Qs_tavg' in ol_ts and 'Qsb_tavg' in ol_ts:
        ol_fraction = np.where((ol_ts['Qs_tavg'] + ol_ts['Qsb_tavg']) > 0, 
                                ol_ts['Qsb_tavg'] / (ol_ts['Qs_tavg'] + ol_ts['Qsb_tavg']), np.nan)
        ax3.plot(ol_fraction, label='OPL', color='black')
        
    if 'Qs_tavg' in da_ts and 'Qsb_tavg' in da_ts:
        da_fraction = np.where((da_ts['Qs_tavg'] + da_ts['Qsb_tavg']) > 0, 
                                da_ts['Qsb_tavg'] / (da_ts['Qs_tavg'] + da_ts['Qsb_tavg']), np.nan)
        ax3.plot(da_fraction, label='DA_nocdf', color='blue')
        
    ax3.set_title("Baseflow Fraction (Qsb / Total Runoff)")
    ax3.legend()
    ax3.grid(True)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(out_file, dpi=150)
    plt.close()
    return out_file
