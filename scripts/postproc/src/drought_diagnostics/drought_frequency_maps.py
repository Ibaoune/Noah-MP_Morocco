import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-parquet", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--reference-mode", default="pooled_2016_2020")
    parser.add_argument("--variable", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Running drought_frequency_maps.py for {args.variable}")
    out_dir_fig = os.path.join(args.output_root, "outputs", "figures", "drought_diagnostics")
    out_dir_tab = os.path.join(args.output_root, "outputs", "tables", "drought_diagnostics")
    
    if args.dry_run:
        print("[DRY RUN] Would generate maps and frequency tables.")
        exit(0)
        
    os.makedirs(out_dir_fig, exist_ok=True)
    os.makedirs(out_dir_tab, exist_ok=True)
    
    in_file = os.path.join(args.output_root, "outputs", "tables", "drought_diagnostics", f"drought_percentiles_pixel_month_2016_2020_{args.variable}.parquet")
    if not os.path.exists(in_file):
        print(f"Missing {in_file}")
        exit(1)
        
    df = pd.read_parquet(in_file)
    
    # Compute frequency of D1
    freq = df.groupby(['north_south', 'east_west', 'experiment'])['is_D1'].mean().reset_index()
    freq.rename(columns={'is_D1': 'drought_frequency_percent'}, inplace=True)
    freq['drought_frequency_percent'] *= 100
    freq['variable'] = args.variable
    freq['drought_threshold'] = 'D1'
    
    tab_out = os.path.join(out_dir_tab, f"drought_frequency_summary_2016_2020_{args.variable}.csv")
    freq.to_csv(tab_out, index=False)
    
    # Plot simple map representation (scatter since we just have ns/ew indices for now)
    # This is a basic plot for V0
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    exps = ["OPL", "DA-NoCDF", "DA-CDF"]
    for i, exp in enumerate(exps):
        sub = freq[freq['experiment'] == exp]
        if not sub.empty:
            sc = axes[i].scatter(sub['east_west'], sub['north_south'], c=sub['drought_frequency_percent'], cmap='YlOrRd', vmin=0, vmax=30)
            axes[i].set_title(f"{exp} ({args.variable})")
            axes[i].axis('off')
    
    cbar = plt.colorbar(sc, ax=axes, orientation='horizontal', fraction=0.05)
    cbar.set_label('Drought Frequency (D1) %')
    plt.suptitle(f"Relative drought diagnostic (D1), 2016-2020 reference")
    
    fig_out = os.path.join(out_dir_fig, f"manuscript_drought_frequency_{args.variable}_OPL_DA_NoCDF_DA_CDF_2016_2020.png")
    plt.savefig(fig_out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved {fig_out} and table.")
