#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step9_streamflow_metrics_2017.py
--------------------------------
Partie B3 : Évaluation des débits HyMAP-2 linres0 aux stations hydrométriques pour 2017.

Expériences 2017 :
  - OPL, OL_DAIC, ENS_OPL, DA_nocdf, DA_cdf, DA_nocdf_nowilt
10 Stations :
  - Journalières : Lalla Chafia, Sidi Jabeur, Ain Loudah, SM Cherif
  - Mensuelles : Ain Timedrine, Ait Khabbach, Azzaba, Dar El Hamra, Pont de Mdez, Pont Ait Aissa
Métriques :
  - KGE (2012, 2009), composantes (r, gamma, beta, alpha), NSE, logNSE (eps = 0.01 * mean_obs),
    débit JJA, jours à débit nul, pic et déphasage.
  - Saisons : Annual, Wet_Nov_Apr, Dry_May_Oct, Excl_Jan.
  - NIC avec bootstrap par blocs mobiles (30 jours, 1000 tirages, seed=42) :
      * DA_nocdf vs ENS_OPL
      * ENS_OPL vs OL_DAIC
      * DA_nocdf_nowilt vs DA_nocdf
      * DA_nocdf vs OPL

Sorties :
  - paper1/tables/streamflow_metrics_2017.csv
  - paper1/tables/streamflow_nic_2017.csv
"""

import os
import glob
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
ROUTING_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/routing")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
CACHE_DIR = os.path.join(ROUTING_DIR, "cache_streamflow_2017")
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

EXPERIMENTS_2017 = {
    "OPL": {
        "name": "Open-Loop linres0",
        "dir": os.path.join(ROUTING_DIR, "output/OPL_linres0_2016_2020/ROUTING"),
    },
    "OL_DAIC": {
        "name": "OL DAIC 2017 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/OL_DAIC_2017_linres0/ROUTING"),
    },
    "ENS_OPL": {
        "name": "ENS OPL 2017 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/ENS_OPL_2017_linres0/ROUTING"),
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
        "name": "DA-NoCDF NoWilt 2017 linres0",
        "dir": os.path.join(ROUTING_DIR, "output/DA_nocdf_nowilt_2017_linres0/ROUTING"),
    }
}

def extract_simulated_streamflow_2017(exp_id, exp_cfg):
    cache_file = os.path.join(CACHE_DIR, f"streamflow_2017_{exp_id}.csv")
    if os.path.exists(cache_file):
        df_cached = pd.read_csv(cache_file)
        if len(df_cached) == 365 and "date" in df_cached.columns:
            print(f"  [{exp_id}] En cache ({len(df_cached)} jours).")
            return df_cached

    print(f"  [{exp_id}] Extraction depuis NetCDF dans {exp_cfg['dir']}...")
    files_2017 = sorted(glob.glob(os.path.join(exp_cfg['dir'], "2017*/**/LIS_HIST_*.d01.nc"), recursive=True))
    file_20180101 = os.path.join(exp_cfg['dir'], "201801/LIS_HIST_201801010000.d01.nc")
    if os.path.exists(file_20180101) and file_20180101 not in files_2017:
        files_2017.append(file_20180101)

    records = []
    seen_dates = set()
    for fpath in sorted(files_2017):
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

                if not dt_str.startswith("2017-"):
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
        dates_arr = dates_arr[valid]

    n = len(obs_arr)
    if n < 5:
        return {
            "n_obs": n, "mean_obs_m3s": np.nan, "mean_sim_m3s": np.nan,
            "bias_m3s": np.nan, "rel_bias_pct": np.nan, "rmse_m3s": np.nan,
            "r": np.nan, "gamma": np.nan, "beta": np.nan, "alpha": np.nan,
            "kge_2012": np.nan, "kge_2009": np.nan,
            "nse": np.nan, "nse_log": np.nan, "eps_m3s": np.nan,
            "zero_days_obs": np.nan, "zero_days_sim": np.nan,
            "summer_bias_jja_m3s": np.nan, "summer_rel_bias_jja_pct": np.nan,
            "peak_obs_m3s": np.nan, "peak_obs_date": "",
            "peak_sim_m3s": np.nan, "peak_sim_date": "",
            "peak_bias_m3s": np.nan, "peak_timing_days": np.nan
        }

    mu_o = float(np.mean(obs_arr))
    mu_s = float(np.mean(sim_arr))
    std_o = float(np.std(obs_arr, ddof=1)) if n > 1 else 0.0
    std_s = float(np.std(sim_arr, ddof=1)) if n > 1 else 0.0

    bias = mu_s - mu_o
    rel_bias = (bias / mu_o * 100.0) if abs(mu_o) > 1e-6 else np.nan
    rmse = float(np.sqrt(np.mean((sim_arr - obs_arr)**2)))

    # Corrélation r
    if std_o > 1e-6 and std_s > 1e-6:
        r = float(np.corrcoef(obs_arr, sim_arr)[0, 1])
    else:
        r = 0.0

    # Biais beta
    beta = (mu_s / mu_o) if abs(mu_o) > 1e-6 else np.nan

    # Variabilité alpha (2009) et gamma (2012)
    alpha = (std_s / std_o) if abs(std_o) > 1e-6 else np.nan
    cv_s = (std_s / mu_s) if abs(mu_s) > 1e-6 else np.nan
    cv_o = (std_o / mu_o) if abs(mu_o) > 1e-6 else np.nan
    gamma = (cv_s / cv_o) if not np.isnan(cv_s) and not np.isnan(cv_o) and abs(cv_o) > 1e-6 else np.nan

    # KGE
    if not np.isnan(r) and not np.isnan(beta) and not np.isnan(gamma):
        ed_2012 = np.sqrt((r - 1.0)**2 + (gamma - 1.0)**2 + (beta - 1.0)**2)
        kge_2012 = float(1.0 - ed_2012)
    else:
        kge_2012 = np.nan

    if not np.isnan(r) and not np.isnan(beta) and not np.isnan(alpha):
        ed_2009 = np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)
        kge_2009 = float(1.0 - ed_2009)
    else:
        kge_2009 = np.nan

    # NSE
    ss_res = np.sum((sim_arr - obs_arr)**2)
    ss_tot = np.sum((obs_arr - mu_o)**2)
    nse = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-6 else np.nan

    # logNSE (avec eps = 0.01 * mean(obs))
    eps = max(1e-4, 0.01 * mu_o)
    log_o = np.log(np.maximum(obs_arr, 0.0) + eps)
    log_s = np.log(np.maximum(sim_arr, 0.0) + eps)
    ss_res_log = np.sum((log_s - log_o)**2)
    ss_tot_log = np.sum((log_o - np.mean(log_o))**2)
    nse_log = float(1.0 - (ss_res_log / ss_tot_log)) if ss_tot_log > 1e-6 else np.nan

    # Jours à débit nul (< 0.001 m3/s)
    zero_obs = int(np.sum(obs_arr < 1e-3))
    zero_sim = int(np.sum(sim_arr < 1e-3))

    # Débit estival JJA
    summer_bias_jja = np.nan
    summer_rel_bias_jja = np.nan
    if dates_arr is not None:
        months = np.array([int(str(d).split("-")[1]) for d in dates_arr])
        jja_mask = np.isin(months, [6, 7, 8])
        if np.sum(jja_mask) >= 5:
            mu_o_jja = float(np.mean(obs_arr[jja_mask]))
            mu_s_jja = float(np.mean(sim_arr[jja_mask]))
            summer_bias_jja = float(mu_s_jja - mu_o_jja)
            summer_rel_bias_jja = float((summer_bias_jja / mu_o_jja * 100.0) if abs(mu_o_jja) > 1e-6 else np.nan)

    # Pic hydrologique
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
    print("  EVALUATION DES DEBITS HYMAP-2 (LINRES = 0) 2017 (PARTIE B3)")
    print("================================================================================")

    print("\n>>> 1. Extraction / Chargement des simulations journalières 2017...")
    sim_dfs = {}
    for exp_id, exp_cfg in EXPERIMENTS_2017.items():
        sim_dfs[exp_id] = extract_simulated_streamflow_2017(exp_id, exp_cfg)

    print("\n>>> 2. Chargement des observations 2017...")
    df_obs_daily = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_daily.csv"))
    df_obs_daily["year"] = pd.to_datetime(df_obs_daily["date"]).dt.year
    df_obs_daily_2017 = df_obs_daily[df_obs_daily["year"] == 2017].copy()

    df_obs_monthly = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_monthly.csv"))
    df_obs_monthly_2017 = df_obs_monthly[df_obs_monthly["annee"] == 2017].copy()
    df_obs_monthly_2017["year_month"] = df_obs_monthly_2017["annee"].astype(str) + "-" + df_obs_monthly_2017["mois"].astype(str).str.zfill(2)

    NIC_PAIRS_2017 = [
        ("DA_nocdf", "ENS_OPL", "DA_nocdf vs ENS_OPL (Effet observations production 2017)"),
        ("ENS_OPL", "OL_DAIC", "ENS_OPL vs OL_DAIC (Effet ensemble production 2017)"),
        ("DA_nocdf_nowilt", "DA_nocdf", "DA_nocdf_nowilt vs DA_nocdf (Effet filtre fletrissement 2017)"),
        ("DA_nocdf", "OPL", "DA_nocdf vs OPL (Comparaison naive production 2017)")
    ]

    SEASONS = {
        "Annual": lambda m: np.ones_like(m, dtype=bool),
        "Wet_Nov_Apr": lambda m: np.isin(m, [11, 12, 1, 2, 3, 4]),
        "Dry_May_Oct": lambda m: np.isin(m, [5, 6, 7, 8, 9, 10]),
        "Excl_Jan": lambda m: np.isin(m, list(range(2, 13))),
    }

    metrics_records = []
    nic_records = []

    print("\n>>> 3. Calcul des métriques journalières pour les stations journalières...")
    daily_stations = [sid for sid, info in RETAINED_STATIONS.items() if info["timestep"] == "journalier"]
    for sid in daily_stations:
        s_info = RETAINED_STATIONS[sid]
        sub_obs = df_obs_daily_2017[df_obs_daily_2017["station_id"] == sid].copy()
        if len(sub_obs) == 0:
            print(f"  [ATTENTION] Aucune obs journalière 2017 pour {sid} !")
            continue

        base_df = sub_obs[["date", "q_m3s"]].rename(columns={"q_m3s": "obs"}).dropna()
        for exp_id in EXPERIMENTS_2017:
            s_exp = sim_dfs[exp_id][["date", sid]].rename(columns={sid: exp_id})
            base_df = base_df.merge(s_exp, on="date", how="inner")

        base_df["month"] = pd.to_datetime(base_df["date"]).dt.month

        for season_name, season_fn in SEASONS.items():
            mask = season_fn(base_df["month"].values)
            df_season = base_df[mask]
            obs_vals = df_season["obs"].values
            dates_vals = df_season["date"].values

            kge_map = {}
            for exp_id in EXPERIMENTS_2017:
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

            for target_exp, ref_exp, pair_desc in NIC_PAIRS_2017:
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
            sub_m = df_obs_monthly_2017[df_obs_monthly_2017["station_id"] == sid].copy()
            df_m_obs = sub_m[["year_month", "q_m3s"]].rename(columns={"q_m3s": "obs"}).dropna()
        else:
            sub_d = df_obs_daily_2017[df_obs_daily_2017["station_id"] == sid].copy()
            sub_d["year_month"] = pd.to_datetime(sub_d["date"]).dt.strftime("%Y-%m")
            df_m_obs = sub_d.groupby("year_month")["q_m3s"].mean().reset_index().rename(columns={"q_m3s": "obs"})

        if len(df_m_obs) == 0:
            print(f"  [ATTENTION] Aucune obs mensuelle pour {sid} en 2017 !")
            continue

        base_m = df_m_obs.copy()
        for exp_id in EXPERIMENTS_2017:
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
            for exp_id in EXPERIMENTS_2017:
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

            for target_exp, ref_exp, pair_desc in NIC_PAIRS_2017:
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
    out_metrics_csv = os.path.join(TABLES_DIR, "streamflow_metrics_2017.csv")
    df_metrics.to_csv(out_metrics_csv, index=False)
    print(f"\n[OK] Table streamflow metrics sauvegardée : {out_metrics_csv} ({len(df_metrics)} lignes).")

    df_nic = pd.DataFrame(nic_records)
    out_nic_csv = os.path.join(TABLES_DIR, "streamflow_nic_2017.csv")
    df_nic.to_csv(out_nic_csv, index=False)
    print(f"[OK] Table streamflow NIC sauvegardée : {out_nic_csv} ({len(df_nic)} lignes).")

    print(df_metrics[(df_metrics["station_id"] == "b_l_chafia") & (df_metrics["season"] == "Annual") & (df_metrics["timestep"] == "journalier")][["experiment", "kge_2012", "r", "beta", "gamma", "nse"]])

if __name__ == "__main__":
    main()
