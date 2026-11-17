#!/usr/bin/env python3
"""
Post-processing & Evaluation of Noah-MP Hydrology Sensitivity Experiments.
Reads long-format ABH observed streamflow from data/streamflow_clean/obs_daily.csv,
aligns with HyMAP-2 simulated routed discharges, and computes standard hydrological metrics:
- Kling-Gupta Efficiency (KGE-2009)
- Nash-Sutcliffe Efficiency (NSE)
- Percent Bias (PBIAS)
- Low-flow metrics (June-September dry season: mean summer flow, zero/low flow days)
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
base_proj = os.path.abspath(os.path.join(script_dir, "../.."))
repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"

routing_dir = f"{base_proj}/routing"
postproc_dir = f"{base_proj}/postproc"
obs_daily_file = f"{repo_root}/data/streamflow_clean/obs_daily.csv"
pairing_file = f"{repo_root}/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv"

# Metric functions
def calc_kge(sim, obs):
    """KGE-2009 (Gupta et al., 2009) based on alpha = std_sim / std_obs"""
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    std_s, std_o = np.std(s), np.std(o)
    mean_s, mean_o = np.mean(s), np.mean(o)
    if std_o == 0 or mean_o == 0:
        return np.nan
    r = np.corrcoef(s, o)[0, 1]
    alpha = std_s / std_o
    beta = mean_s / mean_o
    return 1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)

def calc_nse(sim, obs):
    """Nash-Sutcliffe Efficiency (Nash & Sutcliffe, 1970)"""
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    denom = np.sum((o - np.mean(o))**2)
    if denom == 0:
        return np.nan
    return 1.0 - (np.sum((s - o)**2) / denom)

def calc_pbias(sim, obs):
    """Percent Bias (%)"""
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    sum_o = np.sum(o)
    if sum_o == 0:
        return np.nan
    return 100.0 * np.sum(s - o) / sum_o

def load_clean_observations(obs_csv_path, start_date="2018-01-01", end_date="2018-12-31"):
    """
    Reads observations in long format: station_id, date, q_m3s, flag
    Filters by date window and pivots into wide format: date x station_id
    """
    if not os.path.exists(obs_csv_path):
        raise FileNotFoundError(f"Observations file {obs_csv_path} not found.")

    df_obs = pd.read_csv(obs_csv_path)
    # Ensure correct types
    df_obs["date"] = pd.to_datetime(df_obs["date"])
    df_obs["q_m3s"] = pd.to_numeric(df_obs["q_m3s"], errors="coerce")

    # Filter evaluation period
    mask = (df_obs["date"] >= pd.to_datetime(start_date)) & (df_obs["date"] <= pd.to_datetime(end_date))
    df_filtered = df_obs.loc[mask].copy()

    # Drop invalid/negative flows if any
    df_filtered.loc[df_filtered["q_m3s"] < 0, "q_m3s"] = np.nan

    # Pivot to wide format: index=date (as string YYYY-MM-DD), columns=station_id
    df_filtered["date_str"] = df_filtered["date"].dt.strftime("%Y-%m-%d")
    df_pivot = df_filtered.pivot(index="date_str", columns="station_id", values="q_m3s")
    return df_pivot

def evaluate(start_date="2018-01-01", end_date="2018-12-31", output_suffix=None):
    print("=" * 85)
    print(f" OPL HYDROLOGY SENSITIVITY — EVALUATION {start_date} -> {end_date}")
    print("=" * 85)

    df_obs_wide = load_clean_observations(obs_daily_file, start_date=start_date, end_date=end_date)
    print(f"Loaded observations for {len(df_obs_wide.columns)} stations ({len(df_obs_wide)} date records).")

    df_pairing = pd.read_csv(pairing_file)
    station_names = dict(zip(df_pairing["station_id"], df_pairing["nom"]))

    experiments = [
        ("OL_R1_SIMGM", "SIMGM (Option 1)"),
        ("OL_R2_SIMTOP", "SIMTOP (Option 2)"),
        ("OL_R3_SCHAAKE96", "Schaake96 (Option 3)"),
        ("OL_R4_BATS", "BATS (Option 4)")
    ]

    stations_eval = ["b_l_chafia", "b_s_jabeur", "b_a_loudah", "b_s_cherif"]

    metric_rows = []

    for exp_id, exp_label in experiments:
        csv_sim = f"{routing_dir}/outputs/{exp_id}/streamflow_daily_stations.csv"
        if not os.path.exists(csv_sim):
            print(f"[{exp_id}] Simulated streamflow CSV not found: {csv_sim} (Run extraction first)")
            continue

        df_sim = pd.read_csv(csv_sim)
        if "date" not in df_sim.columns:
            print(f"[{exp_id}] 'date' column missing in {csv_sim}!")
            continue

        df_sim["date_str"] = pd.to_datetime(df_sim["date"]).dt.strftime("%Y-%m-%d")
        df_sim_idx = df_sim.set_index("date_str")

        for sid in stations_eval:
            if sid not in df_obs_wide.columns:
                continue
            if sid not in df_sim_idx.columns:
                continue

            # Align strictly on common dates
            common_dates = df_sim_idx.index.intersection(df_obs_wide.index)
            if len(common_dates) == 0:
                continue

            s_sim_series = df_sim_idx.loc[common_dates, sid].astype(float)
            s_obs_series = df_obs_wide.loc[common_dates, sid].astype(float)

            # Drop missing values (NaN)
            valid_mask = (~s_sim_series.isna()) & (~s_obs_series.isna()) & (s_obs_series >= 0)
            n_valid = int(valid_mask.sum())
            if n_valid < 5:
                continue

            s_sim = s_sim_series[valid_mask].values
            s_obs = s_obs_series[valid_mask].values

            kge = calc_kge(s_sim, s_obs)
            nse = calc_nse(s_sim, s_obs)
            pbias = calc_pbias(s_sim, s_obs)
            r = np.corrcoef(s_sim, s_obs)[0, 1] if len(s_sim) > 1 else np.nan

            # Summer low flow analysis (June 1 - Sept 30)
            summer_dates = [d for d in common_dates if "-06-" in d or "-07-" in d or "-08-" in d or "-09-" in d]
            if len(summer_dates) > 0:
                sub_sim = df_sim_idx.loc[summer_dates, sid].astype(float)
                sub_obs = df_obs_wide.loc[summer_dates, sid].astype(float)
                s_mask = (~sub_sim.isna()) & (~sub_obs.isna()) & (sub_obs >= 0)

                q_summer_obs = float(np.nanmean(sub_obs[s_mask])) if s_mask.sum() > 0 else np.nan
                q_summer_sim = float(np.nanmean(sub_sim[s_mask])) if s_mask.sum() > 0 else np.nan

                zero_days_obs = int((sub_obs[s_mask] <= 0.01).sum())
                zero_days_sim = int((sub_sim[s_mask] <= 0.01).sum())
                low_days_obs = int((sub_obs[s_mask] <= 0.1).sum())
                low_days_sim = int((sub_sim[s_mask] <= 0.1).sum())
                n_summer_valid = int(s_mask.sum())
            else:
                q_summer_obs, q_summer_sim = np.nan, np.nan
                zero_days_obs, zero_days_sim = 0, 0
                low_days_obs, low_days_sim = 0, 0
                n_summer_valid = 0

            st_name = station_names.get(sid, sid)

            metric_rows.append({
                "Station_ID": sid,
                "Station_Name": st_name,
                "Experiment": exp_id,
                "Formulation": exp_label,
                "N_Valid_Days": n_valid,
                "KGE": round(kge, 3) if not np.isnan(kge) else np.nan,
                "NSE": round(nse, 3) if not np.isnan(nse) else np.nan,
                "PBIAS_%": round(pbias, 1) if not np.isnan(pbias) else np.nan,
                "Pearson_r": round(r, 3) if not np.isnan(r) else np.nan,
                "Q_obs_mean": round(float(np.mean(s_obs)), 2),
                "Q_sim_mean": round(float(np.mean(s_sim)), 2),
                "Q_summer_obs": round(q_summer_obs, 2) if not np.isnan(q_summer_obs) else np.nan,
                "Q_summer_sim": round(q_summer_sim, 2) if not np.isnan(q_summer_sim) else np.nan,
                "ZeroDays_summer_obs": zero_days_obs,
                "ZeroDays_summer_sim": zero_days_sim,
                "LowDays_summer_obs": low_days_obs,
                "LowDays_summer_sim": low_days_sim,
                "N_Summer_Valid": n_summer_valid
            })

    if metric_rows:
        df_res = pd.DataFrame(metric_rows)
        suffix = f"_{output_suffix}" if output_suffix else f"_{start_date[:4]}"
        csv_out = f"{postproc_dir}/tables/table_hydrology_metrics{suffix}.csv"
        os.makedirs(f"{postproc_dir}/tables", exist_ok=True)
        df_res.to_csv(csv_out, index=False)
        print(f"\n[OK] Metrics computed and exported to: {csv_out}")
        print(df_res[["Station_ID", "Experiment", "N_Valid_Days", "KGE", "NSE", "PBIAS_%", "Q_obs_mean", "Q_sim_mean"]].to_string())
    else:
        print("\n[INFO] No streamflow extraction files available yet. Metrics will compute automatically once routing outputs are generated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Noah-MP hydrological sensitivity against ABH daily streamflow.")
    parser.add_argument("--start-date", default="2018-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2018-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--suffix", default=None, help="Suffix for output CSV table")
    args = parser.parse_args()

    evaluate(start_date=args.start_date, end_date=args.end_date, output_suffix=args.suffix)
