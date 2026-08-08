import pandas as pd
import os

out_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/matrix_2016_2020/outputs/tables/drought_diagnostics"

# Key Numbers
rows_key = []
for var in ['SSM', 'RZSM']:
    area = pd.read_csv(os.path.join(out_dir, f"drought_area_monthly_summary_2016_2020_{var}.csv"))
    
    # We want OPL, DA-NoCDF, DA-CDF for D1/D2
    for thresh in ['D1', 'D2']:
        sub = area[area['drought_threshold'] == thresh]
        opl = sub[sub['experiment'] == 'OPL']
        mean_opl = opl['drought_area_percent'].mean()
        
        for exp in ['OPL', 'DA-NoCDF', 'DA-CDF']:
            exp_data = sub[sub['experiment'] == exp]
            if len(exp_data) == 0: continue
            
            mean_area = exp_data['drought_area_percent'].mean()
            max_idx = exp_data['drought_area_percent'].idxmax()
            max_area = exp_data.loc[max_idx, 'drought_area_percent']
            max_month = f"{exp_data.loc[max_idx, 'year']}-{exp_data.loc[max_idx, 'month']:02d}"
            
            diff = mean_area - mean_opl
            
            interp = f"Matches reference" if exp == 'OPL' else f"Shifted by {diff:+.1f}%"
            
            rows_key.append({
                "variable": var,
                "drought_threshold": thresh,
                "experiment": exp,
                "mean_drought_area_percent": round(mean_area, 2),
                "max_drought_area_percent": round(max_area, 2),
                "month_of_max": max_month,
                "mean_difference_vs_OPL": round(diff, 2),
                "interpretation": interp
            })

df_key = pd.DataFrame(rows_key)
df_key.to_csv(os.path.join(out_dir, "manuscript_drought_key_numbers_2016_2020.csv"), index=False)

# Transitions
rows_trans = []
for var in ['SSM', 'RZSM']:
    trans = pd.read_csv(os.path.join(out_dir, f"drought_transition_summary_2016_2020_{var}.csv"))
    mean_trans = trans.groupby(['comparison', 'transition_type'])['percent_pixels'].mean().unstack().fillna(0)
    
    for comp in mean_trans.index:
        r = mean_trans.loc[comp]
        unchanged = r.get('unchanged', 0)
        intensified = r.get('intensified', 0)
        alleviated = r.get('alleviated', 0)
        intro = r.get('introduced_drought', 0)
        removed = r.get('removed_drought', 0)
        
        if intro + intensified > removed + alleviated:
            interp = "Net intensification of drought classification"
        else:
            interp = "Net alleviation of drought classification"
            
        rows_trans.append({
            "variable": var,
            "comparison": comp,
            "drought_threshold": "Categorical Shift",
            "unchanged_percent": round(unchanged, 2),
            "intensified_percent": round(intensified, 2),
            "alleviated_percent": round(alleviated, 2),
            "introduced_drought_percent": round(intro, 2),
            "removed_drought_percent": round(removed, 2),
            "interpretation": interp
        })

df_trans = pd.DataFrame(rows_trans)
df_trans.to_csv(os.path.join(out_dir, "manuscript_drought_transition_key_numbers_2016_2020.csv"), index=False)
