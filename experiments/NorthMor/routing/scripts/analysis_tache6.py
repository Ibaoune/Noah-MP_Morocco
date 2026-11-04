#!/usr/bin/env python3
"""
TACHE 6 : DECOMPOSITION DE L'ERREUR. ANALYSE SEULE, AUCUN RUN.
Auteur : Antigravity (Assistant IA)
Date : 2026-10-25
"""

import os
import glob
import datetime
import calendar
from collections import deque
import numpy as np
import pandas as pd
import netCDF4 as nc

def main():
    print("=" * 80)
    print("TACHE 6 : DECOMPOSITION DE L'ERREUR (ANALYSE SEULE)")
    print("=" * 80)

    base_dir = "experiments/NorthMor/routing"
    out_dir = os.path.join(base_dir, "output/OPL_2016_2020")
    clean_dir = "data/streamflow_clean"
    ldt_file = os.path.join(base_dir, "ldt_hymap/lis_input.d01.nc")
    runoff_dir = os.path.join(base_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL")
    routing_dir = os.path.join(out_dir, "ROUTING")

    # 1. Charger appariement
    pairing_csv = os.path.join(out_dir, "t5bis_stations_pairing.csv")
    df_p = pd.read_csv(pairing_csv)
    print(f"Chargement appariements : {len(df_p)} stations")

    # 2. Reseau d'ecoulement et masques de bassins amont
    with nc.Dataset(ldt_file) as ds:
        fd_x = np.ma.filled(ds.variables["HYMAP_flow_direction_x"][:], -9)
        fd_y = np.ma.filled(ds.variables["HYMAP_flow_direction_y"][:], -9)
        drain_area = np.ma.filled(ds.variables["HYMAP_drain_area"][:], 0.0)
        grid_area = np.ma.filled(ds.variables["HYMAP_grid_area"][:], 0.0)

    upstreams = {}
    R, C = fd_x.shape
    for r in range(R):
        for c in range(C):
            nx = int(round(float(fd_x[r, c]))) - 1
            ny = int(round(float(fd_y[r, c]))) - 1
            if 0 <= ny < R and 0 <= nx < C:
                if (ny, nx) not in upstreams:
                    upstreams[(ny, nx)] = []
                upstreams[(ny, nx)].append((r, c))

    def get_catchment(target_r, target_c):
        visited = set([(target_r, target_c)])
        queue = deque([(target_r, target_c)])
        while queue:
            curr = queue.popleft()
            for parent in upstreams.get(curr, []):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return visited

    station_catchments = {}
    station_masks = {}
    for _, row in df_p.iterrows():
        sid = row["station_id"]
        r, c = int(row["row_hymap"]), int(row["col_hymap"])
        cat = get_catchment(r, c)
        station_catchments[sid] = cat
        mask = np.zeros((R, C), dtype=bool)
        for cr, cc in cat:
            mask[cr, cc] = True
        station_masks[sid] = mask

    # 3. Extraction / chargement de Vin journalier (m3/jour)
    vin_cache = os.path.join(out_dir, "t6_vin_daily_12stations.csv")
    if os.path.exists(vin_cache):
        print(f"Chargement Vin journalier depuis cache : {vin_cache}")
        df_vin_daily = pd.read_csv(vin_cache)
    else:
        print("Extraction de Vin journalier (1826 fichiers de ruissellement)...")
        runoff_files = sorted(glob.glob(os.path.join(runoff_dir, "*/*.nc")))
        vin_records = []
        for idx, rf in enumerate(runoff_files):
            fname = os.path.basename(rf)
            # Ex: LIS_HIST_201601020000.d01.nc -> date = 2016-01-01
            dt_str = fname.replace("LIS_HIST_", "").replace("0000.d01.nc", "")
            file_dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
            sim_dt = file_dt - datetime.timedelta(days=1)
            sim_date_str = sim_dt.strftime("%Y-%m-%d")
            if sim_date_str < "2016-01-01" or sim_date_str > "2020-12-31":
                continue

            with nc.Dataset(rf) as ds:
                qs = np.nan_to_num(ds.variables["Qs_tavg"][:])
                qsb = np.nan_to_num(ds.variables["Qsb_tavg"][:])
                if qs.ndim == 3: qs = qs[0]
                if qsb.ndim == 3: qsb = qsb[0]
                flux_m3 = (np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0

            row_data = {"date": sim_date_str}
            for sid, mask in station_masks.items():
                row_data[sid] = float(np.sum(flux_m3[mask]))
            vin_records.append(row_data)

            if (idx + 1) % 365 == 0:
                print(f"  Vin traite : {idx + 1}/{len(runoff_files)} jours...")

        df_vin_daily = pd.DataFrame(vin_records).sort_values("date").reset_index(drop=True)
        df_vin_daily.to_csv(vin_cache, index=False)
        print(f"Vin journalier sauvegarde : {vin_cache}")

    # 4. Extraction / chargement de Qsim journalier (m3/s)
    sim_cache = os.path.join(out_dir, "t6_sim_daily_12stations.csv")
    if os.path.exists(sim_cache):
        print(f"Chargement Qsim journalier depuis cache : {sim_cache}")
        df_sim_daily = pd.read_csv(sim_cache)
    else:
        print("Extraction de Qsim journalier depuis les sorties HyMAP2...")
        hist_files = sorted(glob.glob(os.path.join(routing_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))
        sim_records = []
        for idx, fpath in enumerate(hist_files):
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                sim_date_str = sim_dt.strftime("%Y-%m-%d")
                if sim_date_str < "2016-01-01" or sim_date_str > "2020-12-31":
                    continue

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3: flow = flow[0]

                row_data = {"date": sim_date_str}
                for _, p in df_p.iterrows():
                    sid = p["station_id"]
                    r, c = int(p["row_hymap"]), int(p["col_hymap"])
                    row_data[sid] = float(flow[r, c])
                sim_records.append(row_data)

            if (idx + 1) % 365 == 0:
                print(f"  Qsim traite : {idx + 1}/{len(hist_files)} jours...")

        df_sim_daily = pd.DataFrame(sim_records).sort_values("date").reset_index(drop=True)
        df_sim_daily.to_csv(sim_cache, index=False)
        print(f"Qsim journalier sauvegarde : {sim_cache}")

    # Charger observations
    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))

    # =========================================================================
    # ETAPE 1 : DECOMPOSITION EN TROIS VOLUMES (Vin, Vsim, Vobs) PAR STATION
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPE 1 : DECOMPOSITION EN TROIS VOLUMES (Vin, Vsim, Vobs)")
    print("=" * 80)

    decomp_records = []
    years = [2016, 2017, 2018, 2019, 2020]

    # Pre-agreger monthly simulated et vin
    df_vin_daily["year_month"] = df_vin_daily["date"].str.slice(0, 7)
    df_vin_daily["year"] = df_vin_daily["date"].str.slice(0, 4).astype(int)
    df_vin_monthly = df_vin_daily.drop(columns=["date", "year"]).groupby("year_month").sum().reset_index()

    df_sim_daily["year_month"] = df_sim_daily["date"].str.slice(0, 7)
    df_sim_daily["year"] = df_sim_daily["date"].str.slice(0, 4).astype(int)
    # Pour sim, volume mensuel = somme des Q_sim(m3/s) * 86400
    df_sim_vol_daily = df_sim_daily.copy()
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        df_sim_vol_daily[sid] = df_sim_vol_daily[sid] * 86400.0
    df_sim_monthly_vol = df_sim_vol_daily.drop(columns=["date", "year"]).groupby("year_month").sum().reset_index()

    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        type_pas = p["type_pas"]
        area_km2 = p["aire_hymap_km2"]
        area_m2 = area_km2 * 1e6

        if type_pas == "journalier":
            # Stations journalieres (Bouregreg)
            obs_sub = df_obs_daily[(df_obs_daily["station_id"] == sid) & 
                                   (df_obs_daily["date"] >= "2016-01-01") & 
                                   (df_obs_daily["date"] <= "2020-12-31")].copy()
            # Fusionner pour n'avoir QUE les jours observes
            m_daily = pd.merge(obs_sub[["date", "q_m3s"]], df_sim_daily[["date", sid]], on="date")
            m_daily = pd.merge(m_daily, df_vin_daily[["date", sid]], on="date", suffixes=("_sim_q", "_vin_m3"))
            m_daily = m_daily.dropna(subset=["q_m3s"])
            m_daily["v_obs_m3"] = m_daily["q_m3s"] * 86400.0
            m_daily["v_sim_m3"] = m_daily[f"{sid}_sim_q"] * 86400.0
            m_daily["v_in_m3"] = m_daily[f"{sid}_vin_m3"]
            m_daily["year"] = m_daily["date"].str.slice(0, 4).astype(int)

            # Calcul annuel et 5 ans
            for yr in years + ["5ans_total"]:
                if yr == "5ans_total":
                    sub_y = m_daily
                    label_yr = "2016-2020"
                else:
                    sub_y = m_daily[m_daily["year"] == yr]
                    label_yr = str(yr)

                n_days = len(sub_y)
                if n_days == 0: continue
                v_in_hm3 = sub_y["v_in_m3"].sum() / 1e6
                v_sim_hm3 = sub_y["v_sim_m3"].sum() / 1e6
                v_obs_hm3 = sub_y["v_obs_m3"].sum() / 1e6

                # Lames d'eau en mm/an
                years_equiv = n_days / 365.25
                h_in_mm = (v_in_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv
                h_sim_mm = (v_sim_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv
                h_obs_mm = (v_obs_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv

                r_in_obs = (v_in_hm3 / v_obs_hm3) if v_obs_hm3 > 0 else np.nan
                r_sim_in = (v_sim_hm3 / v_in_hm3) if v_in_hm3 > 0 else np.nan
                r_sim_obs = (v_sim_hm3 / v_obs_hm3) if v_obs_hm3 > 0 else np.nan

                decomp_records.append({
                    "station_id": sid,
                    "nom": nom,
                    "bassin": bassin,
                    "periode": label_yr,
                    "n_pas_eval": n_days,
                    "unite_pas": "jours",
                    "aire_km2": area_km2,
                    "Vin_hm3": v_in_hm3,
                    "Vsim_hm3": v_sim_hm3,
                    "Vobs_hm3": v_obs_hm3,
                    "Hin_mm_an": h_in_mm,
                    "Hsim_mm_an": h_sim_mm,
                    "Hobs_mm_an": h_obs_mm,
                    "Vin_sur_Vobs": r_in_obs,
                    "Vsim_sur_Vin": r_sim_in,
                    "Vsim_sur_Vobs": r_sim_obs
                })
        else:
            # Stations mensuelles (Sebou et Adamna)
            obs_sub = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & 
                                     (df_obs_monthly["annee"] >= 2016) & 
                                     (df_obs_monthly["annee"] <= 2020)].copy()
            obs_sub["year_month"] = obs_sub["annee"].astype(str) + "-" + obs_sub["mois"].astype(str).str.zfill(2)
            # Calculer n_jours dans chaque mois
            def get_month_days(ym):
                y, m = int(ym[:4]), int(ym[5:7])
                return calendar.monthrange(y, m)[1]
            obs_sub["n_days"] = obs_sub["year_month"].apply(get_month_days)
            obs_sub["v_obs_m3"] = obs_sub["q_m3s"] * obs_sub["n_days"] * 86400.0

            m_monthly = pd.merge(obs_sub[["year_month", "annee", "mois", "n_days", "v_obs_m3", "q_m3s"]], 
                                 df_sim_monthly_vol[["year_month", sid]], on="year_month")
            m_monthly = pd.merge(m_monthly, df_vin_monthly[["year_month", sid]], on="year_month", suffixes=("_sim_vol", "_vin_vol"))
            m_monthly = m_monthly.dropna(subset=["q_m3s"])
            m_monthly["v_sim_m3"] = m_monthly[f"{sid}_sim_vol"]
            m_monthly["v_in_m3"] = m_monthly[f"{sid}_vin_vol"]

            for yr in years + ["5ans_total"]:
                if yr == "5ans_total":
                    sub_y = m_monthly
                    label_yr = "2016-2020"
                else:
                    sub_y = m_monthly[m_monthly["annee"] == yr]
                    label_yr = str(yr)

                n_months = len(sub_y)
                if n_months == 0: continue
                n_days = sub_y["n_days"].sum()
                v_in_hm3 = sub_y["v_in_m3"].sum() / 1e6
                v_sim_hm3 = sub_y["v_sim_m3"].sum() / 1e6
                v_obs_hm3 = sub_y["v_obs_m3"].sum() / 1e6

                years_equiv = n_days / 365.25
                h_in_mm = (v_in_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv
                h_sim_mm = (v_sim_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv
                h_obs_mm = (v_obs_hm3 * 1e6 / area_m2) * 1000.0 / years_equiv

                r_in_obs = (v_in_hm3 / v_obs_hm3) if v_obs_hm3 > 0 else np.nan
                r_sim_in = (v_sim_hm3 / v_in_hm3) if v_in_hm3 > 0 else np.nan
                r_sim_obs = (v_sim_hm3 / v_obs_hm3) if v_obs_hm3 > 0 else np.nan

                decomp_records.append({
                    "station_id": sid,
                    "nom": nom,
                    "bassin": bassin,
                    "periode": label_yr,
                    "n_pas_eval": n_months,
                    "unite_pas": "mois",
                    "aire_km2": area_km2,
                    "Vin_hm3": v_in_hm3,
                    "Vsim_hm3": v_sim_hm3,
                    "Vobs_hm3": v_obs_hm3,
                    "Hin_mm_an": h_in_mm,
                    "Hsim_mm_an": h_sim_mm,
                    "Hobs_mm_an": h_obs_mm,
                    "Vin_sur_Vobs": r_in_obs,
                    "Vsim_sur_Vin": r_sim_in,
                    "Vsim_sur_Vobs": r_sim_obs
                })

    df_decomp = pd.DataFrame(decomp_records)
    decomp_csv = os.path.join(out_dir, "t6_three_volumes_decomposition.csv")
    df_decomp.to_csv(decomp_csv, index=False)
    print(f"Table complete de decomposition sauvegardee : {decomp_csv}")

    # Affichage du tableau de synthese sur 5 ans (2016-2020)
    df_5ans = df_decomp[df_decomp["periode"] == "2016-2020"].copy()
    print("\n--- SYNTHESE 2016-2020 : DECOMPOSITION DES TROIS VOLUMES ---")
    cols_show = ["nom", "bassin", "aire_km2", "Vin_hm3", "Vsim_hm3", "Vobs_hm3", 
                 "Hin_mm_an", "Hsim_mm_an", "Hobs_mm_an", "Vin_sur_Vobs", "Vsim_sur_Vin", "Vsim_sur_Vobs"]
    print(df_5ans[cols_show].to_string(index=False, float_format=lambda x: f"{x:7.2f}"))

    # =========================================================================
    # ETAPE 2 : INDICE DE DEBIT DE BASE (BFI) SUR OBSERVE ET SIMULE
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPE 2 : INDICE DE DEBIT DE BASE (BFI) ET PROXIES")
    print("=" * 80)

    def bfi_lyne_hollick(q, alpha=0.925, passes=3):
        n = len(q)
        qf = np.zeros(n)
        for t in range(1, n):
            qf[t] = alpha * qf[t-1] + 0.5 * (1 + alpha) * (q[t] - q[t-1])
            if qf[t] < 0: qf[t] = 0
            if qf[t] > q[t]: qf[t] = q[t]
        if passes > 1:
            for t in range(n-2, -1, -1):
                qf[t] = alpha * qf[t+1] + 0.5 * (1 + alpha) * (qf[t] - qf[t+1])
                if qf[t] < 0: qf[t] = 0
                if qf[t] > q[t]: qf[t] = q[t]
        if passes > 2:
            for t in range(1, n):
                qf[t] = alpha * qf[t-1] + 0.5 * (1 + alpha) * (qf[t] - qf[t-1])
                if qf[t] < 0: qf[t] = 0
                if qf[t] > q[t]: qf[t] = q[t]
        qb = q - qf
        return float(np.sum(qb) / np.sum(q)) if np.sum(q) > 0 else np.nan

    def bfi_ukih(q, block_size=5):
        n = len(q)
        n_blocks = n // block_size
        m_vals, m_idx = [], []
        for b in range(n_blocks):
            block = q[b*block_size : (b+1)*block_size]
            min_i = np.argmin(block)
            m_vals.append(block[min_i])
            m_idx.append(b*block_size + min_i)
        tp_val, tp_idx = [], []
        for i in range(1, len(m_vals)-1):
            if 0.9 * m_vals[i] <= m_vals[i-1] and 0.9 * m_vals[i] <= m_vals[i+1]:
                tp_val.append(m_vals[i])
                tp_idx.append(m_idx[i])
        if len(tp_idx) < 2:
            return np.nan
        qb = np.interp(np.arange(n), tp_idx, tp_val)
        qb = np.minimum(qb, q)
        return float(np.sum(qb) / np.sum(q)) if np.sum(q) > 0 else np.nan

    bfi_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        type_pas = p["type_pas"]

        if type_pas == "journalier":
            obs_sub = df_obs_daily[(df_obs_daily["station_id"] == sid) & 
                                   (df_obs_daily["date"] >= "2016-01-01") & 
                                   (df_obs_daily["date"] <= "2020-12-31")].sort_values("date")
            merged_d = pd.merge(obs_sub[["date", "q_m3s"]], df_sim_daily[["date", sid]], on="date").dropna(subset=["q_m3s"])
            q_obs = merged_d["q_m3s"].values
            q_sim = merged_d[sid].values

            bfi_lh_o = bfi_lyne_hollick(q_obs)
            bfi_lh_s = bfi_lyne_hollick(q_sim)
            bfi_u_o = bfi_ukih(q_obs)
            bfi_u_s = bfi_ukih(q_sim)

            # Indicateurs mensuels de substitution
            merged_d["year_month"] = merged_d["date"].str.slice(0, 7)
            m_agg = merged_d.groupby("year_month").agg({"q_m3s": "mean", sid: "mean"}).reset_index()
            qm_o = m_agg["q_m3s"].values
            qm_s = m_agg[sid].values

            cv_m_o = float(np.std(qm_o) / np.mean(qm_o)) if np.mean(qm_o) > 0 else np.nan
            cv_m_s = float(np.std(qm_s) / np.mean(qm_s)) if np.mean(qm_s) > 0 else np.nan
            ratio_min_mean_o = float(np.min(qm_o) / np.mean(qm_o)) if np.mean(qm_o) > 0 else np.nan
            ratio_min_mean_s = float(np.min(qm_s) / np.mean(qm_s)) if np.mean(qm_s) > 0 else np.nan

            bfi_records.append({
                "station_id": sid, "nom": nom, "bassin": bassin, "pas": "journalier",
                "BFI_LH_Obs": bfi_lh_o, "BFI_LH_Sim": bfi_lh_s,
                "BFI_UKIH_Obs": bfi_u_o, "BFI_UKIH_Sim": bfi_u_s,
                "CV_mensuel_Obs": cv_m_o, "CV_mensuel_Sim": cv_m_s,
                "Qmin_sur_Qmean_Obs": ratio_min_mean_o, "Qmin_sur_Qmean_Sim": ratio_min_mean_s
            })
        else:
            obs_sub = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & 
                                     (df_obs_monthly["annee"] >= 2016) & 
                                     (df_obs_monthly["annee"] <= 2020)].copy()
            obs_sub["year_month"] = obs_sub["annee"].astype(str) + "-" + obs_sub["mois"].astype(str).str.zfill(2)
            merged_m = pd.merge(obs_sub[["year_month", "q_m3s"]], df_sim_monthly_vol[["year_month", sid]], on="year_month").dropna(subset=["q_m3s"])
            qm_o = merged_m["q_m3s"].values
            # Reconvertir volume mensuel en debit moyen mensuel m3/s
            def get_month_days(ym):
                y, m = int(ym[:4]), int(ym[5:7])
                return calendar.monthrange(y, m)[1]
            n_days_arr = np.array([get_month_days(ym) for ym in merged_m["year_month"]])
            qm_s = merged_m[sid].values / (n_days_arr * 86400.0)

            cv_m_o = float(np.std(qm_o) / np.mean(qm_o)) if np.mean(qm_o) > 0 else np.nan
            cv_m_s = float(np.std(qm_s) / np.mean(qm_s)) if np.mean(qm_s) > 0 else np.nan
            ratio_min_mean_o = float(np.min(qm_o) / np.mean(qm_o)) if np.mean(qm_o) > 0 else np.nan
            ratio_min_mean_s = float(np.min(qm_s) / np.mean(qm_s)) if np.mean(qm_s) > 0 else np.nan

            bfi_records.append({
                "station_id": sid, "nom": nom, "bassin": bassin, "pas": "mensuel",
                "BFI_LH_Obs": np.nan, "BFI_LH_Sim": np.nan,
                "BFI_UKIH_Obs": np.nan, "BFI_UKIH_Sim": np.nan,
                "CV_mensuel_Obs": cv_m_o, "CV_mensuel_Sim": cv_m_s,
                "Qmin_sur_Qmean_Obs": ratio_min_mean_o, "Qmin_sur_Qmean_Sim": ratio_min_mean_s
            })

    df_bfi = pd.DataFrame(bfi_records)
    bfi_csv = os.path.join(out_dir, "t6_baseflow_index_comparison.csv")
    df_bfi.to_csv(bfi_csv, index=False)
    print(f"Table BFI sauvegardee : {bfi_csv}")
    print("\n--- TABLEAU BFI ET INDICATEURS DE REGULATION ---")
    print(df_bfi[["nom", "bassin", "pas", "BFI_UKIH_Obs", "BFI_UKIH_Sim", "CV_mensuel_Obs", "CV_mensuel_Sim", "Qmin_sur_Qmean_Obs", "Qmin_sur_Qmean_Sim"]].to_string(index=False, float_format=lambda x: f"{x:6.3f}"))

    # =========================================================================
    # ETAPE 3 : DEUX ANOMALIES A ELUCIDER
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPE 3 : DEUX ANOMALIES A ELUCIDER")
    print("=" * 80)

    # 3a. Bouregreg specific discharge & fenetre 5x5
    print("\n3a. Bouregreg : Analyse des debits specifiques et balayage 5x5...")
    with nc.Dataset(ldt_file) as ds:
        lats = ds.variables["lat"][:]
        lons = ds.variables["lon"][:]

    for sid in ["b_a_loudah", "b_s_cherif"]:
        row_p = df_p[df_p["station_id"] == sid].iloc[0]
        r_c, c_c = int(row_p["row_hymap"]), int(row_p["col_hymap"])
        nom = row_p["nom"]
        q_mean_obs = 0.288
        q_spec_current = q_mean_obs / (drain_area[r_c, c_c] / 1e6) * 1000.0

        print(f"\nStation {nom} ({sid}) :")
        print(f"  Maille actuelle [{r_c}, {c_c}] : Aire={drain_area[r_c, c_c]/1e6:.1f} km2 | q_spec obs = {q_spec_current:.3f} L/s/km2")
        print("  Balayage de la boite 5x5 (r in [r-2, r+2], c in [c-2, c+2]) :")
        cells_box = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                rr = r_c + dr
                cc = c_c + dc
                if 0 <= rr < R and 0 <= cc < C:
                    a_km2 = drain_area[rr, cc] / 1e6
                    q_sp = (q_mean_obs / a_km2 * 1000.0) if a_km2 > 0 else np.nan
                    cells_box.append({"dr": dr, "dc": dc, "r": rr, "c": cc, "aire_km2": a_km2, "q_spec": q_sp})
        df_box = pd.DataFrame(cells_box).sort_values("aire_km2", ascending=False)
        print(df_box.head(10).to_string(index=False, float_format=lambda x: f"{x:7.1f}"))

        # Aire necessaire pour avoir q_spec = 1.1 L/s/km2 (comme Sidi Jabeur / Lalla Chafia)
        target_qspec = 1.15 # L/s/km2
        area_needed = (q_mean_obs / (target_qspec * 1e-3))
        print(f"  -> Aire requise pour atteindre un debit specifique coherent (~1.15 L/s/km2) : {area_needed:.1f} km2")

    # 3b. Ait Khabbach historical series analysis
    print("\n3b. Ait Khabbach : Analyse de la serie historique complete (1970-2024)...")
    ak_all = df_obs_monthly[df_obs_monthly["station_id"] == "ait_khabbach"].copy()
    ak_all["decennie"] = (ak_all["annee"] // 10) * 10
    dec_stats = ak_all.groupby("decennie")["q_m3s"].agg(["count", "mean", "min", "max", "std"]).reset_index()
    dec_stats["q_spec_L_s_km2"] = dec_stats["mean"] / 1240.0 * 1000.0
    print("Statistiques par decennie a Ait Khabbach (Aire = 1240 km2) :")
    print(dec_stats.to_string(index=False, float_format=lambda x: f"{x:7.3f}"))

    # Comparer a Pont Ait Aissa
    paa_all = df_obs_monthly[df_obs_monthly["station_id"] == "pont_ait_aissa"].copy()
    paa_mean = paa_all["q_m3s"].mean()
    paa_qspec = paa_mean / 205.0 * 1000.0
    print(f"\nComparaison amont-aval sur l'Oued Guigou :")
    print(f"  Amont (Pont Ait Aissa) : Aire = 205 km2  | Qobs moyen = {paa_mean:.3f} m3/s | q_spec = {paa_qspec:.3f} L/s/km2")
    ak_mean_rec = ak_all[ak_all["annee"] >= 2000]["q_m3s"].mean()
    ak_qspec_rec = ak_mean_rec / 1240.0 * 1000.0
    print(f"  Aval  (Ait Khabbach)   : Aire = 1240 km2 | Qobs moyen = {ak_mean_rec:.3f} m3/s | q_spec = {ak_qspec_rec:.3f} L/s/km2")

    # =========================================================================
    # ETAPE 4 : CONTROLE DE L'AMPLITUDE (alpha, Q10, Q50, Q90)
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPE 4 : CONTROLE DE L'AMPLITUDE ET DES QUANTILES")
    print("=" * 80)

    amp_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        type_pas = p["type_pas"]

        if type_pas == "journalier":
            obs_sub = df_obs_daily[(df_obs_daily["station_id"] == sid) & 
                                   (df_obs_daily["date"] >= "2016-01-01") & 
                                   (df_obs_daily["date"] <= "2020-12-31")].sort_values("date")
            merged = pd.merge(obs_sub[["date", "q_m3s"]], df_sim_daily[["date", sid]], on="date").dropna(subset=["q_m3s"])
            qo = merged["q_m3s"].values
            qs = merged[sid].values
        else:
            obs_sub = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & 
                                     (df_obs_monthly["annee"] >= 2016) & 
                                     (df_obs_monthly["annee"] <= 2020)].copy()
            obs_sub["year_month"] = obs_sub["annee"].astype(str) + "-" + obs_sub["mois"].astype(str).str.zfill(2)
            merged = pd.merge(obs_sub[["year_month", "q_m3s"]], df_sim_monthly_vol[["year_month", sid]], on="year_month").dropna(subset=["q_m3s"])
            qo = merged["q_m3s"].values
            def get_month_days(ym):
                y, m = int(ym[:4]), int(ym[5:7])
                return calendar.monthrange(y, m)[1]
            n_days_arr = np.array([get_month_days(ym) for ym in merged["year_month"]])
            qs = merged[sid].values / (n_days_arr * 86400.0)

        sigma_o = float(np.std(qo))
        sigma_s = float(np.std(qs))
        alpha_val = sigma_s / sigma_o if sigma_o > 0 else np.nan

        # En hydrologie :
        # Q10 = quantile non depasse 90% du temps (hautes eaux, crue)
        # Q50 = mediane (50%)
        # Q90 = basses eaux non depassees 10% du temps (etiage)
        q10_o = float(np.percentile(qo, 90))
        q10_s = float(np.percentile(qs, 90))
        q50_o = float(np.percentile(qo, 50))
        q50_s = float(np.percentile(qs, 50))
        q90_o = float(np.percentile(qo, 10))
        q90_s = float(np.percentile(qs, 10))

        r_q10 = q10_s / q10_o if q10_o > 0 else np.nan
        r_q50 = q50_s / q50_o if q50_o > 0 else np.nan
        r_q90 = q90_s / q90_o if q90_o > 0 else np.nan

        amp_records.append({
            "station_id": sid, "nom": nom, "bassin": bassin, "pas": type_pas,
            "sigma_obs": sigma_o, "sigma_sim": sigma_s, "alpha": alpha_val,
            "Q10_high_obs": q10_o, "Q10_high_sim": q10_s, "Ratio_Q10_high": r_q10,
            "Q50_med_obs": q50_o, "Q50_med_sim": q50_s, "Ratio_Q50_med": r_q50,
            "Q90_low_obs": q90_o, "Q90_low_sim": q90_s, "Ratio_Q90_low": r_q90
        })

    df_amp = pd.DataFrame(amp_records)
    amp_csv = os.path.join(out_dir, "t6_amplitude_quantiles_control.csv")
    df_amp.to_csv(amp_csv, index=False)
    print(f"Table amplitude sauvegardee : {amp_csv}")
    print("\n--- TABLEAU CONTROLE D'AMPLITUDE ET QUANTILES ---")
    cols_amp = ["nom", "bassin", "pas", "alpha", "Q10_high_obs", "Q10_high_sim", "Ratio_Q10_high", 
                "Q50_med_obs", "Q50_med_sim", "Ratio_Q50_med", "Q90_low_obs", "Q90_low_sim", "Ratio_Q90_low"]
    print(df_amp[cols_amp].to_string(index=False, float_format=lambda x: f"{x:6.3f}"))

    print("\n=== ANALYSE DE LA TACHE 6 TERMINEE AVEC SUCCES ===")

if __name__ == "__main__":
    main()
