import argparse
import pandas as pd
import os
import numpy as np

def compute_percentiles(df, val_col, group_cols):
    return df.groupby(group_cols)[val_col].rank(pct=True) * 100

def compute_relative_percentiles(df_ref, df_target, ref_col, target_col, group_cols):
    # For mapping target values to reference distribution (OPL)
    # We can use scipy.stats.percentileofscore, but doing it grouped is slow.
    # An easier way: rank combined, or use ecdf.
    # We will do a merge and rank or an apply. 
    # For a large dataset, a fast way is to rank the reference, then interpolate or 
    # just compute the ECDF per pixel. Given 60 months per pixel, it's small.
    # We can use pandas rank on the reference, but we need to evaluate the target.
    # A vectorized approach: compute ECDF by sorting. 
    # Actually, scipy.stats.percentileofscore per group.
    
    def get_pct(group):
        # group contains both ref and target? No, they are passed separately or together.
        pass
    
    # Let's combine ref and target, but only rank the ref and map to target?
    # Simpler: just use pd.qcut or rank on ref, but how to apply to target?
    # Let's use `scipy.stats.ecdf`? No, scipy has percentileofscore.
    # Given we are in a hurry and have a parquet, let's use a custom apply.
    pass

# We will implement the relative percentile inside the main loop.

def get_exclusive_class(p):
    if p <= 2: return 'D4'
    if p <= 5: return 'D3'
    if p <= 10: return 'D2'
    if p <= 20: return 'D1'
    if p <= 30: return 'D0'
    return 'None'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-parquet", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--reference-mode", default="pooled_2016_2020")
    parser.add_argument("--variable", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Running compute_drought_percentiles.py for {args.variable}")
    out_dir = os.path.join(args.output_root, "outputs", "tables", "drought_diagnostics")
    out_file = os.path.join(out_dir, f"drought_percentiles_pixel_month_2016_2020_{args.variable}.parquet")

    if args.dry_run:
        print(f"[DRY RUN] Would write {out_file}")
        exit(0)

    os.makedirs(out_dir, exist_ok=True)
    if os.path.exists(out_file) and not args.overwrite:
        print(f"{out_file} exists. Skipping.")
        exit(0)

    df = pd.read_parquet(args.input_parquet)
    # The dataset contains columns like SSM_OPL, SSM_DA_NoCDF, SSM_DA_CDF
    
    experiments = ["OPL", "DA_NoCDF", "DA_CDF"]
    results = []
    
    group_cols = ["north_south", "east_west"]
    if args.reference_mode == "calendar_month_2016_2020":
        group_cols.append("month")

    from scipy import stats
    
    for exp in experiments:
        col_name = f"{args.variable}_{exp}"
        if col_name not in df.columns:
            continue
            
        temp = df[['year', 'month', 'north_south', 'east_west', col_name]].copy()
        
        if args.reference_mode == "opl_pooled_2016_2020":
            opl_col = f"{args.variable}_OPL"
            
            # We want the percentile of col_name in the distribution of opl_col per group
            # A fast way without groupby apply:
            # Sort OPL values per group to create empirical CDF
            # We will use an apply since it's only 16000 groups of 60 items.
            # Using groupby.apply is okay but might take a minute.
            # Let's combine them into a single dataframe to groupby.
            if opl_col == col_name:
                merged = df[['year', 'month', 'north_south', 'east_west', opl_col]].copy()
                ref_idx = opl_col
                tgt_idx = opl_col
            else:
                merged = df[['year', 'month', 'north_south', 'east_west', opl_col, col_name]].copy()
                ref_idx = opl_col
                tgt_idx = col_name
            
            def ecdf_percentile(g):
                # handle duplicate column names if they occur
                ref = g[ref_idx]
                if isinstance(ref, pd.DataFrame): ref = ref.iloc[:, 0]
                ref = ref.dropna().values
                
                tgt = g[tgt_idx]
                if isinstance(tgt, pd.DataFrame): tgt = tgt.iloc[:, -1]
                tgt = tgt.values
                
                if len(ref) == 0:
                    return pd.Series(np.nan, index=g.index)
                ref_sorted = np.sort(ref)
                idx = np.searchsorted(ref_sorted, tgt, side='right')
                pct = (idx / len(ref_sorted)) * 100
                return pd.Series(pct, index=g.index)

            temp['percentile_rank'] = merged.groupby(group_cols, group_keys=False).apply(ecdf_percentile)
            
        else:
            temp['percentile_rank'] = compute_percentiles(temp, col_name, group_cols)
            
        temp['drought_class_exclusive'] = temp['percentile_rank'].apply(get_exclusive_class)
        temp['is_D0'] = temp['percentile_rank'] <= 30
        temp['is_D1'] = temp['percentile_rank'] <= 20
        temp['is_D2'] = temp['percentile_rank'] <= 10
        temp['is_D3'] = temp['percentile_rank'] <= 5
        temp['is_D4'] = temp['percentile_rank'] <= 2
        temp['experiment'] = exp.replace('_', '-')
        temp['variable'] = args.variable
        temp.rename(columns={col_name: 'value'}, inplace=True)
        results.append(temp)
        
    final_df = pd.concat(results, ignore_index=True)
    
    # Check if land_cover is available to propagate
    if 'land_cover' in df.columns:
        lc = df[['north_south', 'east_west', 'land_cover']].drop_duplicates()
        final_df = final_df.merge(lc, on=['north_south', 'east_west'], how='left')

    final_df.to_parquet(out_file, index=False)
    print(f"Saved {out_file}")
