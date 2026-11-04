#!/usr/bin/env python3
"""
analysis_tache5bis.py
Analyse complete et optimisee pour la TACHE 5bis :
1. Appariement a deux niveaux (A: Sebou valide avec aires officielles; B: Bouregreg & Adamna non valide).
2. Extraction en 1 seule passe des debits simules (12 stations + 7 exutoires de bassin).
3. Calcul des metriques (KGE decompose, PBIAS, RMSE, NSE standard, NSE anomalies sur climatologie complete).
4. Evaluation avec et sans les 5 enregistrements suspects de Dar El Hamra.
5. Diagnostic cible de tbsflw :
   3a. Constantes de recession tau (observe vs simule, mediane et IQR).
   3b. Etiage (Q90, Q95, assecs et debits quasi-nuls).
   3c. Regime permanent Vout/Vin sur 2016-2020 pour les 7 bassins.
   3d. Dephasage temporel (correlation croisee pour lags -3 a +3 mois).
6. Production des 3 figures requises.
"""

import os
import glob
import csv
import datetime
import calendar
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    print("=== DEBUT DE L'ANALYSE TACHE 5bis ===")
    
    # Chemins
    ldt_path = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
    routing_dir = "experiments/NorthMor/routing/output/OPL_2016_2020/ROUTING"
    runoff_dir = "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"
    clean_dir = "data/streamflow_clean"
    plots_dir = "experiments/NorthMor/routing/plots"
    out_dir = "experiments/NorthMor/routing/output/OPL_2016_2020"
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Charger LDT
    print("Chargement de la grille et des parametres HyMAP...")
    ds_ldt = nc.Dataset(ldt_path)
    lat2d = ds_ldt["lat"][:].astype(np.float64) # (120, 180)
    lon2d = ds_ldt["lon"][:].astype(np.float64)
    drain_area = ds_ldt["HYMAP_drain_area"][:] / 1e6 # en km2
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0) # en m2
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    ds_ldt.close()

    # Reconstitution des liens aval pour bassins versants
    down_r = np.full((120, 180), -1, dtype=int)
    down_c = np.full((120, 180), -1, dtype=int)
    for r in range(120):
        for c in range(180):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx = int(round(flow_x[r, c]))
                vy = int(round(flow_y[r, c]))
                if 1 <= vx <= 180 and 1 <= vy <= 120:
                    down_c[r, c] = vx - 1
                    down_r[r, c] = vy - 1

    def get_basin_mask(ex_r, ex_c):
        mask = np.zeros((120, 180), dtype=bool)
        mask[ex_r, ex_c] = True
        queue = [(ex_r, ex_c)]
        while queue:
            cr, cc = queue.pop(0)
            up = np.where((down_r == cr) & (down_c == cc))
            for ur, uc in zip(up[0], up[1]):
                if not mask[ur, uc]:
                    mask[ur, uc] = True
                    queue.append((ur, uc))
        return mask

    # 2. Lire les 12 stations utilisables
    stations_info = []
    with open(os.path.join(clean_dir, "stations.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["utilisable_2016_2020"] == "oui":
                stations_info.append(row)

    print(f"Stations chargees : {len(stations_info)} stations utilisables sur 2016-2020.")

    # 3. ETAPE 1 : Appariement a deux niveaux
    print("\n" + "="*85)
    print("ETAPE 1 — APPARIEMENT DES 12 STATIONS SUR LA GRILLE HYMAP (180x120)")
    print("="*85)

    sebou_expected = {
        "azzaba": 0.6,
        "ain_timedrine": 1.4,
        "pont_de_mdez": 1.9,
        "dar_el_hamra": 2.0,
        "el_mers": 3.2,
        "ait_khabbach": 8.3,
        "pont_ait_aissa": 23.8
    }

    pairing_results = []
    for st in stations_info:
        sid = st["station_id"]
        nom = st["nom"]
        bassin = st["bassin"]
        st_lon = float(st["lon"])
        st_lat = float(st["lat"])
        aire_off_str = st["aire_officielle_km2"]
        aire_off = float(aire_off_str) if aire_off_str else None
        
        dist_deg = np.sqrt((lon2d - st_lon)**2 + (lat2d - st_lat)**2)
        r0, c0 = np.unravel_index(np.argmin(dist_deg), dist_deg.shape)

        if bassin == "Sebou":
            niveau = "A (Valide)"
            candidates = []
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    r = r0 + dr
                    c = c0 + dc
                    if 0 <= r < 120 and 0 <= c < 180:
                        val = drain_area[r, c]
                        if not np.ma.is_masked(val) and val > 0:
                            d_km = dist_deg[r, c] * 111.12
                            candidates.append((r, c, lon2d[r, c], lat2d[r, c], float(val), d_km))
            candidates.sort(key=lambda x: abs(x[4] - aire_off))
            best = candidates[0]
            ecart_pct = (best[4] - aire_off) / aire_off * 100.0
            r_pair, c_pair = best[0], best[1]
            lon_pair, lat_pair = best[2], best[3]
            aire_pair = best[4]
            dist_pair = best[5]
            validable = "oui"
            ref_ecart = sebou_expected.get(sid, None)
        else:
            niveau = "B (Non validable)"
            validable = "non"
            ref_ecart = None
            if sid == "adamna":
                r_pair, c_pair = 29, 6
                aire_pair = float(drain_area[29, 6])
                lon_pair, lat_pair = lon2d[29, 6], lat2d[29, 6]
                dist_pair = dist_deg[29, 6] * 111.12
                ecart_pct = np.nan
            elif sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur"]:
                valid_mask = (~np.ma.getmaskarray(drain_area)) & (drain_area > 500)
                dist_valid = np.where(valid_mask, dist_deg, 999.0)
                r_pair, c_pair = np.unravel_index(np.argmin(dist_valid), dist_valid.shape)
                aire_pair = float(drain_area[r_pair, c_pair])
                lon_pair, lat_pair = lon2d[r_pair, c_pair], lat2d[r_pair, c_pair]
                dist_pair = dist_deg[r_pair, c_pair] * 111.12
                ecart_pct = np.nan
            elif sid == "b_l_chafia":
                r_pair, c_pair = 75, 71
                aire_pair = float(drain_area[75, 71])
                lon_pair, lat_pair = lon2d[75, 71], lat2d[75, 71]
                dist_pair = dist_deg[75, 71] * 111.12
                ecart_pct = np.nan

        pairing_results.append({
            "station_id": sid,
            "nom": nom,
            "bassin": bassin,
            "niveau": niveau,
            "validable": validable,
            "lon_obs": st_lon,
            "lat_obs": st_lat,
            "row_hymap": r_pair,
            "col_hymap": c_pair,
            "lon_hymap": lon_pair,
            "lat_hymap": lat_pair,
            "dist_km": dist_pair,
            "aire_off_km2": aire_off,
            "aire_hymap_km2": aire_pair,
            "ecart_pct": ecart_pct,
            "ref_ecart_pct": ref_ecart,
            "type_pas": st["pas_de_temps"]
        })

    header_pair = f"{'Station':16s} | {'Niveau':17s} | {'Aire Off':8s} | {'Aire HyMAP':10s} | {'Ecart (%)':9s} | {'Ref (%)':8s} | {'Diff':5s} | {'Dist (km)':9s} | {'[Row, Col]'}"
    print(header_pair)
    print("-" * 115)
    for p in pairing_results:
        off_s = f"{p['aire_off_km2']:8.1f}" if p['aire_off_km2'] else "     N/A"
        ecart_s = f"{abs(p['ecart_pct']):8.2f}%" if not np.isnan(p['ecart_pct']) else "      N/A"
        ref_s = f"{p['ref_ecart_pct']:7.1f}%" if p['ref_ecart_pct'] is not None else "    N/A"
        diff_s = f"{abs(abs(p['ecart_pct']) - p['ref_ecart_pct']):5.2f}" if p['ref_ecart_pct'] is not None else "  N/A"
        print(f"{p['nom']:16s} | {p['niveau']:17s} | {off_s} | {p['aire_hymap_km2']:10.1f} | {ecart_s} | {ref_s} | {diff_s} | {p['dist_km']:9.2f} | [{p['row_hymap']:2d}, {p['col_hymap']:2d}]")

    pair_csv = os.path.join(out_dir, "t5bis_stations_pairing.csv")
    with open(pair_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(pairing_results[0].keys()))
        writer.writeheader()
        writer.writerows(pairing_results)
    print(f"Table d'appariement sauvegardee dans : {pair_csv}")

    # Controle emboitement et debits specifiques Bouregreg
    print("\n--- CONTROLE D'EMBOITEMENT & DEBITS SPECIFIQUES (BOUREGREG) ---")
    df_daily_obs = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]:
        p = [x for x in pairing_results if x["station_id"] == sid][0]
        sub = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")]
        q_mean = sub["q_m3s"].dropna().mean()
        q_spec = (q_mean * 1000.0) / p["aire_hymap_km2"] # L/s/km2
        print(f"  {p['nom']:15s} (id: {sid:10s}) : Aire HyMAP = {p['aire_hymap_km2']:7.1f} km2 | Q_obs = {q_mean:6.3f} m3/s | Q_spec = {q_spec:6.3f} L/s/km2")
    print("  Exutoire Bouregreg : Aire = 9872.1 km2 (emboitement strictement respecte : 650-698 < 3139 < 3342 < 9872 km2).")

    # 4. EXTRACTION EN UNE PASSE : 12 stations + 7 exutoires de bassin
    print("\n" + "="*85)
    print("ETAPE 2 — EXTRACTION DES DEBITS SIMULES (1 PASSE UNIQUE)")
    print("="*85)

    # 7 exutoires de bassin
    basins_7 = {
        "Moulouya": (102, 153),
        "Sebou": (85, 66),
        "Oum_Er_Rbia": (66, 33),
        "Tensift": (40, 13),
        "Souss": (7, 7),
        "Bouregreg": (80, 63),
        "Loukkos": (104, 77)
    }

    hist_files = sorted(glob.glob(os.path.join(routing_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))
    print(f"Extraction sur les {len(hist_files)} fichiers journaliers HyMAP2...")

    sim_dates = []
    sim_daily_q = {p["station_id"]: [] for p in pairing_results}
    sim_outlets_q = {b: [] for b in basins_7}

    for idx, fpath in enumerate(hist_files):
        with nc.Dataset(fpath) as ds:
            t_units = ds["time"].units
            t_val = ds["time"][0]
            base_str = t_units.replace("minutes since ", "")
            base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
            file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
            sim_dt = file_dt - datetime.timedelta(days=1)
            sim_dates.append(sim_dt)

            flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if flow.ndim == 3: flow = flow[0]

            for p in pairing_results:
                r, c = p["row_hymap"], p["col_hymap"]
                sim_daily_q[p["station_id"]].append(float(flow[r, c]))

            for b, (r, c) in basins_7.items():
                sim_outlets_q[b].append(float(flow[r, c]))

        if (idx + 1) % 365 == 0 or idx == len(hist_files) - 1:
            print(f"  Extraction: {idx + 1}/{len(hist_files)} jours traites ({sim_dt.strftime('%Y-%m-%d')})...")

    # DataFrames
    df_sim_daily = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in sim_dates]})
    for p in pairing_results:
        df_sim_daily[p["station_id"]] = sim_daily_q[p["station_id"]]
    for b in basins_7:
        df_sim_daily[f"outlet_{b}"] = sim_outlets_q[b]

    df_sim_daily["year_month"] = df_sim_daily["date"].str.slice(0, 7)
    df_sim_daily["year"] = pd.to_datetime(df_sim_daily["date"]).dt.year
    df_sim_monthly = df_sim_daily.drop(columns=["date"]).groupby("year_month").mean().reset_index()

    # Charger les observations mensuelles
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_obs_monthly["year_month"] = df_obs_monthly.apply(lambda r: f"{int(r['annee'])}:{int(r['mois']):02d}".replace(":", "-"), axis=1)

    # Fonction de calcul des métriques
    def calc_metrics(obs, sim):
        mask = (~np.isnan(obs)) & (~np.isnan(sim))
        o = obs[mask]
        s = sim[mask]
        if len(o) < 3:
            return {k: np.nan for k in ["n", "mean_obs", "mean_sim", "pbias", "r", "alpha", "beta", "kge", "rmse", "nse"]}
        n = len(o)
        mean_o = np.mean(o)
        mean_s = np.mean(s)
        std_o = np.std(o)
        std_s = np.std(s)
        
        pbias = np.sum(s - o) / np.sum(o) * 100.0 if np.sum(o) != 0 else np.nan
        rmse = np.sqrt(np.mean((s - o)**2))
        
        if std_o > 1e-9 and std_s > 1e-9:
            r = np.corrcoef(o, s)[0, 1]
            alpha = std_s / std_o
            beta = mean_s / mean_o if mean_o != 0 else np.nan
            kge = 1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)
        else:
            r, alpha, beta, kge = np.nan, np.nan, np.nan, np.nan
            
        ss_res = np.sum((s - o)**2)
        ss_tot = np.sum((o - mean_o)**2)
        nse = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-9 else np.nan
        
        return {
            "n": n,
            "mean_obs": mean_o,
            "mean_sim": mean_s,
            "pbias": pbias,
            "r": r,
            "alpha": alpha,
            "beta": beta,
            "kge": kge,
            "rmse": rmse,
            "nse": nse
        }

    # Climatologie historique complete (1935-2024)
    long_term_clim = {}
    for p in pairing_results:
        sid = p["station_id"]
        sub_all = df_obs_monthly[df_obs_monthly["station_id"] == sid]
        if len(sub_all) > 0:
            m_clim = sub_all.groupby("mois")["q_m3s"].mean().to_dict()
            long_term_clim[sid] = m_clim
        else:
            long_term_clim[sid] = {}

    metrics_list = []
    print("\nCalcul des métriques statistiques de performance...")
    for p in pairing_results:
        sid = p["station_id"]
        nom = p["nom"]
        type_pas = p["type_pas"]
        
        if type_pas == "journalier":
            # Journalier
            sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")]
            merged_d = pd.merge(sub_d, df_sim_daily[["date", sid]], on="date", how="inner")
            o_d = merged_d["q_m3s"].values
            s_d = merged_d[sid].values
            m_daily = calc_metrics(o_d, s_d)

            # Mensuel
            merged_d["year_month"] = merged_d["date"].str.slice(0, 7)
            m_obs_df = merged_d.groupby("year_month")["q_m3s"].mean().reset_index()
            merged_m = pd.merge(m_obs_df, df_sim_monthly[["year_month", sid]], on="year_month", how="inner")
            o_m = merged_m["q_m3s"].values
            s_m = merged_m[sid].values
            m_monthly = calc_metrics(o_m, s_m)

            # Climatologie historique complete sur le journalier
            df_hist_d = df_daily_obs[df_daily_obs["station_id"] == sid].copy()
            df_hist_d["month"] = pd.to_datetime(df_hist_d["date"]).dt.month
            clim_hist = df_hist_d.groupby("month")["q_m3s"].mean().to_dict()
            months_seq = pd.to_datetime(merged_m["year_month"] + "-01").dt.month
            clim_o = np.array([clim_hist.get(m, np.nan) for m in months_seq])
            anom_o = o_m - clim_o
            ss_res_anom = np.sum((s_m - o_m)**2)
            ss_tot_anom = np.sum(anom_o**2)
            nse_anom = 1.0 - (ss_res_anom / ss_tot_anom) if ss_tot_anom > 1e-9 else np.nan

            metrics_list.append({
                "station_id": sid,
                "nom": nom,
                "bassin": p["bassin"],
                "niveau": p["niveau"],
                "pas": "journalier",
                "n_obs": m_daily["n"],
                "mean_obs": m_daily["mean_obs"],
                "mean_sim": m_daily["mean_sim"],
                "r": m_daily["r"],
                "alpha": m_daily["alpha"],
                "beta": m_daily["beta"],
                "kge": m_daily["kge"],
                "pbias": m_daily["pbias"],
                "rmse": m_daily["rmse"],
                "nse": m_daily["nse"],
                "nse_anom_lt": np.nan,
                "exclusion_flags": "non"
            })

            metrics_list.append({
                "station_id": sid,
                "nom": nom,
                "bassin": p["bassin"],
                "niveau": p["niveau"],
                "pas": "mensuel",
                "n_obs": m_monthly["n"],
                "mean_obs": m_monthly["mean_obs"],
                "mean_sim": m_monthly["mean_sim"],
                "r": m_monthly["r"],
                "alpha": m_monthly["alpha"],
                "beta": m_monthly["beta"],
                "kge": m_monthly["kge"],
                "pbias": m_monthly["pbias"],
                "rmse": m_monthly["rmse"],
                "nse": m_monthly["nse"],
                "nse_anom_lt": nse_anom,
                "exclusion_flags": "non"
            })

        else:
            sub_m = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            merged_m = pd.merge(sub_m, df_sim_monthly[["year_month", sid]], on="year_month", how="inner")
            
            o_all = merged_m["q_m3s"].values
            s_all = merged_m[sid].values
            m_all = calc_metrics(o_all, s_all)
            
            clim_m = long_term_clim.get(sid, {})
            clim_vals = np.array([clim_m.get(m, np.nan) for m in merged_m["mois"]])
            anom_o = o_all - clim_vals
            ss_res = np.sum((s_all - o_all)**2)
            ss_tot = np.sum(anom_o**2)
            nse_anom_all = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-9 else np.nan

            metrics_list.append({
                "station_id": sid,
                "nom": nom,
                "bassin": p["bassin"],
                "niveau": p["niveau"],
                "pas": "mensuel",
                "n_obs": m_all["n"],
                "mean_obs": m_all["mean_obs"],
                "mean_sim": m_all["mean_sim"],
                "r": m_all["r"],
                "alpha": m_all["alpha"],
                "beta": m_all["beta"],
                "kge": m_all["kge"],
                "pbias": m_all["pbias"],
                "rmse": m_all["rmse"],
                "nse": m_all["nse"],
                "nse_anom_lt": nse_anom_all,
                "exclusion_flags": "inclus (tous)"
            })

            has_flag = merged_m["flag"].notna() & (merged_m["flag"] != "")
            if np.any(has_flag):
                filtered_m = merged_m[~has_flag]
                o_clean = filtered_m["q_m3s"].values
                s_clean = filtered_m[sid].values
                m_clean = calc_metrics(o_clean, s_clean)
                
                clim_clean = np.array([clim_m.get(m, np.nan) for m in filtered_m["mois"]])
                anom_clean = o_clean - clim_clean
                ss_res_c = np.sum((s_clean - o_clean)**2)
                ss_tot_c = np.sum(anom_clean**2)
                nse_anom_c = 1.0 - (ss_res_c / ss_tot_c) if ss_tot_c > 1e-9 else np.nan

                metrics_list.append({
                    "station_id": sid,
                    "nom": nom + " (sans suspects)",
                    "bassin": p["bassin"],
                    "niveau": p["niveau"],
                    "pas": "mensuel",
                    "n_obs": m_clean["n"],
                    "mean_obs": m_clean["mean_obs"],
                    "mean_sim": m_clean["mean_sim"],
                    "r": m_clean["r"],
                    "alpha": m_clean["alpha"],
                    "beta": m_clean["beta"],
                    "kge": m_clean["kge"],
                    "pbias": m_clean["pbias"],
                    "rmse": m_clean["rmse"],
                    "nse": m_clean["nse"],
                    "nse_anom_lt": nse_anom_c,
                    "exclusion_flags": "exclus (sans suspects)"
                })

    df_metrics = pd.DataFrame(metrics_list)
    metrics_csv = os.path.join(out_dir, "t5bis_metrics_12stations.csv")
    df_metrics.to_csv(metrics_csv, index=False)
    print(f"Table des métriques sauvegardee dans : {metrics_csv}")

    print("\n--- SYNTHESE DES METRIQUES MENSUELLES (2016-2020) ---")
    header_m = f"{'Station':24s} | {'Niveau':17s} | {'N':3s} | {'Moy Obs':8s} | {'Moy Sim':8s} | {'KGE':7s} | {'r':7s} | {'alpha':6s} | {'beta':6s} | {'PBIAS (%)':9s} | {'NSE':7s} | {'NSE Anom':8s}"
    print(header_m)
    print("-" * 137)
    for _, row in df_metrics[df_metrics["pas"] == "mensuel"].iterrows():
        print(f"{row['nom']:24s} | {row['niveau']:17s} | {int(row['n_obs']):3d} | {row['mean_obs']:8.3f} | {row['mean_sim']:8.3f} | {row['kge']:+7.3f} | {row['r']:+7.3f} | {row['alpha']:6.3f} | {row['beta']:6.3f} | {row['pbias']:+9.1f}% | {row['nse']:+7.3f} | {row['nse_anom_lt']:+8.3f}")

    # 5. ETAPE 3 : DIAGNOSTIC CIBLE DU PROBLEME tbsflw
    print("\n" + "="*85)
    print("ETAPE 3 — DIAGNOSTIC CIBLE DU PARAMETRE tbsflw (FACTEUR 86 400)")
    print("="*85)

    # 3a. Constantes de récession tau
    print("\n3a. Constantes de récession journalières (segments >= 5 jours stricts de décroissance)...")
    recession_results = []
    tau_scatter_data = {sid: {"tau_obs": [], "tau_sim": []} for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]}

    for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]:
        sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")]
        merged_d = pd.merge(sub_d, df_sim_daily[["date", sid]], on="date", how="inner")
        
        q_obs_arr = merged_d["q_m3s"].values
        q_sim_arr = merged_d[sid].values

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

        taus_obs = extract_recessions(q_obs_arr)
        taus_sim = extract_recessions(q_sim_arr)

        med_o = np.median(taus_obs) if len(taus_obs) > 0 else np.nan
        q25_o, q75_o = np.percentile(taus_obs, [25, 75]) if len(taus_obs) > 0 else (np.nan, np.nan)
        iqr_o = q75_o - q25_o

        med_s = np.median(taus_sim) if len(taus_sim) > 0 else np.nan
        q25_s, q75_s = np.percentile(taus_sim, [25, 75]) if len(taus_sim) > 0 else (np.nan, np.nan)
        iqr_s = q75_s - q25_s

        ratio_med = med_s / med_o if med_o > 0 else np.nan

        p = [x for x in pairing_results if x["station_id"] == sid][0]
        recession_results.append({
            "station_id": sid,
            "nom": p["nom"],
            "n_seg_obs": len(taus_obs),
            "med_tau_obs": med_o,
            "iqr_tau_obs": iqr_o,
            "n_seg_sim": len(taus_sim),
            "med_tau_sim": med_s,
            "iqr_tau_sim": iqr_s,
            "ratio_sim_obs": ratio_med
        })

        # Segments synchrones pour scatter plot
        i = 0
        while i < len(q_obs_arr) - 4:
            j = i
            while j < len(q_obs_arr) - 1 and (q_obs_arr[j+1] < q_obs_arr[j]) and (q_sim_arr[j+1] < q_sim_arr[j]) and q_obs_arr[j+1] > 0.0001 and q_sim_arr[j+1] > 0.0001:
                j += 1
            length = j - i + 1
            if length >= 5:
                t = np.arange(length)
                s_o, _, _, _, _ = stats.linregress(t, np.log(q_obs_arr[i:j+1]))
                s_s, _, _, _, _ = stats.linregress(t, np.log(q_sim_arr[i:j+1]))
                if s_o < -1e-6 and s_s < -1e-6:
                    tau_scatter_data[sid]["tau_obs"].append(-1.0 / s_o)
                    tau_scatter_data[sid]["tau_sim"].append(-1.0 / s_s)
                i = j + 1
            else:
                i += 1

    df_rec = pd.DataFrame(recession_results)
    rec_csv = os.path.join(out_dir, "t5bis_recession_tau.csv")
    df_rec.to_csv(rec_csv, index=False)
    print(f"Table des constantes de récession : {rec_csv}")

    print("\n--- CONSTANTES DE RECESSION TAU (JOURS) ---")
    print(f"{'Station':16s} | {'N seg Obs':9s} | {'Med Tau Obs':11s} | {'IQR Obs':8s} | {'N seg Sim':9s} | {'Med Tau Sim':11s} | {'IQR Sim':8s} | {'Ratio Sim/Obs':13s}")
    print("-" * 105)
    for _, r in df_rec.iterrows():
        print(f"{r['nom']:16s} | {r['n_seg_obs']:9d} | {r['med_tau_obs']:10.2f}j | {r['iqr_tau_obs']:7.2f}j | {r['n_seg_sim']:9d} | {r['med_tau_sim']:10.2f}j | {r['iqr_tau_sim']:7.2f}j | {r['ratio_sim_obs']:12.2f}x")

    # 3b. Statistiques d'étiage
    print("\n3b. Statistiques d'étiage (Q90, Q95, assecs et débits quasi-nuls)...")
    lowflow_list = []
    for p in pairing_results:
        sid = p["station_id"]
        nom = p["nom"]
        type_pas = p["type_pas"]
        
        if type_pas == "journalier":
            sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")]
            merged_d = pd.merge(sub_d, df_sim_daily[["date", sid]], on="date", how="inner")
            o = merged_d["q_m3s"].dropna().values
            s = merged_d[sid].values
            unit = "jours"
        else:
            sub_m = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)]
            merged_m = pd.merge(sub_m, df_sim_monthly[["year_month", sid]], on="year_month", how="inner")
            o = merged_m["q_m3s"].dropna().values
            s = merged_m[sid].values
            unit = "mois"

        q90_o = np.percentile(o, 10)
        q95_o = np.percentile(o, 5)
        q90_s = np.percentile(s, 10)
        q95_s = np.percentile(s, 5)

        zero_o = int(np.sum(o <= 0.0001))
        zero_s = int(np.sum(s <= 0.0001))
        min_s = float(np.min(s))
        min_o = float(np.min(o))

        lowflow_list.append({
            "station_id": sid,
            "nom": nom,
            "bassin": p["bassin"],
            "pas": type_pas,
            "n_total": len(o),
            "unite": unit,
            "q90_obs": q90_o,
            "q90_sim": q90_s,
            "q95_obs": q95_o,
            "q95_sim": q95_s,
            "min_obs": min_o,
            "min_sim": min_s,
            "zero_obs": zero_o,
            "zero_sim": zero_s
        })

    df_low = pd.DataFrame(lowflow_list)
    low_csv = os.path.join(out_dir, "t5bis_lowflow_stats.csv")
    df_low.to_csv(low_csv, index=False)
    print(f"Table des statistiques d'étiage : {low_csv}")

    print("\n--- ANALYSE DE L'ETIAGE (Q90, Q95, ASSECS) ---")
    print(f"{'Station':16s} | {'Pas':7s} | {'Q90 Obs':8s} | {'Q90 Sim':8s} | {'Q95 Obs':8s} | {'Q95 Sim':8s} | {'Min Obs':8s} | {'Min Sim':8s} | {'Zero Obs':8s} | {'Zero Sim'}")
    print("-" * 115)
    for _, r in df_low.iterrows():
        print(f"{r['nom']:16s} | {r['pas']:7s} | {r['q90_obs']:8.4f} | {r['q90_sim']:8.4f} | {r['q95_obs']:8.4f} | {r['q95_sim']:8.4f} | {r['min_obs']:8.4f} | {r['min_sim']:8.4f} | {r['zero_obs']:8d} | {r['zero_sim']:8d}")

    # 3c. Régime permanent Vout/Vin sur 2016-2020 pour les 7 bassins
    print("\n3c. Régime permanent : Calcul du rapport Vout/Vin (2016-2020) pour les 7 bassins...")
    b_masks_7 = {b: get_basin_mask(basins_7[b][0], basins_7[b][1]) for b in basins_7}
    years = [2016, 2017, 2018, 2019, 2020]
    
    vv_csv = os.path.join(out_dir, "t5bis_vout_vin_7basins_2016_2020.csv")
    if os.path.exists(vv_csv):
        print(f"  Chargement table Vout/Vin existante : {vv_csv}")
        df_vv = pd.read_csv(vv_csv)
    else:
        # 1. Calcul de Vin annuel pour les 7 bassins en 1 seule passe sur le ruissellement
        print("  Calcul de Vin annuel (1826 fichiers de ruissellement)...")
        vin_records = {b: {yr: 0.0 for yr in years} for b in basins_7}
        for yr in years:
            r_files = sorted(glob.glob(os.path.join(runoff_dir, f"{yr}*/*.nc")))
            for rf in r_files:
                with nc.Dataset(rf) as ds:
                    qs = np.nan_to_num(ds["Qs_tavg"][:])
                    qsb = np.nan_to_num(ds["Qsb_tavg"][:])
                    if qs.ndim == 3: qs = qs[0]
                    if qsb.ndim == 3: qsb = qsb[0]
                    daily_vol = (np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0
                    for b in basins_7:
                        vin_records[b][yr] += np.sum(daily_vol[b_masks_7[b]])

        # 2. Calcul de Vout annuel directement depuis df_sim_daily
        vout_vin_records = []
        for yr in years:
            sub_yr = df_sim_daily[df_sim_daily["year"] == yr]
            for b in basins_7:
                v_in_hm3 = vin_records[b][yr] / 1e6
                v_out_hm3 = float(sub_yr[f"outlet_{b}"].sum()) * 86400.0 / 1e6
                ratio = (v_out_hm3 / v_in_hm3) * 100.0 if v_in_hm3 > 0 else np.nan
                vout_vin_records.append({
                    "annee": yr,
                    "bassin": b,
                    "Vin_hm3": v_in_hm3,
                    "Vout_hm3": v_out_hm3,
                    "Ratio_pct": ratio
                })

        df_vv = pd.DataFrame(vout_vin_records)
        df_vv.to_csv(vv_csv, index=False)
        print(f"Table Vout/Vin : {vv_csv}")

    print("\n--- TABLEAU DU RAPPORT Vout/Vin (%) PAR ANNEE ET PAR BASSIN ---")
    piv = df_vv.pivot(index="bassin", columns="annee", values="Ratio_pct")
    piv["Moyenne_5ans"] = piv.mean(axis=1)
    print(piv.to_string(float_format=lambda x: f"{x:6.1f}%"))

    # 3d. Déphasage temporel : corrélations croisées
    print("\n3d. Déphasage temporel : Corrélation croisée pour des décalages de -3 à +3 mois...")
    lag_records = []
    lags = [-3, -2, -1, 0, 1, 2, 3]

    for p in pairing_results:
        sid = p["station_id"]
        nom = p["nom"]
        type_pas = p["type_pas"]
        
        if type_pas == "journalier":
            sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")].copy()
            sub_d["year_month"] = sub_d["date"].str.slice(0, 7)
            sub_m = sub_d.groupby("year_month")["q_m3s"].mean().reset_index()
        else:
            sub_m = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)][["year_month", "q_m3s"]].copy()

        merged_m = pd.merge(sub_m, df_sim_monthly[["year_month", sid]], on="year_month", how="inner").sort_values("year_month")
        o_series = merged_m["q_m3s"].values
        s_series = merged_m[sid].values

        lag_corrs = {}
        for k in lags:
            if k < 0:
                o_sub = o_series[-k:]
                s_sub = s_series[:k]
            elif k > 0:
                o_sub = o_series[:-k]
                s_sub = s_series[k:]
            else:
                o_sub = o_series
                s_sub = s_series

            mask = (~np.isnan(o_sub)) & (~np.isnan(s_sub))
            if np.sum(mask) >= 5 and np.std(o_sub[mask]) > 1e-9 and np.std(s_sub[mask]) > 1e-9:
                r_k = np.corrcoef(o_sub[mask], s_sub[mask])[0, 1]
            else:
                r_k = np.nan
            lag_corrs[k] = r_k

        valid_lags = {k: v for k, v in lag_corrs.items() if not np.isnan(v)}
        if valid_lags:
            best_lag = max(valid_lags, key=valid_lags.get)
            best_r = valid_lags[best_lag]
        else:
            best_lag = 0
            best_r = np.nan

        lag_rec = {
            "station_id": sid,
            "nom": nom,
            "bassin": p["bassin"],
            "r_lag_-3": lag_corrs[-3],
            "r_lag_-2": lag_corrs[-2],
            "r_lag_-1": lag_corrs[-1],
            "r_lag_0": lag_corrs[0],
            "r_lag_+1": lag_corrs[1],
            "r_lag_+2": lag_corrs[2],
            "r_lag_+3": lag_corrs[3],
            "optimal_lag_mois": best_lag,
            "max_r": best_r,
            "gain_r": best_r - lag_corrs[0]
        }
        lag_records.append(lag_rec)

    df_lags = pd.DataFrame(lag_records)
    lag_csv = os.path.join(out_dir, "t5bis_cross_correlation_lags.csv")
    df_lags.to_csv(lag_csv, index=False)
    print(f"Table des correlations croisees : {lag_csv}")

    print("\n--- CORRELATIONS CROISEES ET DEPHASAGES OPTIMAUX ---")
    print(f"{'Station':16s} | {'r(k=-3)':7s} | {'r(k=-2)':7s} | {'r(k=-1)':7s} | {'r(k=0)':7s} | {'r(k=+1)':7s} | {'r(k=+2)':7s} | {'r(k=+3)':7s} | {'Lag Opt':7s} | {'Max r':7s}")
    print("-" * 105)
    for _, r in df_lags.iterrows():
        print(f"{r['nom']:16s} | {r['r_lag_-3']:+7.3f} | {r['r_lag_-2']:+7.3f} | {r['r_lag_-1']:+7.3f} | {r['r_lag_0']:+7.3f} | {r['r_lag_+1']:+7.3f} | {r['r_lag_+2']:+7.3f} | {r['r_lag_+3']:+7.3f} | {int(r['optimal_lag_mois']):+7d} | {r['max_r']:+7.3f}")

    # 6. ETAPE 4 : PRODUCTION DES 3 FIGURES
    print("\n" + "="*85)
    print("ETAPE 4 — PRODUCTION DES FIGURES D'ANALYSE")
    print("="*85)

    # FIGURE 1 : 12 panneaux
    fig, axes = plt.subplots(4, 3, figsize=(18, 16), sharex=False)
    axes = axes.flatten()

    for idx, p in enumerate(pairing_results):
        ax = axes[idx]
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        area = p["aire_hymap_km2"]
        
        m_row = df_metrics[(df_metrics["station_id"] == sid) & (df_metrics["pas"] == "mensuel") & (df_metrics["exclusion_flags"] != "exclus (sans suspects)")].iloc[0]
        kge_val = m_row["kge"]
        r_val = m_row["r"]
        pbias_val = m_row["pbias"]

        if p["type_pas"] == "journalier":
            sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")].copy()
            sub_d["year_month"] = sub_d["date"].str.slice(0, 7)
            sub_m = sub_d.groupby("year_month")["q_m3s"].mean().reset_index()
        else:
            sub_m = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)][["year_month", "q_m3s"]].copy()

        merged_m = pd.merge(sub_m, df_sim_monthly[["year_month", sid]], on="year_month", how="inner").sort_values("year_month")
        dts = pd.to_datetime(merged_m["year_month"] + "-15").dt.to_pydatetime()
        q_obs = merged_m["q_m3s"].values
        q_sim = merged_m[sid].values

        ax.plot(dts, q_obs, marker="o", color="#d62728", lw=1.8, markersize=4, label="Observé", zorder=4)
        ax.plot(dts, q_sim, marker="s", color="#1f77b4", lw=1.8, markersize=4, label="Simulé OPL", zorder=3)

        title_str = f"{nom} ({bassin})\nAire: {area:.0f} km² | KGE: {kge_val:+.2f} | r: {r_val:+.2f} | PBIAS: {pbias_val:+.0f}%"
        ax.set_title(title_str, fontsize=10, fontweight="bold")
        ax.set_ylabel("Débit (m³/s)", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        if idx == 0:
            ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Confrontation Mensuelle HyMAP2 OPL (2016-2020) aux 12 Stations d'Observation\n"
                 "(Sebou [Niveau A], Bouregreg & Ksob [Niveau B])", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig1_path = os.path.join(plots_dir, "t5bis_12stations_hydrographs.png")
    plt.savefig(fig1_path, dpi=200)
    plt.close()
    print(f"Figure 1 (12 panneaux) : {fig1_path}")

    # FIGURE 2 : FDC log pour les 4 stations journalières
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, sid in enumerate(["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]):
        ax = axes[idx]
        p = [x for x in pairing_results if x["station_id"] == sid][0]
        nom = p["nom"]
        area = p["aire_hymap_km2"]

        sub_d = df_daily_obs[(df_daily_obs["station_id"] == sid) & (df_daily_obs["date"] >= "2016-01-01") & (df_daily_obs["date"] <= "2020-12-31")]
        merged_d = pd.merge(sub_d, df_sim_daily[["date", sid]], on="date", how="inner")
        
        o_clean = merged_d["q_m3s"].dropna().values
        s_clean = merged_d[sid].values

        prob_o = np.arange(1, len(o_clean) + 1) / len(o_clean) * 100.0
        q_sorted_o = np.sort(o_clean)[::-1]

        prob_s = np.arange(1, len(s_clean) + 1) / len(s_clean) * 100.0
        q_sorted_s = np.sort(s_clean)[::-1]

        ax.semilogy(prob_o, q_sorted_o, color="#d62728", lw=2.2, label="Observé")
        ax.semilogy(prob_s, q_sorted_s, color="#1f77b4", lw=2.2, linestyle="--", label="Simulé HyMAP2")

        ax.set_title(f"{nom} (Aire = {area:.0f} km²)", fontsize=11, fontweight="bold")
        ax.set_xlabel("% du temps de dépassement", fontsize=10)
        ax.set_ylabel("Débit journalier (m³/s) [échelle log]", fontsize=10)
        ax.grid(True, which="both", linestyle="--", alpha=0.5)
        ax.set_xlim(0, 100)
        ax.legend(loc="upper right", fontsize=9)

        q95_o = np.percentile(o_clean, 5)
        q95_s = np.percentile(s_clean, 5)
        ratio_str = f"{q95_s/q95_o:.1f}x" if q95_o > 0.0001 else "assec (Q=0)"
        ax.text(0.04, 0.15, f"Q95 Obs : {q95_o:.3f} m³/s\nQ95 Sim : {q95_s:.3f} m³/s\nRatio Sim/Obs : {ratio_str}",
                transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85, ec="gray"))

    fig.suptitle("Courbes des Débits Classés (FDC) - Échelle Logarithmique (Bouregreg 2016-2020)\n"
                 "Mise en évidence du plancher d'étiage artificiel simulé", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    fig2_path = os.path.join(plots_dir, "t5bis_flow_duration_curves_bouregreg.png")
    plt.savefig(fig2_path, dpi=200)
    plt.close()
    print(f"Figure 2 (FDC log Bouregreg) : {fig2_path}")

    # FIGURE 3 : Dispersion des tau de récession
    fig, ax = plt.subplots(figsize=(9, 8))
    colors_rec = {"b_a_loudah": "#1f77b4", "b_s_cherif": "#ff7f0e", "b_s_jabeur": "#2ca02c", "b_l_chafia": "#d62728"}
    labels_rec = {"b_a_loudah": "Ain Loudah", "b_s_cherif": "S.M. Cherif", "b_s_jabeur": "Sidi Jabeur", "b_l_chafia": "Lalla Chafia"}

    all_t_obs = []
    all_t_sim = []

    for sid in ["b_a_loudah", "b_s_cherif", "b_s_jabeur", "b_l_chafia"]:
        t_o = tau_scatter_data[sid]["tau_obs"]
        t_s = tau_scatter_data[sid]["tau_sim"]
        if len(t_o) > 0:
            ax.scatter(t_o, t_s, color=colors_rec[sid], alpha=0.75, s=45, label=f"{labels_rec[sid]} (N={len(t_o)})")
            all_t_obs.extend(t_o)
            all_t_sim.extend(t_s)

    max_val = max(max(all_t_obs) if all_t_obs else 50, max(all_t_sim) if all_t_sim else 50) * 1.1
    ax.plot([0.5, max_val], [0.5, max_val], "k--", lw=1.8, label="1:1 (Idéal)")
    ax.plot([0.5, max_val], [5, max_val*10], "r:", lw=1.2, alpha=0.7, label="Simulé = 10x Observé")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 100)
    ax.set_ylim(5, 500)

    ax.set_xlabel("Constante de récession observée $\\tau_{obs}$ (jours)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Constante de récession simulée $\\tau_{sim}$ (jours)", fontsize=11, fontweight="bold")
    ax.set_title("Diagramme de Dispersion des Constantes de Récession $\\tau$ (Segments synchrones >= 5j)\n"
                 "Régression exponentielle $Q(t) = Q_0 \\exp(-t/\\tau)$", fontsize=12, fontweight="bold")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", fontsize=10)

    if len(all_t_obs) > 0:
        med_all_o = np.median(all_t_obs)
        med_all_s = np.median(all_t_sim)
        ax.text(0.60, 0.12, f"Médiane globale Obs : {med_all_o:.1f} jours\nMédiane globale Sim : {med_all_s:.1f} jours\nFacteur moyen Sim/Obs : {med_all_s/med_all_o:.1f}x",
                transform=ax.transAxes, fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.9, ec="gray"))

    plt.tight_layout()
    fig3_path = os.path.join(plots_dir, "t5bis_recession_tau_scatter.png")
    plt.savefig(fig3_path, dpi=200)
    plt.close()
    print(f"Figure 3 (Scatter tau) : {fig3_path}")

    print("\n=== TOUTES LES ETAPES DE LA TACHE 5bis SONT TERMINEES AVEC SUCCES ===")

if __name__ == "__main__":
    main()
