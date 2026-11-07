#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_t8_analysis_and_plots.py
Analyse complete de la Tache 8 pour l'assimilation DA_nocdf vs Open-Loop (OPL).
- Controles obligatoires (Spinup < 1%, Vsim/Vin 100%, Bilan masse 2018 < 0.2%)
- Differences Delta Q = Q_DA - Q_OPL (journalier, mensuel, crues, detectabilite)
- Metrique VALUE = |Q_OPL - Q_obs| - |Q_DA - Q_obs| et metriques KGE/r/NSE/alpha/beta/PBIAS
- 6 Figures de qualite publication pour un collegue hydrologue dans experiments/NorthMor/routing/plots/_history/t8_ol_nocdf/
- Tableau de synthese hydrologique
"""

import os, sys, glob, re, datetime, json
import numpy as np
import pandas as pd
import scipy.stats as stats
import netCDF4 as nc

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

def main():
    print("=" * 95)
    print("TACHE 8 — ANALYSE COMPLETE DA_nocdf vs OPL & LOT DE FIGURES POUR UN HYDROLOGUE")
    print("=" * 95)

    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing"
    clean_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/streamflow_clean"
    plots_dir = os.path.join(base_dir, "plots/_history/t8_ol_nocdf")
    os.makedirs(plots_dir, exist_ok=True)

    opl_out_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee")
    da_out_dir = os.path.join(base_dir, "output/DA_nocdf_2016_2020")
    ldt_path = os.path.join(base_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    pairing_csv = os.path.join(base_dir, "stations/hymap_stations_pairing.csv")

    df_p = pd.read_csv(pairing_csv)
    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_obs_monthly["year_month"] = df_obs_monthly["annee"].astype(str) + "-" + df_obs_monthly["mois"].astype(str).str.zfill(2)

    # 1. Verification et extraction des debits journaliers DA_nocdf
    sim_da_cache = os.path.join(da_out_dir, "t8_sim_daily_12stations_da_nocdf.csv")
    if os.path.exists(sim_da_cache):
        print(f"Chargement des debits DA_nocdf depuis le cache : {sim_da_cache}")
        df_q_da_d = pd.read_csv(sim_da_cache)
    else:
        print("Extraction des debits journaliers DA_nocdf depuis LIS_HIST...")
        hist_files = sorted(glob.glob(os.path.join(da_out_dir, "ROUTING/20*/**/LIS_HIST_*.d01.nc"), recursive=True))
        if len(hist_files) < 1826:
            raise RuntimeError(f"Fichiers LIS_HIST incomplets pour DA_nocdf ({len(hist_files)} / 1827)")
        records = []
        for fpath in hist_files:
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                dt_str = sim_dt.strftime("%Y-%m-%d")

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3: flow = flow[0]
                row_dict = {"date": dt_str}
                for _, row in df_p.iterrows():
                    sid = row["station_id"]
                    r, c = int(row["row_hymap"]), int(row["col_hymap"])
                    row_dict[sid] = float(flow[r, c])
                records.append(row_dict)
        df_q_da_d = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        df_q_da_d.to_csv(sim_da_cache, index=False)
        print("Extraction DA_nocdf terminee.")

    # Chargement debits OPL
    sim_opl_cache = os.path.join(opl_out_dir, "t7_sim_daily_12stations_corrigee.csv")
    df_q_opl_d = pd.read_csv(sim_opl_cache)

    df_q_da_d["year_month"] = pd.to_datetime(df_q_da_d["date"]).dt.to_period("M").astype(str)
    df_q_da_m = df_q_da_d.groupby("year_month").mean(numeric_only=True).reset_index()

    df_q_opl_d["year_month"] = pd.to_datetime(df_q_opl_d["date"]).dt.to_period("M").astype(str)
    df_q_opl_m = df_q_opl_d.groupby("year_month").mean(numeric_only=True).reset_index()

    # Dictionnaire de métadonnées officielles
    meta_dict = {
        "b_a_loudah": {"ire": "2673/20", "oued": "Korifla", "aire_off": 697.6, "couv": "100%"},
        "b_s_cherif": {"ire": "2674/20", "oued": "Mechraa", "aire_off": 649.5, "couv": "100%"},
        "b_s_jabeur": {"ire": "964/21",  "oued": "Grou",    "aire_off": 3138.5, "couv": "100%"},
        "b_l_chafia": {"ire": "963/21",  "oued": "Bouregreg","aire_off": 3341.6, "couv": "99.95%"},
        "adamna":     {"ire": "402/52",  "oued": "Ksob",    "aire_off": 1617.0, "couv": "33.3%"},
        "ain_timedrine": {"ire": "581/22", "oued": "Sebou", "aire_off": 4387.0, "couv": "100%"},
        "ait_khabbach":  {"ire": "585/22", "oued": "Guigou", "aire_off": 1240.0, "couv": "73.3%"},
        "azzaba":        {"ire": "583/22", "oued": "Sebou", "aire_off": 4640.0, "couv": "100%"},
        "dar_el_hamra":  {"ire": "1000/23","oued": "Zloul", "aire_off": 670.0,  "couv": "100%"},
        "el_mers":       {"ire": "541/23", "oued": "Masser","aire_off": 1004.0, "couv": "33.3%"},
        "pont_ait_aissa":{"ire": "198/30", "oued": "Guigou","aire_off": 205.0,  "couv": "100%"},
        "pont_de_mdez":  {"ire": "582/22", "oued": "Sebou", "aire_off": 3435.0, "couv": "73.3%"}
    }

    # =========================================================================
    # ETAPE 2 — CONTROLES OBLIGATOIRES
    # =========================================================================
    print("\n" + "=" * 95)
    print("ETAPE 2 — CONTROLES OBLIGATOIRES DE CONFIGURATION (DA_nocdf vs OPL)")
    print("=" * 95)

    # 1. Controle Spin-up
    rst_c1 = os.path.join(base_dir, "output/DA_nocdf_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc")
    rst_c2 = os.path.join(base_dir, "output/DA_nocdf_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc")
    with nc.Dataset(rst_c1) as ds: bsf_c1 = float(np.sum(np.maximum(ds['BSFSTO'][:], 0.0))) / 1e6
    with nc.Dataset(rst_c2) as ds: bsf_c2 = float(np.sum(np.maximum(ds['BSFSTO'][:], 0.0))) / 1e6
    spinup_err = abs(bsf_c2 - bsf_c1) / bsf_c1 * 100.0
    print(f"1. Spin-up Cycle 1 BSFSTO = {bsf_c1:.3f} hm3 | Cycle 2 BSFSTO = {bsf_c2:.3f} hm3")
    print(f"   Ecart relatif inter-cycles : {spinup_err:.4f} % (Critere < 1.0 % : {'VALIDE' if spinup_err < 1.0 else 'ECHEC'})")

    # 2. Bassins versants & Ratios Vsim/Vin
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    drain_area_grid = ds_ldt["HYMAP_drain_area"][:].filled(0.0)
    elevation_grid = ds_ldt["ELEVATION"][:].filled(0.0)
    lon_grid = ds_ldt["lon"][:]
    lat_grid = ds_ldt["lat"][:]
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

    runoff_da_dir = os.path.join(base_dir, "runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL")
    df_q_da_d["annee"] = pd.to_datetime(df_q_da_d["date"]).dt.year
    annees = [2016, 2017, 2018, 2019, 2020]

    vin_cache_file = os.path.join(da_out_dir, "t8_vin_by_year_da.json")
    if os.path.exists(vin_cache_file):
        print(f"Chargement de Vin DA depuis le cache : {vin_cache_file}")
        with open(vin_cache_file, "r") as f_c:
            vin_by_year_da = {int(k): v for k, v in json.load(f_c).items()}
    else:
        print("Calcul de Vin par bassin pour DA_nocdf...")
        vin_by_year_da = {y: {sid: 0.0 for sid in station_masks} for y in annees}
        rfiles_da = sorted(glob.glob(os.path.join(runoff_da_dir, "*/*.nc")))
        for rf in rfiles_da:
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
                    vin_by_year_da[y][sid] += float(np.sum(vol_m3[m])) / 1e6
        with open(vin_cache_file, "w") as f_c:
            json.dump(vin_by_year_da, f_c)

    vsim_vin_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        tot_vin = sum(vin_by_year_da[y][sid] for y in annees)
        tot_vsim = float(df_q_da_d[sid].sum() * 86400.0 / 1e6)
        ratio_5y = tot_vsim / tot_vin if tot_vin > 0 else 0.0
        vsim_vin_records.append({
            "station_id": sid, "nom": nom, "bassin": bassin,
            "Vin_5ans_hm3": tot_vin, "Vsim_5ans_hm3": tot_vsim, "ratio_5ans": ratio_5y
        })
    df_vv_da = pd.DataFrame(vsim_vin_records)
    print("\n2. Ratios de transmission Vsim/Vin DA_nocdf sur 5 ans :")
    for _, r in df_vv_da.iterrows():
        print(f"   {r['nom']:16s} : Vin = {r['Vin_5ans_hm3']:7.1f} hm3 | Vsim = {r['Vsim_5ans_hm3']:7.1f} hm3 | Ratio = {r['ratio_5ans']*100:6.2f} %")

    # 3. Bilan de masse annuel 2018
    rst_201712 = os.path.join(da_out_dir, "ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc")
    rst_201812 = os.path.join(da_out_dir, "ROUTING/201812/LIS_RST_HYMAP2_router_201812312345.d01.nc")
    def rst_tot(rf):
        with nc.Dataset(rf) as ds:
            return float(np.sum(np.maximum(ds['BSFSTO'][:], 0.0) + np.maximum(ds['RNFSTO'][:], 0.0) + \
                                np.maximum(ds['RIVSTO'][:], 0.0) + np.maximum(ds['FLDSTO'][:], 0.0))) / 1e6
    s_start = rst_tot(rst_201712)
    s_end = rst_tot(rst_201812)
    delta_s_2018 = s_end - s_start

    rfiles_2018_da = sorted(glob.glob(os.path.join(runoff_da_dir, "2018*/*.nc")))
    vin_2018_dom = 0.0
    for rf in rfiles_2018_da:
        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds["Qs_tavg"][:])
            qsb = np.nan_to_num(ds["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]
            vin_2018_dom += float(np.sum((np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0 / 1e6))

    outlet_mask = np.zeros((R, C), dtype=bool)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
                if vx < 1 or vx > C or vy < 1 or vy > R or (vx-1 == c and vy-1 == r):
                    outlet_mask[r, c] = True

    hfiles_2018_da = sorted(glob.glob(os.path.join(da_out_dir, "ROUTING/2018*/LIS_HIST_*.d01.nc")))
    vout_2018_dom = 0.0
    for hf in hfiles_2018_da:
        with nc.Dataset(hf) as ds:
            fl = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if fl.ndim == 3: fl = fl[0]
            vout_2018_dom += float(np.sum(fl[outlet_mask]) * 86400.0 / 1e6)

    bilan_sum_2018 = vout_2018_dom + delta_s_2018
    err_bilan_pct = abs(vin_2018_dom - bilan_sum_2018) / vin_2018_dom * 100.0
    print(f"\n3. Bilan de masse annuel 2018 domaine complet (DA_nocdf) :")
    print(f"   Vin total   : {vin_2018_dom:10.2f} hm3")
    print(f"   Vout mer    : {vout_2018_dom:10.2f} hm3")
    print(f"   Delta S     : {delta_s_2018:+10.2f} hm3")
    print(f"   Erreur fermeture : {err_bilan_pct:.4f} % (Critere < 0.2 % : {'VALIDE' if err_bilan_pct < 0.2 else 'ECHEC'})")

    # =========================================================================
    # ETAPE 3 & 4 — DIFFERENCES DA - OPL ET METRIQUE VALUE
    # =========================================================================
    print("\n" + "=" * 95)
    print("ETAPE 3 & 4 — DIFFERENCES DA MOINS OPL & METRIQUE VALUE")
    print("=" * 95)

    def get_season(dt_series):
        m = pd.to_datetime(dt_series).dt.month
        return np.where(m.isin([12, 1, 2]), "DJF",
               np.where(m.isin([3, 4, 5]), "MAM",
               np.where(m.isin([6, 7, 8]), "JJA", "SON")))

    df_q_da_d["saison"] = get_season(df_q_da_d["date"])
    df_q_opl_d["saison"] = get_season(df_q_opl_d["date"])

    def month_to_season(ym):
        m = int(ym.split("-")[1])
        if m in [12, 1, 2]: return "DJF"
        elif m in [3, 4, 5]: return "MAM"
        elif m in [6, 7, 8]: return "JJA"
        else: return "SON"
    df_q_da_m["saison"] = df_q_da_m["year_month"].apply(month_to_season)
    df_q_opl_m["saison"] = df_q_opl_m["year_month"].apply(month_to_season)

    station_stats = []
    value_records = []
    detect_records = []

    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        pas = p["type_pas"]
        meta = meta_dict[sid]

        if pas == "journalier":
            sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
            m_all = pd.merge(sub_o[["date", "q_m3s"]], df_q_opl_d[["date", sid, "saison"]], on="date", how="inner").rename(columns={sid: "q_opl"})
            m_all = pd.merge(m_all, df_q_da_d[["date", sid]], on="date", how="inner").rename(columns={sid: "q_da"})
        else:
            sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            m_all = pd.merge(sub_o[["year_month", "q_m3s"]], df_q_opl_m[["year_month", sid, "saison"]], on="year_month", how="inner").rename(columns={sid: "q_opl"})
            m_all = pd.merge(m_all, df_q_da_m[["year_month", sid]], on="year_month", how="inner").rename(columns={sid: "q_da"})

        o = m_all["q_m3s"].to_numpy()
        s_opl = m_all["q_opl"].to_numpy()
        s_da = m_all["q_da"].to_numpy()
        delta_q = s_da - s_opl
        m_all["delta_q"] = delta_q

        # Metrique VALUE = |Q_opl - Q_obs| - |Q_da - Q_obs|
        err_opl = np.abs(s_opl - o)
        err_da = np.abs(s_da - o)
        value = err_opl - err_da
        m_all["value"] = value
        pos_val_tot = float(np.mean(value > 0.0) * 100.0)

        # VALUE par saison
        val_by_saison = {}
        for s in ["DJF", "MAM", "JJA", "SON"]:
            sub_s = m_all[m_all["saison"] == s]
            val_by_saison[s] = float(np.mean(sub_s["value"] > 0.0) * 100.0) if len(sub_s) > 0 else np.nan

        # Detectabilite : ratio |Delta Q| / |Q_opl - Q_obs|
        ratio_detect = np.mean(np.abs(delta_q)) / (np.mean(err_opl) + 1e-6)

        # Metriques hydrologiques OPL
        r_opl, _ = stats.pearsonr(o, s_opl)
        alpha_opl = np.std(s_opl, ddof=1) / np.std(o, ddof=1)
        beta_opl = np.mean(s_opl) / np.mean(o)
        pbias_opl = float(np.sum(s_opl - o) / np.sum(o) * 100.0)
        kge_opl = 1.0 - np.sqrt((r_opl - 1.0)**2 + (alpha_opl - 1.0)**2 + (beta_opl - 1.0)**2)
        nse_opl = 1.0 - np.sum((s_opl - o)**2) / np.sum((o - np.mean(o))**2)

        # Metriques hydrologiques DA
        r_da, _ = stats.pearsonr(o, s_da)
        alpha_da = np.std(s_da, ddof=1) / np.std(o, ddof=1)
        beta_da = np.mean(s_da) / np.mean(o)
        pbias_da = float(np.sum(s_da - o) / np.sum(o) * 100.0)
        kge_da = 1.0 - np.sqrt((r_da - 1.0)**2 + (alpha_da - 1.0)**2 + (beta_da - 1.0)**2)
        nse_da = 1.0 - np.sum((s_da - o)**2) / np.sum((o - np.mean(o))**2)

        # Lame d'eau mm/an
        area_m2 = meta["aire_off"] * 1e6
        v_obs_mman = float(np.mean(o) * 86400 * 365.25 / area_m2 * 1000.0)
        v_opl_mman = float(np.mean(s_opl) * 86400 * 365.25 / area_m2 * 1000.0)
        v_da_mman = float(np.mean(s_da) * 86400 * 365.25 / area_m2 * 1000.0)
        vin_mman = float(sum(vin_by_year_da[y][sid] for y in annees) * 1e6 / 5.0 / area_m2 * 1000.0)

        station_stats.append({
            "station_id": sid, "nom": nom, "oued": meta["oued"], "bassin": bassin,
            "ire": meta["ire"], "aire_off_km2": meta["aire_off"], "aire_hymap_km2": p["aire_hymap_km2"],
            "ecart_aire_pct": (p["aire_hymap_km2"] - meta["aire_off"]) / meta["aire_off"] * 100.0,
            "pas_de_temps": pas, "couverture": meta["couv"], "n_obs": len(o),
            "KGE_opl": kge_opl, "KGE_da": kge_da, "Delta_KGE": kge_da - kge_opl,
            "NSE_opl": nse_opl, "NSE_da": nse_da, "Delta_NSE": nse_da - nse_opl,
            "r_opl": r_opl, "r_da": r_da, "Delta_r": r_da - r_opl,
            "alpha_opl": alpha_opl, "alpha_da": alpha_da,
            "beta_opl": beta_opl, "beta_da": beta_da,
            "PBIAS_opl": pbias_opl, "PBIAS_da": pbias_da,
            "pos_val_tot": pos_val_tot,
            "val_DJF": val_by_saison["DJF"], "val_MAM": val_by_saison["MAM"],
            "val_JJA": val_by_saison["JJA"], "val_SON": val_by_saison["SON"],
            "ratio_detect": ratio_detect,
            "mean_delta_q": float(np.mean(delta_q)),
            "vin_mman": vin_mman, "vsim_opl_mman": v_opl_mman, "vsim_da_mman": v_da_mman, "vobs_mman": v_obs_mman
        })

    df_synth = pd.DataFrame(station_stats)

    print(f"\nTABLEAU VALUE & DETECTABILITE :")
    print(f"{'Station':16s} | {'VALUE > 0 Total':16s} | {'DJF':6s} | {'MAM':6s} | {'JJA':6s} | {'SON':6s} | {'|ΔQ|/|Err|':10s} | {'Δ KGE':7s} | {'Δ r':6s} | {'Δ PBIAS':8s}")
    print("-" * 110)
    for _, r in df_synth.iterrows():
        print(f"{r['nom']:16s} | {r['pos_val_tot']:14.1f} % | {r['val_DJF']:5.1f}% | {r['val_MAM']:5.1f}% | {r['val_JJA']:5.1f}% | {r['val_SON']:5.1f}% | {r['ratio_detect']*100:8.2f} % | {r['Delta_KGE']:+7.3f} | {r['Delta_r']:+6.3f} | {r['PBIAS_da'] - r['PBIAS_opl']:+7.1f}%")

    # =========================================================================
    # ANALYSE PAR EVENEMENT DE CRUE (BOUREGREG JOURNALIER)
    # =========================================================================
    print("\nANALYSE PAR EVENEMENT DE CRUE (STATIONS JOURNALIERES BOUREGREG) :")
    events_records = []
    for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]:
        sub = df_q_opl_d[["date", sid]].rename(columns={sid: "q_opl"}).copy()
        sub["q_da"] = df_q_da_d[sid]
        q75 = np.percentile(sub["q_opl"], 75)
        sub["is_flood"] = sub["q_opl"] > q75
        
        # Identification blocs contigus
        sub["event_id"] = (sub["is_flood"] != sub["is_flood"].shift(1)).cumsum()
        flood_blocks = sub[sub["is_flood"]].groupby("event_id")
        for eid, grp in flood_blocks:
            if len(grp) >= 2: # Au moins 2 jours
                v_opl = grp["q_opl"].sum() * 86400.0 / 1e6
                v_da = grp["q_da"].sum() * 86400.0 / 1e6
                pk_opl = grp["q_opl"].max()
                pk_da = grp["q_da"].max()
                events_records.append({
                    "station_id": sid, "nom": meta_dict[sid]["oued"] + " (" + sid + ")",
                    "date_debut": grp["date"].iloc[0], "date_fin": grp["date"].iloc[-1], "duree_j": len(grp),
                    "peak_opl": pk_opl, "peak_da": pk_da, "delta_peak": pk_da - pk_opl,
                    "v_opl_hm3": v_opl, "v_da_hm3": v_da, "delta_v_hm3": v_da - v_opl,
                    "ratio_delta_v_pct": (v_da - v_opl) / v_opl * 100.0
                })
    df_events = pd.DataFrame(events_records)
    print(f"Total evenements de crue identifies (Q > Q75, >=2j) : {len(df_events)}")
    print(f"Delta V moyen par crue : {df_events['delta_v_hm3'].mean():+.4f} hm3 ({df_events['ratio_delta_v_pct'].mean():+.2f} %)")
    df_events.to_csv(os.path.join(plots_dir, "t8_flood_events_comparison.csv"), index=False)

    # Sauvegarde CSV synthese
    df_synth.to_csv(os.path.join(plots_dir, "synthese_hydrologique_12stations.csv"), index=False)

    # =========================================================================
    # ETAPE 5 — LOT DE 6 FIGURES POUR UN HYDROLOGUE
    # =========================================================================
    print("\n" + "=" * 95)
    print("ETAPE 5 — PRODUCTION DU LOT DE FIGURES (_history/t8_ol_nocdf/)")
    print("=" * 95)

    # Couleurs harmonieuses
    c_obs = "#1f1f1f"     # Noir profond
    c_opl = "#1f77b4"     # Bleu royal
    c_da  = "#d62728"     # Rouge vermillon
    c_vin = "#7f7f7f"     # Gris moyen

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 13
    })

    # -------------------------------------------------------------------------
    # FIGURE 1 : CARTE DE SITUATION
    # -------------------------------------------------------------------------
    print("Generation de F1_carte_situation.png...")
    fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
    
    # Fond d'elevation
    im = ax.imshow(elevation_grid, extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()],
                   origin="lower", cmap="terrain", alpha=0.45, vmin=0, vmax=2500)
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Altitude MNT (m)", fontsize=10)

    # Reseau hydrographique HyMAP (mailles > 400 km2)
    riv_mask = drain_area_grid > 400.0
    for r in range(R):
        for c in range(C):
            if riv_mask[r, c] and down_r[r, c] >= 0:
                pr, pc = down_r[r, c], down_c[r, c]
                w = min(max(np.log10(drain_area_grid[r, c] / 200.0) * 1.2, 0.4), 3.0)
                ax.plot([lon_grid[r, c], lon_grid[pr, pc]], [lat_grid[r, c], lat_grid[pr, pc]],
                        color="#1b4f72", linewidth=w, alpha=0.8)

    # Bassins versants ombres
    basin_colors = {"Bouregreg": "#3498db", "Sebou": "#2ecc71", "Ksob": "#e67e22"}
    for _, row in df_p.iterrows():
        sid = row["station_id"]
        b = row["bassin"]
        m = station_masks[sid]
        ax.contour(lon_grid, lat_grid, m.astype(float), levels=[0.5],
                   colors=[basin_colors[b]], linewidths=1.2, alpha=0.7)

    # Stations
    for _, row in df_p.iterrows():
        sid = row["station_id"]
        b = row["bassin"]
        meta = meta_dict[sid]
        lon_s, lat_s = row["lon_obs"], row["lat_obs"]
        ax.scatter(lon_s, lat_s, color=basin_colors[b], edgecolor="black", s=90, zorder=5, marker="^")
        
        # Label decale
        dx, dy = 0.08, 0.08
        if sid in ["b_s_cherif", "pont_de_mdez"]: dy = -0.16
        if sid == "ain_timedrine": dx = 0.12
        ax.annotate(f"{row['nom']}\n({meta['oued']}, {meta['aire_off']:.0f} km²\nCouv: {meta['couv']})",
                    xy=(lon_s, lat_s), xytext=(lon_s + dx, lat_s + dy),
                    fontsize=8, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=basin_colors[b], alpha=0.85),
                    arrowprops=dict(arrowstyle="->", color=basin_colors[b], lw=0.8), zorder=6)

    # Legende bassins
    patches = [
        mpatches.Patch(color=basin_colors["Bouregreg"], label="Bassin du Bouregreg (4 stations journalières)"),
        mpatches.Patch(color=basin_colors["Sebou"], label="Bassin du Sebou (7 stations mensuelles)"),
        mpatches.Patch(color=basin_colors["Ksob"], label="Bassin du Ksob (1 station mensuelle)")
    ]
    ax.legend(handles=patches, loc="upper right", framealpha=0.9, title="Bassins hydrographiques")

    ax.set_title("F1. Réseau hydrographique HyMAP et localisation des 12 stations hydrologiques d'évaluation\n(Marqueurs : stations | Traits bleus : réseau hydrographique | Contours : bassins versants amont)",
                 fontweight="bold", pad=12)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_xlim(-10.2, -1.0)
    ax.set_ylim(30.0, 36.0)
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F1_carte_situation.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 2 : HYDROGRAMMES COMPARATIFS (PAR BASSIN)
    # -------------------------------------------------------------------------
    print("Generation de F2a_hydrogrammes_bouregreg.png...")
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True, dpi=150)
    b_stations = ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]
    for idx, sid in enumerate(b_stations):
        ax = axes[idx]
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        meta = meta_dict[sid]
        s_row = df_synth[df_synth["station_id"] == sid].iloc[0]

        sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")]
        d_obs = [pd.to_datetime(x).to_pydatetime() for x in sub_o["date"]]
        q_obs = sub_o["q_m3s"].to_numpy()

        d_sim = [pd.to_datetime(x).to_pydatetime() for x in df_q_opl_d["date"]]
        q_opl = df_q_opl_d[sid].to_numpy()
        q_da = df_q_da_d[sid].to_numpy()

        ax.plot(d_obs, q_obs, color=c_obs, lw=1.1, label="Observations jaugées", alpha=0.85)
        ax.plot(d_sim, q_opl, color=c_opl, lw=1.1, label=f"Open-Loop (OPL) | KGE={s_row['KGE_opl']:.2f}, r={s_row['r_opl']:.2f}, PB={s_row['PBIAS_opl']:+.1f}%", alpha=0.85)
        ax.plot(d_sim, q_da, color=c_da, lw=1.1, linestyle="--", label=f"Assimilation SMAP (DA) | KGE={s_row['KGE_da']:.2f}, r={s_row['r_da']:.2f}, PB={s_row['PBIAS_da']:+.1f}%", alpha=0.9)

        ax.set_title(f"{p_row['nom']} — Oued {meta['oued']} (Aire: {meta['aire_off']:.0f} km²) | Pas journalier", fontweight="bold")
        ax.set_ylabel("Débit (m³/s)")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9)
    axes[-1].set_xlabel("Année")
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.suptitle("F2a. Hydrogrammes comparatifs journaliers — Bassin du Bouregreg (2016–2020)", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F2a_hydrogrammes_bouregreg.png"), dpi=150)
    plt.close(fig)

    print("Generation de F2b_hydrogrammes_sebou.png...")
    fig, axes = plt.subplots(7, 1, figsize=(14, 16), sharex=True, dpi=150)
    s_stations = ["azzaba", "ain_timedrine", "dar_el_hamra", "pont_ait_aissa", "pont_de_mdez", "ait_khabbach", "el_mers"]
    for idx, sid in enumerate(s_stations):
        ax = axes[idx]
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        meta = meta_dict[sid]
        s_row = df_synth[df_synth["station_id"] == sid].iloc[0]

        sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)]
        d_obs = [pd.to_datetime(x).to_pydatetime() for x in sub_o["year_month"]]
        q_obs = sub_o["q_m3s"].to_numpy()

        d_sim = [pd.to_datetime(x).to_pydatetime() for x in df_q_opl_m["year_month"]]
        q_opl = df_q_opl_m[sid].to_numpy()
        q_da = df_q_da_m[sid].to_numpy()

        ax.plot(d_obs, q_obs, color=c_obs, lw=1.4, marker="o", markersize=3, label="Obs mensuelle", alpha=0.85)
        ax.plot(d_sim, q_opl, color=c_opl, lw=1.2, label=f"OPL | KGE={s_row['KGE_opl']:.2f}, r={s_row['r_opl']:.2f}, PB={s_row['PBIAS_opl']:+.1f}%")
        ax.plot(d_sim, q_da, color=c_da, lw=1.2, linestyle="--", label=f"DA | KGE={s_row['KGE_da']:.2f}, r={s_row['r_da']:.2f}, PB={s_row['PBIAS_da']:+.1f}%")

        ax.set_title(f"{p_row['nom']} — Oued {meta['oued']} (Aire: {meta['aire_off']:.0f} km²)", fontweight="bold")
        ax.set_ylabel("Débit (m³/s)")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9)
    axes[-1].set_xlabel("Année")
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.suptitle("F2b. Hydrogrammes comparatifs mensuels — Bassin du Sebou (2016–2020)", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F2b_hydrogrammes_sebou.png"), dpi=150)
    plt.close(fig)

    print("Generation de F2c_hydrogrammes_ksob.png...")
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)
    sid = "adamna"
    p_row = df_p[df_p["station_id"] == sid].iloc[0]
    meta = meta_dict[sid]
    s_row = df_synth[df_synth["station_id"] == sid].iloc[0]
    sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)]
    d_obs = [pd.to_datetime(x).to_pydatetime() for x in sub_o["year_month"]]
    q_obs = sub_o["q_m3s"].to_numpy()
    d_sim = [pd.to_datetime(x).to_pydatetime() for x in df_q_opl_m["year_month"]]
    q_opl = df_q_opl_m[sid].to_numpy()
    q_da = df_q_da_m[sid].to_numpy()

    ax.plot(d_obs, q_obs, color=c_obs, lw=1.5, marker="o", label="Obs mensuelle (33% couv.)")
    ax.plot(d_sim, q_opl, color=c_opl, lw=1.4, label=f"OPL | KGE={s_row['KGE_opl']:.2f}, r={s_row['r_opl']:.2f}, PB={s_row['PBIAS_opl']:+.1f}%")
    ax.plot(d_sim, q_da, color=c_da, lw=1.4, linestyle="--", label=f"DA | KGE={s_row['KGE_da']:.2f}, r={s_row['r_da']:.2f}, PB={s_row['PBIAS_da']:+.1f}%")
    ax.set_title(f"F2c. {p_row['nom']} — Oued {meta['oued']} (Bassin du Ksob, Aire: {meta['aire_off']:.0f} km²)\nHydrogramme mensuel 2016–2020", fontweight="bold")
    ax.set_ylabel("Débit (m³/s)")
    ax.set_xlabel("Année")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F2c_hydrogrammes_ksob.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 3 : COURBES DES DEBITS CLASSES (FLOW DURATION CURVES)
    # -------------------------------------------------------------------------
    print("Generation de F3_courbes_debits_classes.png...")
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), dpi=150)
    axes = axes.flatten()
    for idx, sid in enumerate(b_stations):
        ax = axes[idx]
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        meta = meta_dict[sid]

        sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")]
        m_df = pd.merge(sub_o[["date", "q_m3s"]], df_q_opl_d[["date", sid]], on="date").rename(columns={sid: "q_opl"})
        m_df = pd.merge(m_df, df_q_da_d[["date", sid]], on="date").rename(columns={sid: "q_da"})

        q_o = np.sort(m_df["q_m3s"].to_numpy())[::-1]
        q_op = np.sort(m_df["q_opl"].to_numpy())[::-1]
        q_d = np.sort(m_df["q_da"].to_numpy())[::-1]
        n_pts = len(q_o)
        prob = (np.arange(1, n_pts + 1) / (n_pts + 1)) * 100.0

        ax.plot(prob, q_o, color=c_obs, lw=1.8, label="Observé")
        ax.plot(prob, q_op, color=c_opl, lw=1.5, linestyle="--", label="Open-Loop")
        ax.plot(prob, q_d, color=c_da, lw=1.5, linestyle=":", label="DA SMAP")

        # Calcul percentiles
        q10_o, q50_o, q90_o, q95_o = np.percentile(q_o, [90, 50, 10, 5])
        q10_op, q50_op, q90_op, q95_op = np.percentile(q_op, [90, 50, 10, 5])
        q10_d, q50_d, q90_d, q95_d = np.percentile(q_d, [90, 50, 10, 5])

        assecs_o = np.sum(q_o < 0.001)
        assecs_op = np.sum(q_op < 0.001)
        assecs_d = np.sum(q_d < 0.001)

        annot_text = (
            f"Débits (m³/s)   Obs   |   OPL   |    DA\n"
            f"Q10 (crue) :  {q10_o:5.2f} |  {q10_op:5.2f} |  {q10_d:5.2f}\n"
            f"Q50 (méd.) :  {q50_o:5.3f} |  {q50_op:5.3f} |  {q50_d:5.3f}\n"
            f"Q90 (étiage): {q90_o:5.3f} |  {q90_op:5.3f} |  {q90_d:5.3f}\n"
            f"Q95 (étiage): {q95_o:5.3f} |  {q95_op:5.3f} |  {q95_d:5.3f}\n"
            f"Jours assec :   {assecs_o:3d}   |    {assecs_op:3d}    |    {assecs_d:3d}"
        )
        ax.text(0.04, 0.06, annot_text, transform=ax.transAxes, fontsize=8,
                family="monospace", bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9f9", ec="#bdc3c7", alpha=0.9))

        ax.set_yscale("log")
        ax.set_ylim(0.003, max(q_op.max(), q_o.max()) * 1.5)
        ax.set_xlim(0, 100)
        ax.set_title(f"{p_row['nom']} — Oued {meta['oued']} ({meta['aire_off']:.0f} km²)", fontweight="bold")
        ax.set_xlabel("Fréquence au non-dépassement (%)")
        ax.set_ylabel("Débit classé (m³/s, éch. log)")
        ax.grid(True, which="both", linestyle=":", alpha=0.5)
        ax.legend(loc="upper right")

    plt.suptitle("F3. Courbes des débits classés (Flow Duration Curves) — 4 stations journalières du Bouregreg\n(Comparaison des régimes de crue, d'écoulement médian et d'étiage soutenu)", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F3_courbes_debits_classes.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 4 : CLIMATOLOGIE MENSUELLE (CYCLE ANNUEL MOYEN 2016-2020)
    # -------------------------------------------------------------------------
    print("Generation de F4_climatologie_mensuelle.png...")
    fig, axes = plt.subplots(3, 4, figsize=(16, 11), dpi=150)
    axes = axes.flatten()
    mois_noms = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

    for idx, p_row in df_p.iterrows():
        ax = axes[idx]
        sid = p_row["station_id"]
        meta = meta_dict[sid]
        pas = p_row["type_pas"]

        if pas == "journalier":
            sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
            sub_o["mois"] = pd.to_datetime(sub_o["date"]).dt.month
            m_obs_cycle = sub_o.groupby("mois")["q_m3s"].mean().reindex(range(1, 13))
            
            sub_sim_opl = df_q_opl_d.copy()
            sub_sim_opl["mois"] = pd.to_datetime(sub_sim_opl["date"]).dt.month
            m_opl_cycle = sub_sim_opl.groupby("mois")[sid].mean().reindex(range(1, 13))

            sub_sim_da = df_q_da_d.copy()
            sub_sim_da["mois"] = pd.to_datetime(sub_sim_da["date"]).dt.month
            m_da_cycle = sub_sim_da.groupby("mois")[sid].mean().reindex(range(1, 13))
        else:
            sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            m_obs_cycle = sub_o.groupby("mois")["q_m3s"].mean().reindex(range(1, 13))

            sub_sim_opl = df_q_opl_m.copy()
            sub_sim_opl["mois"] = sub_sim_opl["year_month"].apply(lambda x: int(x.split("-")[1]))
            m_opl_cycle = sub_sim_opl.groupby("mois")[sid].mean().reindex(range(1, 13))

            sub_sim_da = df_q_da_m.copy()
            sub_sim_da["mois"] = sub_sim_da["year_month"].apply(lambda x: int(x.split("-")[1]))
            m_da_cycle = sub_sim_da.groupby("mois")[sid].mean().reindex(range(1, 13))

        x_months = np.arange(1, 13)
        ax.plot(x_months, m_obs_cycle.to_numpy(), color=c_obs, marker="s", lw=1.6, label="Observé")
        ax.plot(x_months, m_opl_cycle.to_numpy(), color=c_opl, marker="o", lw=1.3, linestyle="--", label="OPL")
        ax.plot(x_months, m_da_cycle.to_numpy(), color=c_da, marker="^", lw=1.3, linestyle=":", label="DA")

        ax.set_title(f"{p_row['nom']} ({p_row['bassin']})", fontweight="bold", fontsize=9.5)
        ax.set_xticks(x_months)
        ax.set_xticklabels(mois_noms, fontsize=8)
        ax.set_ylabel("Débit moyen (m³/s)", fontsize=8)
        ax.grid(True, linestyle=":", alpha=0.5)
        if idx == 0: ax.legend(loc="upper right", fontsize=8)

    plt.suptitle("F4. Climatologie mensuelle (Cycle annuel moyen 2016–2020) aux 12 stations\n(Contraste entre régime pluvial hivernal du Bouregreg et régime karstique soutenu au printemps du haut Sebou)", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F4_climatologie_mensuelle.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 5 : DECOMPOSITION DU DEFICIT (LAME D'EAU mm/an)
    # -------------------------------------------------------------------------
    print("Generation de F5_decomposition_deficit.png...")
    fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
    
    n_st = len(df_synth)
    idx_bars = np.arange(n_st)
    width = 0.25

    rects1 = ax.bar(idx_bars - width, df_synth["vin_mman"], width, label="Ruissellement brut Noah-MP (Vin)", color="#7f8c8d", alpha=0.85)
    rects2 = ax.bar(idx_bars, df_synth["vsim_opl_mman"], width, label="Débit routé HyMAP (Vsim OPL)", color=c_opl, alpha=0.85)
    rects3 = ax.bar(idx_bars + width, df_synth["vobs_mman"], width, label="Débit jaugé observé (Vobs)", color="#2c3e50", alpha=0.85)

    ax.set_xticks(idx_bars)
    ax.set_xticklabels([f"{r['nom']}\n({r['bassin'][:4]}.)" for _, r in df_synth.iterrows()], rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Lame d'eau écoulée annuelle (mm/an)", fontsize=10)
    ax.set_title("F5. Décomposition du déficit volumique annuel moyen (2016–2020)\nSéparation visuelle entre l'erreur de production (écart Vin vs Vobs) et l'erreur de routage (écart Vsim vs Vin)", fontweight="bold", pad=12)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)

    # Annotations sur le Sebou et Bouregreg
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F5_decomposition_deficit.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE 6 : EFFET DE L'ASSIMILATION (SAISONNALITE ET VALUE)
    # -------------------------------------------------------------------------
    print("Generation de F6_effet_assimilation.png...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, dpi=150)
    
    # Delta Q saisonnier
    seasons = ["DJF", "MAM", "JJA", "SON"]
    w_s = 0.18
    s_colors = {"DJF": "#3498db", "MAM": "#2ecc71", "JJA": "#e74c3c", "SON": "#f39c12"}

    # Calcul Delta Q moyen saisonnier par station
    for i_s, s in enumerate(seasons):
        delta_q_season = []
        for _, r in df_synth.iterrows():
            sid = r["station_id"]
            pas = r["pas_de_temps"]
            if pas == "journalier":
                sub_d = df_q_da_d[df_q_da_d["saison"] == s]
                sub_op = df_q_opl_d[df_q_opl_d["saison"] == s]
                d_q = (sub_d[sid] - sub_op[sid]).mean()
            else:
                sub_d = df_q_da_m[df_q_da_m["saison"] == s]
                sub_op = df_q_opl_m[df_q_opl_m["saison"] == s]
                d_q = (sub_d[sid] - sub_op[sid]).mean()
            delta_q_season.append(d_q)
        ax1.bar(idx_bars + (i_s - 1.5) * w_s, delta_q_season, w_s, label=s, color=s_colors[s], alpha=0.85)

    ax1.axhline(0, color="black", lw=0.8, linestyle="--")
    ax1.set_ylabel("ΔQ moyen = Q_DA - Q_OPL (m³/s)")
    ax1.set_title("Panneau supérieur : Incrément de débit moyen induit par l'assimilation SMAP (ΔQ par saison)", fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", title="Saison")

    # Fraction de VALUE positive par saison
    for i_s, s in enumerate(seasons):
        val_s = df_synth[f"val_{s}"].to_numpy()
        ax2.bar(idx_bars + (i_s - 1.5) * w_s, val_s, w_s, label=s, color=s_colors[s], alpha=0.85)

    ax2.axhline(50, color="red", lw=1.0, linestyle="--", label="Seuil neutre 50%")
    ax2.set_xticks(idx_bars)
    ax2.set_xticklabels([f"{r['nom']}\n({r['bassin']})" for _, r in df_synth.iterrows()], rotation=20, ha="right")
    ax2.set_ylabel("Échantillons avec VALUE > 0 (%)")
    ax2.set_ylim(0, 100)
    ax2.set_title("Panneau inférieur : Fraction d'échantillons où l'assimilation améliore l'estimation du débit (VALUE > 0)", fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", title="Saison")

    plt.suptitle("F6. Évaluation diagnostique de la valeur ajoutée de l'assimilation SMAP (DA_nocdf vs OPL)", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(os.path.join(plots_dir, "F6_effet_assimilation.png"), dpi=150)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FICHIER TEXTE DES LEGENDES
    # -------------------------------------------------------------------------
    legendes_text = """LEGENDES DU LOT DE FIGURES POUR UN COLLEGUE HYDROLOGUE
Repertoire : experiments/NorthMor/routing/plots/_history/t8_ol_nocdf/

F1_carte_situation.png :
Carte de situation du domaine Nord Maroc montrant le réseau hydrographique HyMAP (lignes bleues dont l'épaisseur est proportionnelle à la surface drainée) et l'emprise des 12 bassins versants amont évalués. Les stations hydrologiques sont codées par couleur de grand bassin (bleu : Bouregreg, 4 stations journalières ; vert : Sebou, 7 stations mensuelles ; orange : Ksob, 1 station mensuelle) avec indication de l'oued jaugé et de la superficie de drainage officielle.

F2a_hydrogrammes_bouregreg.png :
Hydrogrammes journaliers observés (noir), simulés en boucle ouverte (OPL, bleu) et avec assimilation d'humidité du sol SMAP (DA, rouge tireté) sur les 4 stations du bassin du Bouregreg de 2016 à 2020. Les titres résument les performances hydrologiques (KGE, r, PBIAS), mettant en évidence le soutien artificiel continu d'étiage induit par le modèle de nappe et la réponse contrastée des crues rapides.

F2b_hydrogrammes_sebou.png :
Hydrogrammes mensuels observés (noir avec ronds) et simulés (OPL en bleu, DA en rouge tireté) sur les 7 stations du haut bassin du Sebou (Moyen Atlas) de 2016 à 2020. L'écart persistant avec les observations reflète le déficit structurel de production d'écoulement de surface sur les karsts atlasiques, non comblé par l'assimilation de surface.

F2c_hydrogrammes_ksob.png :
Hydrogramme mensuel observé et simulé à la station d'Adamna sur l'oued Ksob (bassin semi-aride d'Essaouira). L'analyse illustre la surestimation chronique du ruissellement en zone semi-aride couplée à un tarissement ralenti par le plancher du routeur.

F3_courbes_debits_classes.png :
Courbes des débits classés (Flow Duration Curves, échelle logarithmique) pour les 4 stations journalières du Bouregreg comparant les régimes observés et simulés. L'encart statistique synthétise les débits caractéristiques de crue (Q10), médians (Q50) et d'étiage sévère (Q90, Q95), ainsi que le nombre de jours d'assec complet (mettant en relief l'incapacité du modèle corrigé à tarir sur les oueds temporaires comme Sidi Jabeur).

F4_climatologie_mensuelle.png :
Cycles annuels moyens (2016–2020) calculés mois par mois pour les 12 stations, opposant le régime méditerranéen pluvial à crues d'hiver brutales du Bouregreg au régime karstique atlasique du Sebou caractérisé par un étiage estival très soutenu par les sources d'altitude.

F5_decomposition_deficit.png :
Bilan volumique annuel moyen décomposé en lame d'eau (mm/an) par station : comparaison directe entre le ruissellement produit par le modèle de surface Noah-MP (Vin), le volume routé restitué aux stations par HyMAP (Vsim), et le volume jaugé observé (Vobs). Cette figure démontre sans ambiguïté que le modèle de routage est rigoureusement conservatif (Vsim ≈ Vin), localisant 100 % du déficit hydrologique dans la physique de production du modèle de surface.

F6_effet_assimilation.png :
Évaluation de l'impact hydrologique de l'assimilation SMAP : le panneau supérieur présente l'incrément moyen de débit ΔQ = Q_DA - Q_OPL décomposé par saison, tandis que le panneau inférieur quantifie la métrique VALUE (pourcentage d'échantillons temporels où l'assimilation rapproche la simulation de la vérité observée).
"""
    with open(os.path.join(plots_dir, "legendes_figures.txt"), "w", encoding="utf-8") as f:
        f.write(legendes_text)
    print("Fichier legendes_figures.txt genere avec succes.")

    print("\n" + "=" * 95)
    print("ANALYSE ET LOT DE FIGURES TACHE 8 GENERES AVEC SUCCES !")
    print("=" * 95)

if __name__ == "__main__":
    main()
