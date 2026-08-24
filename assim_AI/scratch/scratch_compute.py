# Author: M. EL Aabaribaoune (@um6p)
import pandas as pd
import numpy as np

def compute_stats():
    df = pd.read_parquet('data/processed/monthly_pixel_dataset_2016_2020_static.parquet')
    df['month'] = pd.to_datetime(df['time']).dt.month
    djf = df[df['month'].isin([12, 1, 2])]
    jja = df[df['month'].isin([6, 7, 8])]

    print("=== D2 DA-CDF Runoff Stats ===")
    for var in ['Qs_tavg', 'Qsb_tavg']:
        opl = f'{var}_OPL'
        cdf = f'{var}_DA_CDF'
        if opl in df.columns and cdf in df.columns:
            diff_djf = djf[cdf] - djf[opl]
            diff_jja = jja[cdf] - jja[opl]
            print(f"{var} DJF diff: min={diff_djf.min():.6e}, mean={diff_djf.mean():.6e}, max={diff_djf.max():.6e}")
            print(f"{var} JJA diff: min={diff_jja.min():.6e}, mean={diff_jja.mean():.6e}, max={diff_jja.max():.6e}")
            total_djf = diff_djf.mean()
            total_jja = diff_jja.mean()

    # Total runoff
    opl_q = djf['Qs_tavg_OPL'] + djf['Qsb_tavg_OPL']
    cdf_q = djf['Qs_tavg_DA_CDF'] + djf['Qsb_tavg_DA_CDF']
    diff_q = cdf_q - opl_q
    print(f"Total runoff DJF diff: min={diff_q.min():.6e}, mean={diff_q.mean():.6e}, max={diff_q.max():.6e}")
    opl_q_jja = jja['Qs_tavg_OPL'] + jja['Qsb_tavg_OPL']
    cdf_q_jja = jja['Qs_tavg_DA_CDF'] + jja['Qsb_tavg_DA_CDF']
    diff_q_jja = cdf_q_jja - opl_q_jja
    print(f"Total runoff JJA diff: min={diff_q_jja.min():.6e}, mean={diff_q_jja.mean():.6e}, max={diff_q_jja.max():.6e}")


    print("=== E1 Seasonal SSM Response ===")
    ssm_opl = 'SSM_OPL'
    ssm_nocdf = 'SSM_DA_NoCDF'
    if ssm_opl in df.columns and ssm_nocdf in df.columns:
        print(f"OL DJF mean: {djf[ssm_opl].mean():.6f}")
        print(f"DA-NoCDF DJF mean: {djf[ssm_nocdf].mean():.6f}")
        diff_djf = djf[ssm_nocdf] - djf[ssm_opl]
        print(f"Diff DJF mean: {diff_djf.mean():.6f}")
        print(f"% pos DJF: {(diff_djf > 0).mean()*100:.2f}%, % neg: {(diff_djf < 0).mean()*100:.2f}%")
        
        print(f"OL JJA mean: {jja[ssm_opl].mean():.6f}")
        print(f"DA-NoCDF JJA mean: {jja[ssm_nocdf].mean():.6f}")
        diff_jja = jja[ssm_nocdf] - jja[ssm_opl]
        print(f"Diff JJA mean: {diff_jja.mean():.6f}")
        print(f"% pos JJA: {(diff_jja > 0).mean()*100:.2f}%, % neg: {(diff_jja < 0).mean()*100:.2f}%")

    print("=== E2 Runoff partitioning DA-NoCDF ===")
    precip = 'Rainf_tavg_OPL'
    if precip in df.columns:
        print(f"Precip DJF mean: {djf[precip].mean():.6e}, JJA mean: {jja[precip].mean():.6e}")
    
    for var in ['Qs_tavg', 'Qsb_tavg']:
        opl = f'{var}_OPL'
        nocdf = f'{var}_DA_NoCDF'
        if opl in df.columns and nocdf in df.columns:
            diff_djf = djf[nocdf] - djf[opl]
            diff_jja = jja[nocdf] - jja[opl]
            print(f"DA-NoCDF - OL {var} DJF mean: {diff_djf.mean():.6e}, JJA mean: {diff_jja.mean():.6e}")
            
    # Total runoff DA-NoCDF
    opl_q = djf['Qs_tavg_OPL'] + djf['Qsb_tavg_OPL']
    nocdf_q = djf['Qs_tavg_DA_NoCDF'] + djf['Qsb_tavg_DA_NoCDF']
    diff_q = nocdf_q - opl_q
    print(f"Total runoff DA-NoCDF - OL DJF mean: {diff_q.mean():.6e}")
    
    opl_q_jja = jja['Qs_tavg_OPL'] + jja['Qsb_tavg_OPL']
    nocdf_q_jja = jja['Qs_tavg_DA_NoCDF'] + jja['Qsb_tavg_DA_NoCDF']
    diff_q_jja = nocdf_q_jja - opl_q_jja
    print(f"Total runoff DA-NoCDF - OL JJA mean: {diff_q_jja.mean():.6e}")

    # E4 RF metrics
    df_rf = pd.read_csv('outputs/tables/rf_metrics_v02_spatial_cv.csv')
    print("=== E4 RF Metrics ===")
    print(df_rf.head())
    
if __name__ == "__main__":
    compute_stats()
