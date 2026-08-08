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

    print(f"Running drought_area_timeseries.py for {args.variable}")
    out_dir_fig = os.path.join(args.output_root, "figures", "drought_diagnostics")
    out_dir_tab = os.path.join(args.output_root, "tables", "drought_diagnostics")
    
    if args.dry_run:
        print("[DRY RUN] Would generate area timeseries.")
        exit(0)
        
    in_file = os.path.join(args.output_root, "tables", "drought_diagnostics", f"drought_percentiles_pixel_month_2016_2020_{args.variable}.parquet")
    if not os.path.exists(in_file):
        print(f"Missing {in_file}")
        exit(1)
        
    df = pd.read_parquet(in_file)
    
    # Calculate area % for D1 and D2
    df['time'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')
    total_pixels = df.groupby(['time', 'experiment'])['value'].count().reset_index(name='n_total_pixels')
    
    d1 = df.groupby(['time', 'experiment'])['is_D1'].sum().reset_index(name='n_drought_pixels')
    d1 = d1.merge(total_pixels, on=['time', 'experiment'])
    d1['drought_area_percent'] = (d1['n_drought_pixels'] / d1['n_total_pixels']) * 100
    d1['drought_threshold'] = 'D1'
    
    d2 = df.groupby(['time', 'experiment'])['is_D2'].sum().reset_index(name='n_drought_pixels')
    d2 = d2.merge(total_pixels, on=['time', 'experiment'])
    d2['drought_area_percent'] = (d2['n_drought_pixels'] / d2['n_total_pixels']) * 100
    d2['drought_threshold'] = 'D2'
    
    res = pd.concat([d1, d2])
    res['variable'] = args.variable
    res['year'] = res['time'].dt.year
    res['month'] = res['time'].dt.month
    
    tab_out = os.path.join(out_dir_tab, f"drought_area_monthly_summary_2016_2020_{args.variable}.csv")
    res.drop(columns=['time']).to_csv(tab_out, index=False)
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=res[res['drought_threshold'] == 'D1'], x='time', y='drought_area_percent', hue='experiment')
    plt.title(f"Drought Area Percentage (D1) for {args.variable}\nRelative percentile diagnostic, 2016-2020 reference")
    plt.ylabel('Drought Area (%)')
    plt.xlabel('Time')
    plt.grid(True)
    
    fig_out = os.path.join(out_dir_fig, f"manuscript_drought_area_timeseries_{args.variable}_2016_2020.png")
    plt.savefig(fig_out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved {fig_out} and table.")
