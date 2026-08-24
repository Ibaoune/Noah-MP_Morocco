# Author: M. EL Aabaribaoune (@um6p)
import pandas as pd
import os

df = pd.read_csv('outputs/tables/q1_hydrological_response_summary.csv')
if 'n_pixels' in df.columns:
    df.rename(columns={'n_pixels': 'n_grid_cells'}, inplace=True)
df['aggregation_method'] = 'spatial mean map'

def get_n_months(period):
    if period == 'annual': return 60
    elif period in ['DJF', 'JJA']: return 15
    return 60
df['n_months'] = df['period'].apply(get_n_months)

df.to_csv('outputs/tables/q1_hydrological_response_summary.csv', index=False)

with open('reports/q1_hydrological_response_summary.md', 'w') as f:
    f.write("| " + " | ".join(df.columns) + " |\n")
    f.write("| " + " | ".join(["---"] * len(df.columns)) + " |\n")
    for _, row in df.iterrows():
        f.write("| " + " | ".join([str(x) for x in row.values]) + " |\n")

# Create key numbers table
key_rows = []
targets = ['SSM', 'RZSM', 'ET', 'total_runoff', 'surface_runoff', 'baseflow']
for t in targets:
    for p in ['annual', 'DJF', 'JJA']:
        # Extract means
        m_nocdf = df[(df['variable']==t) & (df['period']==p) & (df['experiment_difference']=='DA-NoCDF_minus_OPL')]['mean'].values
        m_cdf = df[(df['variable']==t) & (df['period']==p) & (df['experiment_difference']=='DA-CDF_minus_OPL')]['mean'].values
        m_nocdf_cdf = df[(df['variable']==t) & (df['period']==p) & (df['experiment_difference']=='DA-NoCDF_minus_DA-CDF')]['mean'].values
        unit = df[(df['variable']==t)]['unit'].values[0]
        
        m_nocdf = m_nocdf[0] if len(m_nocdf)>0 else np.nan
        m_cdf = m_cdf[0] if len(m_cdf)>0 else np.nan
        m_nocdf_cdf = m_nocdf_cdf[0] if len(m_nocdf_cdf)>0 else np.nan
        
        interp = ""
        if 'runoff' in t or 'baseflow' in t:
            interp = "CDF matching strongly attenuates the response." if abs(m_cdf) < abs(m_nocdf)/2 else "Response preserved."
        elif t == 'ET':
            interp = "ET remains non-negligibly affected."
        else:
            interp = "State variable directly affected by assimilation."
            
        key_rows.append({
            'target': t,
            'period': p,
            'DA_NoCDF_minus_OPL_mean': m_nocdf,
            'DA_CDF_minus_OPL_mean': m_cdf,
            'NoCDF_minus_CDF_mean': m_nocdf_cdf,
            'unit': unit,
            'main_interpretation': interp
        })

key_df = pd.DataFrame(key_rows)
key_df.to_csv('outputs/tables/q1_hydrological_response_key_numbers.csv', index=False)

print("Done tables update")
