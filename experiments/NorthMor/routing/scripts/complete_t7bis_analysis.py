#!/usr/bin/env python3
"""
complete_t7bis_analysis.py
Tâche 7bis - Vérification complète de la simulation corrigée OPL 2016-2020 :
1. Distribution effective de tbsflw après application du plancher cntime/86400.
2. Diagnostic de vidange :
   - Constantes de récession tau (médiane & IQR) aux 4 stations journalières vs 6.0 jours observés.
   - Q90, Q95, min et nombre de jours à débit nul (assecs) à Sidi Jabeur, Adamna et les autres stations.
   - Bilan annuel Vsim/Vin par bassin et par an (2016 à 2020 et 5 ans).
   - Bilan de masse 2018 (fermeture < 0.2 %).
   - Tableau complet avant/après des métriques (KGE, r, alpha, beta, PBIAS) aux 12 stations.
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy import stats

def main():
    base_dir = "experiments/NorthMor/routing"
    clean_dir = "data/streamflow_clean"
    ldt_path = os.path.join(base_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    pairing_csv = os.path.join(base_dir, "stations/hymap_stations_pairing.csv")
    t5bis_metrics_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_metrics_12stations.csv")
    t5bis_rec_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_recession_tau.csv")
    t5bis_lowflow_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_lowflow_stats.csv")
    t6_decomp_csv = os.path.join(base_dir, "output/OPL_2016_2020/t6_three_volumes_decomposition.csv")
    
    corr_out_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee")
    os.makedirs(corr_out_dir, exist_ok=True)

    # =========================================================================
    # 1. DISTRIBUTION EFFECTIVE DE tbsflw APRES PLANCHER
    # =========================================================================
    print("=" * 95)
    print("1. DISTRIBUTION EFFECTIVE DE tbsflw APRES APPLICATION DU PLANCHER LIS")
    print("=" * 95)
    ds_corr = nc.Dataset(ldt_path)
    tbs_input = ds_corr.variables["HYMAP_baseflow_time_delay"][:] # en jours
    cntime = ds_corr.variables["HYMAP_runoff_time_delay"][:] # en secondes
    area = ds_corr.variables["HYMAP_grid_area"][:]
    mask = ~np.ma.getmaskarray(area) & (area > 0) & (cntime > 0)

    tbs_in_v = tbs_input[mask]
    cntime_v = cntime[mask]
    floor_v = cntime_v / 86400.0 # plancher en jours
    tbs_eff_v = np.where(tbs_in_v < floor_v, floor_v, tbs_in_v)

    n_cells = len(tbs_in_v)
    n_bitten = int(np.sum(tbs_in_v < floor_v))
    pct_bitten = n_bitten / n_cells * 100.0

    print(f"Nombre de mailles terrestres actives : {n_cells}")
    print(f"Mailles où le plancher s'applique (tbsflw < cntime/86400) : {n_bitten} / {n_cells} ({pct_bitten:.2f} %)")
    print()
    def p_stats(label, a):
        return f"{label:35s} | Min={np.min(a):6.3f}j | Q10={np.percentile(a,10):6.3f}j | Q25={np.percentile(a,25):6.3f}j | Med={np.median(a):6.3f}j | Moy={np.mean(a):6.3f}j | Q75={np.percentile(a,75):6.3f}j | Q90={np.percentile(a,90):6.3f}j | Max={np.max(a):7.3f}j"

    print(p_stats("1. tbsflw input (corrigé / 86400)", tbs_in_v))
    print(p_stats("2. plancher cntime/86400 (Getirana)", floor_v))
    print(p_stats("3. tbsflw EFFECTIF utilisé par LIS", tbs_eff_v))
    print("=" * 95)

    # =========================================================================
    # 2. CHARGEMENT DES DONNEES (OBSERVATIONS & SIMULATIONS AVANT/APRES)
    # =========================================================================
    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_obs_monthly["year_month"] = df_obs_monthly["annee"].astype(str) + "-" + df_obs_monthly["mois"].astype(str).str.zfill(2)

    df_p = pd.read_csv(pairing_csv)

    # Simulation avant correction
    df_q_avant_d = pd.read_csv(os.path.join(base_dir, "output/OPL_2016_2020/t6_sim_daily_12stations.csv"))
    df_q_avant_d["year_month"] = pd.to_datetime(df_q_avant_d["date"]).dt.to_period("M").astype(str)
    df_q_avant_m = df_q_avant_d.groupby("year_month").mean(numeric_only=True).reset_index()

    # Simulation après correction (lire ou extraire si non présent)
    sim_corr_cache = os.path.join(corr_out_dir, "t7_sim_daily_12stations_corrigee.csv")
    if os.path.exists(sim_corr_cache):
        df_q_corr_d = pd.read_csv(sim_corr_cache)
    else:
        print("Extraction des débits simulés corrigés depuis LIS_HIST...")
        hist_files = sorted(glob.glob(os.path.join(corr_out_dir, "ROUTING/20*/**/LIS_HIST_*.d01.nc"), recursive=True))
        records = []
        for idx, fpath in enumerate(hist_files):
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                sim_date_str = sim_dt.strftime("%Y-%m-%d")

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3: flow = flow[0]

                row_dict = {"date": sim_date_str}
                for _, row in df_p.iterrows():
                    sid = row["station_id"]
                    r, c = int(row["row_hymap"]), int(row["col_hymap"])
                    row_dict[sid] = float(flow[r, c])
                records.append(row_dict)
        df_q_corr_d = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        df_q_corr_d.to_csv(sim_corr_cache, index=False)

    df_q_corr_d["year_month"] = pd.to_datetime(df_q_corr_d["date"]).dt.to_period("M").astype(str)
    df_q_corr_m = df_q_corr_d.groupby("year_month").mean(numeric_only=True).reset_index()

    # =========================================================================
    # 3. CONSTANTES DE RECESSION TAU (JOURNALIER)
    # =========================================================================
    print("\n2. CONSTANTES DE RECESSION TAU (SEGMENTS >= 5 JOURS DE DECROISSANCE)")
    print("-" * 95)
    def extract_recessions(q_series):
        tau_list = []
        i = 0
        while i < len(q_series) - 4:
            j = i
            while j < len(q_series) - 1 and q_series[j+1] < q_series[j] and q_series[j+1] > 0.0001:
                j += 1
            length = j - i + 1
            if length >= 5:
                seg = q_series[i:j+1]
                t = np.arange(length)
                slope, intercept, r_val, p_val, std_err = stats.linregress(t, np.log(seg))
                if slope < -1e-6:
                    tau = -1.0 / slope
                    tau_list.append(tau)
                i = j + 1
            else:
                i += 1
        return tau_list

    rec_records = []
    for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]:
        sub_obs = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
        m_av = pd.merge(sub_obs, df_q_avant_d[["date", sid]], on="date", how="inner")
        m_ap = pd.merge(sub_obs, df_q_corr_d[["date", sid]], on="date", how="inner")

        q_obs = m_av["q_m3s"].to_numpy()
        q_av = m_av[sid].to_numpy()
        q_ap = m_ap[sid].to_numpy()

        t_obs = extract_recessions(q_obs)
        t_av = extract_recessions(q_av)
        t_ap = extract_recessions(q_ap)

        nom = df_p[df_p["station_id"] == sid]["nom"].iloc[0]
        
        med_o = np.median(t_obs) if len(t_obs) > 0 else np.nan
        iqr_o = (np.percentile(t_obs, 75) - np.percentile(t_obs, 25)) if len(t_obs) > 0 else np.nan

        med_av = np.median(t_av) if len(t_av) > 0 else np.nan
        iqr_av = (np.percentile(t_av, 75) - np.percentile(t_av, 25)) if len(t_av) > 0 else np.nan

        med_ap = np.median(t_ap) if len(t_ap) > 0 else np.nan
        iqr_ap = (np.percentile(t_ap, 75) - np.percentile(t_ap, 25)) if len(t_ap) > 0 else np.nan

        rec_records.append({
            "station_id": sid,
            "nom": nom,
            "med_tau_obs": med_o, "iqr_tau_obs": iqr_o,
            "med_tau_avant": med_av, "iqr_tau_avant": iqr_av,
            "med_tau_apres": med_ap, "iqr_tau_apres": iqr_ap,
            "ratio_avant": med_av / med_o if med_o > 0 else np.nan,
            "ratio_apres": med_ap / med_o if med_o > 0 else np.nan
        })

    df_rec = pd.DataFrame(rec_records)
    print(f"{'Station':16s} | {'Tau Obs (j)':14s} | {'Tau Avant (j)':16s} | {'Ratio Av':9s} | {'Tau Après (j)':16s} | {'Ratio Ap':9s}")
    print("-" * 95)
    for _, r in df_rec.iterrows():
        print(f"{r['nom']:16s} | {r['med_tau_obs']:5.2f} (IQR {r['iqr_tau_obs']:4.2f}) | {r['med_tau_avant']:5.2f} (IQR {r['iqr_tau_avant']:4.2f}) | {r['ratio_avant']:8.2f}x | {r['med_tau_apres']:5.2f} (IQR {r['iqr_tau_apres']:4.2f}) | {r['ratio_apres']:8.2f}x")
    df_rec.to_csv(os.path.join(corr_out_dir, "t7bis_recession_comparison.csv"), index=False)

    # =========================================================================
    # 4. STATISTIQUES D'ETIAGE (Q90, Q95, MIN, ASSECS)
    # =========================================================================
    print("\n3. STATISTIQUES D'ETIAGE : Q90, Q95, MINIMUM ET ASSECS")
    print("-" * 95)
    lowflow_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        pas = p["type_pas"]

        if pas == "journalier":
            sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
            m_av = pd.merge(sub_o, df_q_avant_d[["date", sid]], on="date", how="inner")
            m_ap = pd.merge(sub_o, df_q_corr_d[["date", sid]], on="date", how="inner")
            o = m_av["q_m3s"].to_numpy()
            s_av = m_av[sid].to_numpy()
            s_ap = m_ap[sid].to_numpy()
            unit = "j"
        else:
            sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            m_av = pd.merge(sub_o, df_q_avant_m[["year_month", sid]], on="year_month", how="inner")
            m_ap = pd.merge(sub_o, df_q_corr_m[["year_month", sid]], on="year_month", how="inner")
            o = m_av["q_m3s"].to_numpy()
            s_av = m_av[sid].to_numpy()
            s_ap = m_ap[sid].to_numpy()
            unit = "m"

        q90_o, q95_o = np.percentile(o, 10), np.percentile(o, 5)
        q90_av, q95_av = np.percentile(s_av, 10), np.percentile(s_av, 5)
        q90_ap, q95_ap = np.percentile(s_ap, 10), np.percentile(s_ap, 5)

        min_o, min_av, min_ap = np.min(o), np.min(s_av), np.min(s_ap)
        zero_o = int(np.sum(o <= 0.001))
        zero_av = int(np.sum(s_av <= 0.001))
        zero_ap = int(np.sum(s_ap <= 0.001))

        lowflow_records.append({
            "station_id": sid, "nom": nom, "bassin": p["bassin"], "pas": pas, "n": len(o),
            "q90_obs": q90_o, "q90_avant": q90_av, "q90_apres": q90_ap,
            "ratio_q90_av": q90_av / q90_o if q90_o > 0 else np.nan,
            "ratio_q90_ap": q90_ap / q90_o if q90_o > 0 else np.nan,
            "q95_obs": q95_o, "q95_avant": q95_av, "q95_apres": q95_ap,
            "min_obs": min_o, "min_avant": min_av, "min_apres": min_ap,
            "assecs_obs": zero_o, "assecs_avant": zero_av, "assecs_apres": zero_ap
        })

    df_lowflow = pd.DataFrame(lowflow_records)
    print(f"{'Station':16s} | {'Q90 Obs':8s} | {'Q90 Av':8s} | {'Q90 Ap':8s} | {'Ratio Av':9s} | {'Ratio Ap':9s} | {'Min Obs':8s} | {'Min Av':8s} | {'Min Ap':8s} | {'Assecs O/Av/Ap'}")
    print("-" * 115)
    for _, r in df_lowflow.iterrows():
        rat_av_str = f"{r['ratio_q90_av']:8.2f}x" if not np.isnan(r['ratio_q90_av']) else "   N/A   "
        rat_ap_str = f"{r['ratio_q90_ap']:8.2f}x" if not np.isnan(r['ratio_q90_ap']) else "   N/A   "
        print(f"{r['nom']:16s} | {r['q90_obs']:8.3f} | {r['q90_avant']:8.3f} | {r['q90_apres']:8.3f} | {rat_av_str} | {rat_ap_str} | {r['min_obs']:8.3f} | {r['min_avant']:8.3f} | {r['min_apres']:8.3f} | {r['assecs_obs']:3d} / {r['assecs_avant']:3d} / {r['assecs_apres']:3d}")
    df_lowflow.to_csv(os.path.join(corr_out_dir, "t7bis_lowflow_comparison.csv"), index=False)

    # =========================================================================
    # 5. METRIQUES HYDROLOGIQUES COMPLETES AVANT / APRES (12 STATIONS)
    # =========================================================================
    print("\n4. METRIQUES HYDROLOGIQUES COMPLETES AVANT / APRES (12 STATIONS)")
    print("-" * 95)
    df_m_avant = pd.read_csv(t5bis_metrics_csv)
    metrics_records = []

    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        pas = p["type_pas"]

        sub_av = df_m_avant[(df_m_avant["station_id"] == sid) & (df_m_avant["pas"] == pas)]
        if len(sub_av) > 1 and "exclusion_flags" in sub_av.columns:
            sub_av = sub_av[sub_av["exclusion_flags"] != "exclus (sans suspects)"]
        m_av = sub_av.iloc[0]

        if pas == "journalier":
            sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
            m_ap = pd.merge(sub_o, df_q_corr_d[["date", sid]], on="date", how="inner")
            o = m_ap["q_m3s"].to_numpy()
            s_ap = m_ap[sid].to_numpy()
        else:
            sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            m_ap = pd.merge(sub_o, df_q_corr_m[["year_month", sid]], on="year_month", how="inner")
            o = m_ap["q_m3s"].to_numpy()
            s_ap = m_ap[sid].to_numpy()

        r_ap, _ = stats.pearsonr(o, s_ap)
        alpha_ap = np.std(s_ap, ddof=1) / np.std(o, ddof=1)
        beta_ap = np.mean(s_ap) / np.mean(o)
        pbias_ap = float(np.sum(s_ap - o) / np.sum(o) * 100.0)
        kge_ap = 1.0 - np.sqrt((r_ap - 1.0)**2 + (alpha_ap - 1.0)**2 + (beta_ap - 1.0)**2)

        metrics_records.append({
            "station_id": sid, "nom": nom, "bassin": bassin, "pas": pas, "n_obs": len(o),
            "KGE_av": m_av["kge"], "KGE_ap": kge_ap, "Delta_KGE": kge_ap - m_av["kge"],
            "r_av": m_av["r"], "r_ap": r_ap,
            "alpha_av": m_av["alpha"], "alpha_ap": alpha_ap,
            "beta_av": m_av["beta"], "beta_ap": beta_ap,
            "PBIAS_av": m_av["pbias"], "PBIAS_ap": pbias_ap
        })

    df_metrics_comp = pd.DataFrame(metrics_records)
    print(f"{'Station':16s} | {'KGE Av':8s} | {'KGE Ap':8s} | {'Δ KGE':7s} | {'r Av':6s} | {'r Ap':6s} | {'alpha Av':9s} | {'alpha Ap':9s} | {'beta Av':8s} | {'beta Ap':8s} | {'PBIAS Av':9s} | {'PBIAS Ap':9s}")
    print("-" * 125)
    for _, r in df_metrics_comp.iterrows():
        print(f"{r['nom']:16s} | {r['KGE_av']:8.3f} | {r['KGE_ap']:8.3f} | {r['Delta_KGE']:+7.3f} | {r['r_av']:6.3f} | {r['r_ap']:6.3f} | {r['alpha_av']:9.3f} | {r['alpha_ap']:9.3f} | {r['beta_av']:8.3f} | {r['beta_ap']:8.3f} | {r['PBIAS_av']:8.1f}% | {r['PBIAS_ap']:8.1f}%")
    df_metrics_comp.to_csv(os.path.join(corr_out_dir, "t7bis_metrics_before_after.csv"), index=False)

    # =========================================================================
    # 6. RATIOS Vsim/Vin PAR BASSIN ET PAR ANNEE
    # =========================================================================
    print("\n5. RATIOS Vsim/Vin PAR BASSIN ET PAR ANNEE (2016-2020)")
    print("-" * 95)
    # Vin calculé par bassin et par an
    runoff_dir = os.path.join(base_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL")
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    R, C = flow_x.shape
    ds_ldt.close()

    down_r = np.full((R, C), -1, dtype=int)
    down_c = np.full((R, C), -1, dtype=int)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
                if 1 <= vx <= C and 1 <= vy <= R:
                    down_c[r, c], down_r[r, c] = vx - 1, vy - 1

    parents = {}
    for r in range(R):
        for c in range(C):
            pr, pc = down_r[r, c], down_c[r, c]
            if pr >= 0 and pc >= 0:
                if (pr, pc) not in parents: parents[(pr, pc)] = []
                parents[(pr, pc)].append((r, c))

    def get_catchment(orow, ocol):
        vis = set([(orow, ocol)])
        q = [(orow, ocol)]
        while q:
            curr = q.pop(0)
            if curr in parents:
                for p in parents[curr]:
                    if p not in vis:
                        vis.add(p)
                        q.append(p)
        return vis

    station_masks = {}
    for _, row in df_p.iterrows():
        sid = row["station_id"]
        cat = get_catchment(int(row["row_hymap"]), int(row["col_hymap"]))
        m = np.zeros((R, C), dtype=bool)
        for cr, cc in cat: m[cr, cc] = True
        station_masks[sid] = m

    # Calcul Vin et Vsim par an
    df_q_corr_d["annee"] = pd.to_datetime(df_q_corr_d["date"]).dt.year
    annees = [2016, 2017, 2018, 2019, 2020]

    vin_by_year = {y: {sid: 0.0 for sid in station_masks} for y in annees}
    rfiles = sorted(glob.glob(os.path.join(runoff_dir, "*/*.nc")))
    for rf in rfiles:
        dt_str = os.path.basename(rf).replace("LIS_HIST_", "").replace("0000.d01.nc", "")
        file_dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
        sim_dt = file_dt - datetime.timedelta(days=1)
        y = sim_dt.year
        if y not in annees: continue
        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds["Qs_tavg"][:])
            qsb = np.nan_to_num(ds["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]
            vol_m3 = (np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0
            for sid, m in station_masks.items():
                vin_by_year[y][sid] += float(np.sum(vol_m3[m])) / 1e6 # hm3

    vsim_vin_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        rec = {"station_id": sid, "nom": nom, "bassin": bassin}
        tot_vin = 0.0
        tot_vsim = 0.0
        for y in annees:
            vin_y = vin_by_year[y][sid]
            vsim_y = float(df_q_corr_d[df_q_corr_d["annee"] == y][sid].sum() * 86400.0 / 1e6)
            rat_y = vsim_y / vin_y if vin_y > 0 else 0.0
            rec[f"Vsim_Vin_{y}"] = rat_y
            tot_vin += vin_y
            tot_vsim += vsim_y
        rec["Vsim_Vin_5ans"] = tot_vsim / tot_vin if tot_vin > 0 else 0.0
        rec["Vin_5ans_hm3"] = tot_vin
        rec["Vsim_5ans_hm3"] = tot_vsim
        vsim_vin_records.append(rec)

    df_vv = pd.DataFrame(vsim_vin_records)
    print(f"{'Station':16s} | {'2016':7s} | {'2017':7s} | {'2018':7s} | {'2019':7s} | {'2020':7s} | {'5 ANS TOTAL':12s} | {'Vin (hm3)':10s} | {'Vsim (hm3)':10s}")
    print("-" * 105)
    for _, r in df_vv.iterrows():
        print(f"{r['nom']:16s} | {r['Vsim_Vin_2016']*100:6.1f}% | {r['Vsim_Vin_2017']*100:6.1f}% | {r['Vsim_Vin_2018']*100:6.1f}% | {r['Vsim_Vin_2019']*100:6.1f}% | {r['Vsim_Vin_2020']*100:6.1f}% | {r['Vsim_Vin_5ans']*100:10.2f} % | {r['Vin_5ans_hm3']:10.1f} | {r['Vsim_5ans_hm3']:10.1f}")
    df_vv.to_csv(os.path.join(corr_out_dir, "t7bis_vsim_vin_annual.csv"), index=False)

    # =========================================================================
    # 7. FERMETURE DU BILAN DE MASSE 2018
    # =========================================================================
    print("\n6. FERMETURE DU BILAN DE MASSE ANNUEL 2018")
    print("-" * 95)
    rst_201712 = os.path.join(corr_out_dir, "ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc")
    rst_201812 = os.path.join(corr_out_dir, "ROUTING/201812/LIS_RST_HYMAP2_router_201812312345.d01.nc")

    def rst_tot(rf):
        with nc.Dataset(rf) as ds:
            b = np.sum(np.maximum(ds['BSFSTO'][:], 0.0))
            r = np.sum(np.maximum(ds['RNFSTO'][:], 0.0))
            rv = np.sum(np.maximum(ds['RIVSTO'][:], 0.0))
            f = np.sum(np.maximum(ds['FLDSTO'][:], 0.0))
            return (b + r + rv + f) / 1e6

    s_start = rst_tot(rst_201712)
    s_end = rst_tot(rst_201812)
    delta_s = s_end - s_start

    # Vin total domaine 2018
    rfiles_2018 = sorted(glob.glob(os.path.join(runoff_dir, "2018*/*.nc")))
    vin_2018 = 0.0
    for rf in rfiles_2018:
        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds["Qs_tavg"][:])
            qsb = np.nan_to_num(ds["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]
            vin_2018 += float(np.sum((np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0 / 1e6))

    # Vout exutoires mer 2018
    hfiles_2018 = sorted(glob.glob(os.path.join(corr_out_dir, "ROUTING/2018*/LIS_HIST_*.d01.nc")))
    outlet_mask = np.zeros((R, C), dtype=bool)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
                if vx < 1 or vx > C or vy < 1 or vy > R or (vx-1 == c and vy-1 == r):
                    outlet_mask[r, c] = True

    vout_2018 = 0.0
    for hf in hfiles_2018:
        with nc.Dataset(hf) as ds:
            fl = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if fl.ndim == 3: fl = fl[0]
            vout_2018 += float(np.sum(fl[outlet_mask]) * 86400.0 / 1e6)

    bilan_sum = vout_2018 + delta_s
    ecart = vin_2018 - bilan_sum
    err_pct = abs(ecart) / vin_2018 * 100.0

    print(f"Vin total domaine 2018     : {vin_2018:10.2f} hm3")
    print(f"Vout exutoires mer 2018    : {vout_2018:10.2f} hm3")
    print(f"Delta S domaine (2018)     : {delta_s:+10.2f} hm3")
    print(f"Vout + Delta S             : {bilan_sum:10.2f} hm3")
    print(f"Ecart résiduel             : {ecart:+10.3f} hm3")
    print(f"Erreur de fermeture        : {err_pct:.4f} %")
    print(f"Critère fermeture < 0.2 %  : {'VALIDE' if err_pct < 0.2 else 'ECHEC'}")
    print("=" * 95)

if __name__ == "__main__":
    main()
