#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step4_streamflow_metrics_corrected_2018.py
Évaluation des débits HyMAP-2 linres0 aux stations hydrométriques pour la Partie A4.
Inclut :
  - OPL, OL_DAIC, ENS_OPL, ENS_corr, DA_nocdf, DA_cdf, DA_nocdf_nowilt, DA_corr
  - 10 stations retenues (4 journalières, 10 mensuelles)
  - Métriques complètes : KGE (2012, 2009) et composantes (r, gamma, beta, alpha),
    NSE, logNSE (eps = 0.01 * mean_obs), débit JJA, jours à débit nul, pic et décalage.
  - Saisons : Annual, Wet_Nov_Apr, Dry_May_Oct, Excl_Jan
  - NIC avec :
      * DA_corr vs ENS_corr
      * ENS_corr vs OL_DAIC
      * DA_nocdf vs ENS_OPL
      * ENS_OPL vs OL_DAIC
      * DA_nocdf_nowilt vs DA_nocdf
      * DA_nocdf vs OPL
  - Bootstrap par blocs mobiles (30 jours, 1000 tirages, reproductible seed=42)

Sorties :
  - paper1/tables/streamflow_metrics_corrected_2018.csv
  - paper1/tables/streamflow_nic_corrected_2018.csv
"""

import os
import sys
import glob
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
ROUTING_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/routing")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
CACHE_DIR = os.path.join(ROUTING_DIR, "cache_streamflow_2018")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

RETAINED_STATIONS = {
    "b_l_chafia": {
        "name": "Lalla Chafia", "basin": "Bouregreg", "oued": "Bouregreg",
        "row": 75, "col": 71, "area_km2": 3341.6, "timestep": "journalier",
        "statut": "Retenue — Évaluation principale", "note": "Amont naturel non régulé"
    },
    "b_s_jabeur": {
        "name": "Sidi Jabeur", "basin": "Bouregreg", "oued": "Grou",
        "row": 71, "col": 71, "area_km2": 3138.5, "timestep": "journalier",
        "statut": "Retenue — Évaluation principale", "note": "Amont naturel non régulé"
    },
    "ain_timedrine": {
        "name": "Ain Timedrine", "basin": "Sebou", "oued": "Sebou",
        "row": 74, "col": 108, "area_km2": 4387.0, "timestep": "mensuel",
        "statut": "Retenue — Évaluation principale", "note": "Station mensuelle Sebou Niveau A"
    },
    "ait_khabbach": {
        "name": "Ait Khabbach", "basin": "Sebou", "oued": "Guigou",
        "row": 68, "col": 103, "area_km2": 1240.0, "timestep": "mensuel",
        "statut": "Retenue — Évaluation principale", "note": "Station mensuelle Sebou Niveau A"
    },
    "azzaba": {
        "name": "Azzaba", "basin": "Sebou", "oued": "Sebou",
        "row": 75, "col": 108, "area_km2": 4640.0, "timestep": "mensuel",
        "statut": "Retenue — Évaluation principale", "note": "Station mensuelle Sebou Niveau A"
    },
    "dar_el_hamra": {
        "name": "Dar El Hamra", "basin": "Sebou", "oued": "Zloul",
        "row": 75, "col": 112, "area_km2": 670.0, "timestep": "mensuel",
        "statut": "Retenue — Évaluation principale", "note": "Station mensuelle Sebou Niveau A"
    },
    "pont_de_mdez": {
        "name": "Pont de Mdez", "basin": "Sebou", "oued": "Sebou",
        "row": 72, "col": 109, "area_km2": 3435.0, "timestep": "mensuel",
        "statut": "Retenue — Évaluation principale", "note": "Station mensuelle Sebou Niveau A"
    },
    "b_a_loudah": {
        "name": "Ain Loudah", "basin": "Bouregreg", "oued": "Korifla",
        "row": 70, "col": 64, "area_km2": 697.6, "timestep": "journalier",
        "statut": "Retenue — Avec réserves", "note": "Série mesurée dupliquée avec SM Cherif"
    },
    "b_s_cherif": {
        "name": "S.M. Cherif", "basin": "Bouregreg", "oued": "Mechraa",
        "row": 70, "col": 67, "area_km2": 649.5, "timestep": "journalier",
        "statut": "Retenue — Avec réserves", "note": "Série mesurée dupliquée avec Ain Loudah"
    },
    "pont_ait_aissa": {
        "name": "Pont Ait Aissa", "basin": "Sebou", "oued": "Guigou",
        "row": 62, "col": 98, "area_km2": 205.0, "timestep": "mensuel",
        "statut": "Retenue — Avec réserves", "note": "Très petit bassin versant (205 km²)"
    }
}

EXPERIMENTS = {
    "OPL": {
        "name": "Open-Loop linres0",
        "dir": os.path.join(ROUTING_DIR, "output/OPL_linres0_2016_2020/ROUTING"),
    },
    "OL_DAIC": {
        "name": "OL DAIC 2018 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/OL_DAIC_2018_linres0/ROUTING"),
    },
    "ENS_OPL": {
        "name": "ENS OPL 2018 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/ENS_OPL_2018_linres0/ROUTING"),
    },
    "ENS_corr": {
        "name": "ENS corr 2018 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/ENS_corr_2018_linres0/ROUTING"),
    },
    "DA_nocdf": {
        "name": "DA-NoCDF linres0",
        "dir": os.path.join(ROUTING_DIR, "output/DA_nocdf_linres0_2016_2020/ROUTING"),
    },
    "DA_cdf": {
        "name": "DA-CDF linres0",
        "dir": os.path.join(ROUTING_DIR, "output/DA_cdf_linres0_2016_2020/ROUTING"),
    },
    "DA_nocdf_nowilt": {
        "name": "DA-NoCDF NoWilt 2018 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/DA_nocdf_nowilt_2018_linres0/ROUTING"),
    },
    "DA_corr": {
        "name": "DA corr 2018 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/DA_corr_2018_linres0/ROUTING"),
    }
}

def extract_simulated_streamflow_2018(exp_id, exp_cfg):
    cache_file = os.path.join(CACHE_DIR, f"streamflow_2018_{exp_id}.csv")
    if os.path.exists(cache_file):
        df_cached = pd.read_csv(cache_file)
        if len(df_cached) == 365 and "date" in df_cached.columns:
            print(f"  [{exp_id}] En cache ({len(df_cached)} jours).")
            return df_cached

    print(f"  [{exp_id}] Extraction depuis NetCDF dans {exp_cfg['dir']}...")
    files_2018 = sorted(glob.glob(os.path.join(exp_cfg['dir'], "2018*/**/LIS_HIST_*.d01.nc"), recursive=True))
    file_20190101 = os.path.join(exp_cfg['dir'], "201901/LIS_HIST_201901010000.d01.nc")
    if os.path.exists(file_20190101) and file_20190101 not in files_2018:
        files_2018.append(file_20190101)

    records = []
    seen_dates = set()
    for fpath in sorted(files_2018):
        fname = os.path.basename(fpath)
        if not fname.startswith("LIS_HIST_"):
            continue
        try:
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                dt_str = sim_dt.strftime("%Y-%m-%d")

                if not dt_str.startswith("2018-"):
                    continue
                if dt_str in seen_dates:
                    continue
                seen_dates.add(dt_str)

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3:
                    flow = flow[0]

                rec = {"date": dt_str}
                for sid, info in RETAINED_STATIONS.items():
                    r, c = info["row"], info["col"]
                    rec[sid] = float(flow[r, c])
                records.append(rec)
        except Exception as e:
            print(f"    Erreur lecture {fname}: {e}")

    df_out = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    df_out.to_csv(cache_file, index=False)
    print(f"  [{exp_id}] Extraction terminée : {len(df_out)} jours sauvés dans {cache_file}.")
    return df_out

def compute_hydrological_metrics(obs_arr, sim_arr, dates_arr=None):
    valid = ~np.isnan(obs_arr) & ~np.isnan(sim_arr)
    obs_arr = obs_arr[valid]
    sim_arr = sim_arr[valid]
    if dates_arr is not None:
        dates_arr = np.array(dates_arr)[valid]

    n = len(obs_arr)
    if n < 5:
        return {
            "n_obs": n, "mean_obs_m3s": np.nan, "mean_sim_m3s": np.nan,
            "bias_m3s": np.nan, "rel_bias_pct": np.nan, "rmse_m3s": np.nan,
            "r": np.nan, "gamma": np.nan, "beta": np.nan, "alpha": np.nan,
            "kge_2012": np.nan, "kge_2009": np.nan,
            "nse": np.nan, "nse_log": np.nan, "eps_m3s": np.nan,
            "zero_days_obs": 0, "zero_days_sim": 0,
            "summer_bias_jja_m3s": np.nan, "summer_rel_bias_jja_pct": np.nan,
            "peak_obs_m3s": np.nan, "peak_obs_date": "",
            "peak_sim_m3s": np.nan, "peak_sim_date": "",
            "peak_bias_m3s": np.nan, "peak_timing_days": np.nan
        }

    mu_o = float(np.mean(obs_arr))
    mu_s = float(np.mean(sim_arr))
    std_o = float(np.std(obs_arr, ddof=0))
    std_s = float(np.std(sim_arr, ddof=0))

    bias = mu_s - mu_o
    rel_bias = (bias / (mu_o + 1e-12)) * 100.0
    rmse = float(np.sqrt(np.mean((sim_arr - obs_arr) ** 2)))

    if std_o > 1e-12 and std_s > 1e-12:
        r = float(np.corrcoef(obs_arr, sim_arr)[0, 1])
        alpha = float(std_s / std_o)
    else:
        r = np.nan
        alpha = np.nan

    beta = float(mu_s / (mu_o + 1e-12)) if mu_o > 1e-12 else np.nan

    if not np.isnan(alpha) and not np.isnan(beta) and beta > 1e-12:
        gamma = float(alpha / beta)
    else:
        gamma = np.nan

    if not np.isnan(r) and not np.isnan(gamma) and not np.isnan(beta):
        ed_2012 = np.sqrt((r - 1.0) ** 2 + (gamma - 1.0) ** 2 + (beta - 1.0) ** 2)
        kge_2012 = float(1.0 - ed_2012)
    else:
        kge_2012 = np.nan

    if not np.isnan(r) and not np.isnan(alpha) and not np.isnan(beta):
        ed_2009 = np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)
        kge_2009 = float(1.0 - ed_2009)
    else:
        kge_2009 = np.nan

    ss_tot = np.sum((obs_arr - mu_o) ** 2)
    if ss_tot > 1e-12:
        nse = float(1.0 - (np.sum((sim_arr - obs_arr) ** 2) / ss_tot))
    else:
        nse = np.nan

    eps = max(0.01 * mu_o, 1e-4)
    log_o = np.log(np.maximum(obs_arr, 0.0) + eps)
    log_s = np.log(np.maximum(sim_arr, 0.0) + eps)
    ss_tot_log = np.sum((log_o - np.mean(log_o)) ** 2)
    if ss_tot_log > 1e-12:
        nse_log = float(1.0 - (np.sum((log_s - log_o) ** 2) / ss_tot_log))
    else:
        nse_log = np.nan

    zero_obs = int(np.sum(obs_arr < 0.001))
    zero_sim = int(np.sum(sim_arr < 0.001))

    summer_bias_jja = np.nan
    summer_rel_bias_jja = np.nan
    if dates_arr is not None:
        dt_series = pd.to_datetime(dates_arr)
        jja_mask = dt_series.month.isin([6, 7, 8])
        if np.sum(jja_mask) > 0:
            mu_o_jja = float(np.mean(obs_arr[jja_mask]))
            mu_s_jja = float(np.mean(sim_arr[jja_mask]))
            summer_bias_jja = mu_s_jja - mu_o_jja
            summer_rel_bias_jja = (summer_bias_jja / (mu_o_jja + 1e-12)) * 100.0

    peak_obs = float(np.max(obs_arr))
    peak_sim = float(np.max(sim_arr))
    peak_bias = peak_sim - peak_obs
    peak_obs_date = ""
    peak_sim_date = ""
    peak_timing = np.nan
    if dates_arr is not None:
        idx_o = int(np.argmax(obs_arr))
        idx_s = int(np.argmax(sim_arr))
        peak_obs_date = str(dates_arr[idx_o])
        peak_sim_date = str(dates_arr[idx_s])
        dt_o = pd.to_datetime(peak_obs_date)
        dt_s = pd.to_datetime(peak_sim_date)
        peak_timing = int((dt_s - dt_o).days)

    return {
        "n_obs": n, "mean_obs_m3s": mu_o, "mean_sim_m3s": mu_s,
        "bias_m3s": bias, "rel_bias_pct": rel_bias, "rmse_m3s": rmse,
        "r": r, "gamma": gamma, "beta": beta, "alpha": alpha,
        "kge_2012": kge_2012, "kge_2009": kge_2009,
        "nse": nse, "nse_log": nse_log, "eps_m3s": eps,
        "zero_days_obs": zero_obs, "zero_days_sim": zero_sim,
        "summer_bias_jja_m3s": summer_bias_jja,
        "summer_rel_bias_jja_pct": summer_rel_bias_jja,
        "peak_obs_m3s": peak_obs, "peak_obs_date": peak_obs_date,
        "peak_sim_m3s": peak_sim, "peak_sim_date": peak_sim_date,
        "peak_bias_m3s": peak_bias, "peak_timing_days": peak_timing
    }

def moving_block_bootstrap_nic(obs_arr, sim_target_arr, sim_ref_arr, block_len=30, n_boot=1000):
    n = len(obs_arr)
    if n < block_len * 2:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    num_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len + 1

    rng = np.random.RandomState(42)
    delta_kge_dist = []
    nic_dist = []

    for _ in range(n_boot):
        starts = rng.randint(0, max_start, size=num_blocks)
        indices = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n]

        o_b = obs_arr[indices]
        st_b = sim_target_arr[indices]
        sr_b = sim_ref_arr[indices]

        m_t = compute_hydrological_metrics(o_b, st_b)
        m_r = compute_hydrological_metrics(o_b, sr_b)

        kt = m_t["kge_2012"]
        kr = m_r["kge_2012"]

        if not np.isnan(kt) and not np.isnan(kr):
            dk = kt - kr
            delta_kge_dist.append(dk)
            denom = 1.0 - kr
            nic_val = dk / denom if abs(denom) > 1e-6 else np.nan
            if not np.isnan(nic_val):
                nic_dist.append(nic_val)

    if len(nic_dist) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    nic_mean = float(np.mean(nic_dist))
    nic_ci_low = float(np.percentile(nic_dist, 2.5))
    nic_ci_high = float(np.percentile(nic_dist, 97.5))
    d_kge_ci_low = float(np.percentile(delta_kge_dist, 2.5))
    d_kge_ci_high = float(np.percentile(delta_kge_dist, 97.5))

    return nic_mean, nic_ci_low, nic_ci_high, d_kge_ci_low, d_kge_ci_high

def main():
    print("================================================================================")
    print("  EVALUATION DES DEBITS HYMAP-2 (LINRES = 0) AVEC RUNS CORRIGES (PARTIE A4)")
    print("================================================================================")

    print("\n>>> 1. Extraction / Chargement des simulations journalières 2018...")
    sim_dfs = {}
    for exp_id, exp_cfg in EXPERIMENTS.items():
        sim_dfs[exp_id] = extract_simulated_streamflow_2018(exp_id, exp_cfg)

    print("\n>>> 2. Chargement des observations 2018...")
    df_obs_daily = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_daily.csv"))
    df_obs_daily["year"] = pd.to_datetime(df_obs_daily["date"]).dt.year
    df_obs_daily_2018 = df_obs_daily[df_obs_daily["year"] == 2018].copy()

    df_obs_monthly = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_monthly.csv"))
    df_obs_monthly_2018 = df_obs_monthly[df_obs_monthly["annee"] == 2018].copy()
    df_obs_monthly_2018["year_month"] = df_obs_monthly_2018["annee"].astype(str) + "-" + df_obs_monthly_2018["mois"].astype(str).str.zfill(2)

    # Paires d'évaluation NIC incluant les deux paires demandées en A4
    NIC_PAIRS = [
        ("DA_corr", "ENS_corr", "DA_corr vs ENS_corr (Effet observations systeme corrige)"),
        ("ENS_corr", "OL_DAIC", "ENS_corr vs OL_DAIC (Effet residuel ensemble corrige)"),
        ("DA_nocdf", "ENS_OPL", "DA_nocdf vs ENS_OPL (Effet observations systeme production)"),
        ("ENS_OPL", "OL_DAIC", "ENS_OPL vs OL_DAIC (Effet ensemble production)"),
        ("DA_nocdf_nowilt", "DA_nocdf", "DA_nocdf_nowilt vs DA_nocdf (Effet filtre fletrissement)"),
        ("DA_nocdf", "OPL", "DA_nocdf vs OPL (Comparaison naive production)")
    ]

    SEASONS = {
        "Annual": lambda m: np.ones_like(m, dtype=bool),
        "Wet_Nov_Apr": lambda m: np.isin(m, [11, 12, 1, 2, 3, 4]),
        "Dry_May_Oct": lambda m: np.isin(m, [5, 6, 7, 8, 9, 10]),
        "Excl_Jan": lambda m: np.isin(m, list(range(2, 13))),
    }

    metrics_records = []
    nic_records = []

    print("\n>>> 3. Calcul des métriques journalières pour les 4 stations à pas journalier...")
    daily_stations = [sid for sid, info in RETAINED_STATIONS.items() if info["timestep"] == "journalier"]
    for sid in daily_stations:
        s_info = RETAINED_STATIONS[sid]
        sub_obs = df_obs_daily_2018[df_obs_daily_2018["station_id"] == sid].copy()
        if len(sub_obs) == 0:
            print(f"  [ATTENTION] Aucune obs journalière 2018 pour {sid} !")
            continue

        base_df = sub_obs[["date", "q_m3s"]].rename(columns={"q_m3s": "obs"}).dropna()
        for exp_id in EXPERIMENTS:
            s_exp = sim_dfs[exp_id][["date", sid]].rename(columns={sid: exp_id})
            base_df = base_df.merge(s_exp, on="date", how="inner")

        base_df["month"] = pd.to_datetime(base_df["date"]).dt.month

        for season_name, season_fn in SEASONS.items():
            mask = season_fn(base_df["month"].values)
            df_season = base_df[mask]
            obs_vals = df_season["obs"].values
            dates_vals = df_season["date"].values

            kge_map = {}
            for exp_id in EXPERIMENTS:
                sim_vals = df_season[exp_id].values
                m = compute_hydrological_metrics(obs_vals, sim_vals, dates_vals)
                kge_map[exp_id] = m["kge_2012"]
                rec = {
                    "experiment": exp_id,
                    "station_id": sid,
                    "station_name": s_info["name"],
                    "bassin": s_info["basin"],
                    "statut": s_info["statut"],
                    "timestep": "journalier",
                    "season": season_name,
                    **m
                }
                metrics_records.append(rec)

            for target_exp, ref_exp, pair_desc in NIC_PAIRS:
                k_t = kge_map[target_exp]
                k_r = kge_map[ref_exp]
                if not np.isnan(k_t) and not np.isnan(k_r):
                    d_kge = k_t - k_r
                    denom = 1.0 - k_r
                    nic_val = d_kge / denom if abs(denom) > 1e-6 else np.nan
                else:
                    d_kge, nic_val = np.nan, np.nan

                if season_name == "Annual":
                    boot_res = moving_block_bootstrap_nic(
                        base_df["obs"].values,
                        base_df[target_exp].values,
                        base_df[ref_exp].values,
                        block_len=30, n_boot=1000
                    )
                    nic_b_mean, nic_ci_l, nic_ci_h, dkge_ci_l, dkge_ci_h = boot_res
                else:
                    nic_b_mean, nic_ci_l, nic_ci_h, dkge_ci_l, dkge_ci_h = np.nan, np.nan, np.nan, np.nan, np.nan

                nic_rec = {
                    "pair": f"{target_exp} vs {ref_exp}",
                    "pair_description": pair_desc,
                    "station_id": sid,
                    "station_name": s_info["name"],
                    "bassin": s_info["basin"],
                    "statut": s_info["statut"],
                    "timestep": "journalier",
                    "season": season_name,
                    "kge_target": k_t,
                    "kge_ref": k_r,
                    "delta_kge": d_kge,
                    "nic": nic_val,
                    "nic_boot_mean": nic_b_mean,
                    "nic_ci95_low": nic_ci_l,
                    "nic_ci95_high": nic_ci_h,
                    "delta_kge_ci95_low": dkge_ci_l,
                    "delta_kge_ci95_high": dkge_ci_h
                }
                nic_records.append(nic_rec)

    print("\n>>> 4. Calcul des métriques mensuelles pour TOUTES les 10 stations retenues...")
    for sid, s_info in RETAINED_STATIONS.items():
        if s_info["timestep"] == "mensuel":
            sub_m = df_obs_monthly_2018[df_obs_monthly_2018["station_id"] == sid].copy()
            df_m_obs = sub_m[["year_month", "q_m3s"]].rename(columns={"q_m3s": "obs"}).dropna()
        else:
            sub_d = df_obs_daily_2018[df_obs_daily_2018["station_id"] == sid].copy()
            sub_d["year_month"] = pd.to_datetime(sub_d["date"]).dt.strftime("%Y-%m")
            df_m_obs = sub_d.groupby("year_month")["q_m3s"].mean().reset_index().rename(columns={"q_m3s": "obs"})

        if len(df_m_obs) == 0:
            print(f"  [ATTENTION] Aucune obs mensuelle pour {sid} !")
            continue

        base_m = df_m_obs.copy()
        for exp_id in EXPERIMENTS:
            s_exp = sim_dfs[exp_id][["date", sid]].copy()
            s_exp["year_month"] = pd.to_datetime(s_exp["date"]).dt.strftime("%Y-%m")
            m_exp = s_exp.groupby("year_month")[sid].mean().reset_index().rename(columns={sid: exp_id})
            base_m = base_m.merge(m_exp, on="year_month", how="inner")

        base_m["month"] = base_m["year_month"].str.split("-").str[1].astype(int)

        for season_name, season_fn in SEASONS.items():
            mask = season_fn(base_m["month"].values)
            df_season = base_m[mask]
            obs_vals = df_season["obs"].values
            dates_vals = df_season["year_month"].values

            kge_map = {}
            for exp_id in EXPERIMENTS:
                sim_vals = df_season[exp_id].values
                m = compute_hydrological_metrics(obs_vals, sim_vals, dates_vals)
                kge_map[exp_id] = m["kge_2012"]
                rec = {
                    "experiment": exp_id,
                    "station_id": sid,
                    "station_name": s_info["name"],
                    "bassin": s_info["basin"],
                    "statut": s_info["statut"],
                    "timestep": "mensuel",
                    "season": season_name,
                    **m
                }
                metrics_records.append(rec)

            for target_exp, ref_exp, pair_desc in NIC_PAIRS:
                k_t = kge_map[target_exp]
                k_r = kge_map[ref_exp]
                if not np.isnan(k_t) and not np.isnan(k_r):
                    d_kge = k_t - k_r
                    denom = 1.0 - k_r
                    nic_val = d_kge / denom if abs(denom) > 1e-6 else np.nan
                else:
                    d_kge, nic_val = np.nan, np.nan

                nic_rec = {
                    "pair": f"{target_exp} vs {ref_exp}",
                    "pair_description": pair_desc,
                    "station_id": sid,
                    "station_name": s_info["name"],
                    "bassin": s_info["basin"],
                    "statut": s_info["statut"],
                    "timestep": "mensuel",
                    "season": season_name,
                    "kge_target": k_t,
                    "kge_ref": k_r,
                    "delta_kge": d_kge,
                    "nic": nic_val,
                    "nic_boot_mean": np.nan,
                    "nic_ci95_low": np.nan,
                    "nic_ci95_high": np.nan,
                    "delta_kge_ci95_low": np.nan,
                    "delta_kge_ci95_high": np.nan
                }
                nic_records.append(nic_rec)

    df_metrics = pd.DataFrame(metrics_records)
    df_nic = pd.DataFrame(nic_records)

    out_metrics = os.path.join(TABLES_DIR, "streamflow_metrics_corrected_2018.csv")
    out_nic = os.path.join(TABLES_DIR, "streamflow_nic_corrected_2018.csv")

    df_metrics.to_csv(out_metrics, index=False)
    df_nic.to_csv(out_nic, index=False)

    print(f"\n[OK] Sauvegarde terminée :")
    print(f"  - {out_metrics} ({len(df_metrics)} lignes)")
    print(f"  - {out_nic} ({len(df_nic)} lignes)")
    print("================================================================================")

if __name__ == "__main__":
    main()
