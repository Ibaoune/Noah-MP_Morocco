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

    print(f"Running drought_by_landcover.py for {args.variable}")
    out_dir_fig = os.path.join(args.output_root, "figures", "drought_diagnostics")
    out_dir_tab = os.path.join(args.output_root, "tables", "drought_diagnostics")
    
    if args.dry_run:
        print("[DRY RUN] Would generate landcover stat tables.")
        exit(0)
        
    in_file = os.path.join(args.output_root, "tables", "drought_diagnostics", f"drought_percentiles_pixel_month_2016_2020_{args.variable}.parquet")
    if not os.path.exists(in_file):
        print(f"Missing {in_file}")
        exit(1)
        
    df = pd.read_parquet(in_file)
    
    if 'land_cover' not in df.columns:
        print("No land_cover column found. Skipping land_cover analysis.")
        exit(0)
        
    df['time'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')
    total_pixels = df.groupby(['time', 'experiment', 'land_cover'])['value'].count().reset_index(name='n_total_pixels')
    
    d1 = df.groupby(['time', 'experiment', 'land_cover'])['is_D1'].sum().reset_index(name='n_drought_pixels')
    d1 = d1.merge(total_pixels, on=['time', 'experiment', 'land_cover'])
    d1['drought_area_percent'] = (d1['n_drought_pixels'] / d1['n_total_pixels']) * 100
    
    mean_area = d1.groupby(['land_cover', 'experiment'])['drought_area_percent'].agg(['mean', 'std']).reset_index()
    mean_area.rename(columns={'mean': 'drought_area_percent_mean', 'std': 'drought_area_percent_std'}, inplace=True)
    mean_area['drought_threshold'] = 'D1'
    mean_area['variable'] = args.variable
    
    tab_out = os.path.join(out_dir_tab, f"drought_by_landcover_summary_2016_2020_{args.variable}.csv")
    mean_area.to_csv(tab_out, index=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=mean_area, x='land_cover', y='drought_area_percent_mean', hue='experiment')
    plt.title(f"Mean Drought Area (D1) by Land Cover ({args.variable})")
    plt.ylabel('Mean Drought Area (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig_out = os.path.join(out_dir_fig, f"manuscript_drought_by_landcover_{args.variable}_2016_2020.png")
    plt.savefig(fig_out, dpi=300, facecolor='white')
    plt.close()
    
    print(f"Saved {fig_out} and table.")
