import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-parquet", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--reference-mode", default="pooled_2016_2020")
    parser.add_argument("--variable", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Running drought_transition_analysis.py for {args.variable}")
    out_dir_fig = os.path.join(args.output_root, "figures", "drought_diagnostics")
    out_dir_tab = os.path.join(args.output_root, "tables", "drought_diagnostics")
    
    if args.dry_run:
        print("[DRY RUN] Would generate transition matrix.")
        exit(0)
        
    in_file = os.path.join(args.output_root, "tables", "drought_diagnostics", f"drought_percentiles_pixel_month_2016_2020_{args.variable}.parquet")
    if not os.path.exists(in_file):
        print(f"Missing {in_file}")
        exit(1)
        
    df = pd.read_parquet(in_file)
    
    # Pivot to compare experiments
    pivot = df.pivot_table(index=['year', 'month', 'north_south', 'east_west'], columns='experiment', values='drought_class_exclusive', aggfunc='first').reset_index()
    
    def get_transition(opl, da):
        if opl == da: return 'unchanged'
        if opl == 'None' and da != 'None': return 'introduced_drought'
        if opl != 'None' and da == 'None': return 'removed_drought'
        # Simple heuristic since D4 > D3 > D2 > D1 > D0
        levels = {'None': 0, 'D0': 1, 'D1': 2, 'D2': 3, 'D3': 4, 'D4': 5}
        if levels.get(da, 0) > levels.get(opl, 0): return 'intensified'
        return 'alleviated'

    if 'OPL' in pivot.columns and 'DA-NoCDF' in pivot.columns:
        pivot['transition_OPL_NoCDF'] = pivot.apply(lambda x: get_transition(x['OPL'], x['DA-NoCDF']), axis=1)
        
        sum_nocdf = pivot.groupby(['year', 'month', 'transition_OPL_NoCDF']).size().reset_index(name='n_pixels')
        sum_nocdf['comparison'] = 'OPL_to_DA-NoCDF'
        sum_nocdf.rename(columns={'transition_OPL_NoCDF': 'transition_type'}, inplace=True)
    else:
        sum_nocdf = pd.DataFrame()

    if 'OPL' in pivot.columns and 'DA-CDF' in pivot.columns:
        pivot['transition_OPL_CDF'] = pivot.apply(lambda x: get_transition(x['OPL'], x['DA-CDF']), axis=1)
        
        sum_cdf = pivot.groupby(['year', 'month', 'transition_OPL_CDF']).size().reset_index(name='n_pixels')
        sum_cdf['comparison'] = 'OPL_to_DA-CDF'
        sum_cdf.rename(columns={'transition_OPL_CDF': 'transition_type'}, inplace=True)
    else:
        sum_cdf = pd.DataFrame()

    res = pd.concat([sum_nocdf, sum_cdf])
    if not res.empty:
        total = res.groupby(['year', 'month', 'comparison'])['n_pixels'].transform('sum')
        res['percent_pixels'] = (res['n_pixels'] / total) * 100
        res['variable'] = args.variable
        
        tab_out = os.path.join(out_dir_tab, f"drought_transition_summary_2016_2020_{args.variable}.csv")
        res.to_csv(tab_out, index=False)
        
        # Simple bar plot
        plt.figure(figsize=(10, 6))
        mean_trans = res.groupby(['comparison', 'transition_type'])['percent_pixels'].mean().unstack().fillna(0)
        mean_trans.plot(kind='bar', stacked=True, ax=plt.gca())
        plt.title(f"Average Monthly Drought Transitions ({args.variable})")
        plt.ylabel('Percent of Pixels (%)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        fig_out = os.path.join(out_dir_fig, f"manuscript_drought_transition_{args.variable}_2016_2020.png")
        plt.savefig(fig_out, dpi=300, facecolor='white')
        plt.close()
        print(f"Saved {fig_out} and table.")
