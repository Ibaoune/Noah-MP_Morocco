import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run(cfg):
    print("--- Running GLDAS Comparison ---")
    plt.rcParams.update(cfg.PLOT_RC_PARAMS)
    
    if not os.path.exists(cfg.DIR_OBS_GLDAS):
        print(f"  -> Warning: GLDAS directory not found at {cfg.DIR_OBS_GLDAS}. Plotting skeleton.")
    else:
        print(f"  -> Found GLDAS dataset directory: {cfg.DIR_OBS_GLDAS}")
        
    # Skeleton implementation
    
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, "Figures 6-9: GLDAS LSM\n(Requires GLDAS NetCDF data extraction logic)", 
             ha='center', va='center', size=14)
    plt.axis('off')
    
    output_path = os.path.join(cfg.DIR_FIGURES, "gldas_lsm_placeholder.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    
    print(f"  -> Saved placeholder: {output_path}")
    print("--- GLDAS Comparison Completed ---\n")
