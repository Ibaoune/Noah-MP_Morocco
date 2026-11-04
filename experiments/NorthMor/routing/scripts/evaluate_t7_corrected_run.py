#!/usr/bin/env python3
"""
evaluate_t7_corrected_run.py
Tâche 7 - Etape 3 :
Evaluation complète de la simulation corrigée OPL 2016-2020 et comparaison avant/après :
1. Critère de stabilisation du spin-up (< 1 %).
2. Niveau de stabilisation et pente de BSFSTO.
3. Ratios Vsim/Vin sur les 12 bassins (se rapprochent-ils de 1 ?).
4. Assecs et régimes d'étiage à Sidi Jabeur et Adamna.
5. Fermeture du bilan de masse (< 0.2 %).
6. Métriques comparatives avant/après (KGE, r, alpha, beta, PBIAS) aux 12 stations.
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy.stats import linregress, pearsonr

def main():
    base_dir = "experiments/NorthMor/routing"
    clean_dir = "data/streamflow_clean"
    ldt_path = os.path.join(base_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    pairing_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_stations_pairing.csv")
    t5bis_metrics_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_metrics_12stations.csv")
    t6_decomp_csv = os.path.join(base_dir, "output/OPL_2016_2020/t6_three_volumes_decomposition.csv")
    
    # Chemins des runs
    sp1_rst = os.path.join(base_dir, "output/OPL_spinup_c1_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc")
    sp2_rst = os.path.join(base_dir, "output/OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc")
    corr_routing_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee/ROUTING")
    out_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 90)
    print("EVALUATION DE LA SIMULATION CORRIGEE HYMAP2 (TACHE 7 - ETAPE 3)")
    print("=" * 90)

    # -------------------------------------------------------------------------
    # 1. CRITERE DE STABILISATION DU SPIN-UP
    # -------------------------------------------------------------------------
    print("\n1. CRITERE DE STABILISATION DU SPIN-UP (CYCLE 1 VS CYCLE 2)")
    print("-" * 65)
    def read_rst_stocks(rst_file):
        with nc.Dataset(rst_file, 'r') as ds:
            bsf = np.sum(np.maximum(ds['BSFSTO'][:], 0.0)) / 1e6
            rnf = np.sum(np.maximum(ds['RNFSTO'][:], 0.0)) / 1e6
            riv = np.sum(np.maximum(ds['RIVSTO'][:], 0.0)) / 1e6
            fld = np.sum(np.maximum(ds['FLDSTO'][:], 0.0)) / 1e6
            return {"bsf": bsf, "rnf": rnf, "riv": riv, "fld": fld, "tot": bsf+rnf+riv+fld}

    stocks_c1 = read_rst_stocks(sp1_rst)
    stocks_c2 = read_rst_stocks(sp2_rst)
    d_bsf = stocks_c2["bsf"] - stocks_c1["bsf"]
    d_bsf_rel = abs(d_bsf) / stocks_c1["bsf"] * 100.0
    d_tot = stocks_c2["tot"] - stocks_c1["tot"]
    d_tot_rel = abs(d_tot) / stocks_c1["tot"] * 100.0

    print(f"Cycle 1 (Fin 2016) : BSFSTO = {stocks_c1['bsf']:8.2f} hm3 | Total = {stocks_c1['tot']:8.2f} hm3")
    print(f"Cycle 2 (Fin 2016) : BSFSTO = {stocks_c2['bsf']:8.2f} hm3 | Total = {stocks_c2['tot']:8.2f} hm3")
    print(f"Ecart nappe Cycle 2 vs Cycle 1 : {d_bsf:+8.2f} hm3 ({d_bsf_rel:.4f} %)")
    print(f"Ecart total Cycle 2 vs Cycle 1 : {d_tot:+8.2f} hm3 ({d_tot_rel:.4f} %)")
    criterion_pass = d_bsf_rel < 1.0
    print(f"Critère de stabilisation < 1 % : {'VALIDE' if criterion_pass else 'ECHEC'}")

    # -------------------------------------------------------------------------
    # 2. DYNAMIQUE DE BSFSTO SUR 2016-2020 CORRIGEE
    # -------------------------------------------------------------------------
    print("\n2. DYNAMIQUE ET STABILISATION DE BSFSTO SUR 5 ANS (2016-2020)")
    print("-" * 65)
    hist_files = sorted(glob.glob(os.path.join(corr_routing_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))
    print(f"Nombre de fichiers LIS_HIST corriges trouves : {len(hist_files)}")
    assert len(hist_files) == 1827, f"Attendu 1827 fichiers, trouve {len(hist_files)}"

    daily_stocks = []
    df_p = pd.read_csv(pairing_csv)

    # Reconstituer l'arborescence pour extraire débits aux stations
    qsim_records = []

    for idx, fpath in enumerate(hist_files):
        with nc.Dataset(fpath) as ds:
            t_units = ds["time"].units
            t_val = ds["time"][0]
            base_str = t_units.replace("minutes since ", "")
            base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
            file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
            sim_dt = file_dt - datetime.timedelta(days=1)
            sim_date_str = sim_dt.strftime("%Y-%m-%d")

            riv = np.sum(np.maximum(np.nan_to_num(ds["RiverStor_tavg"][:]), 0.0)) / 1e6
            fld = np.sum(np.maximum(np.nan_to_num(ds["FloodStor_tavg"][:]), 0.0)) / 1e6
            rnf = np.sum(np.maximum(np.nan_to_num(ds["RunoffStor_tavg"][:]), 0.0)) / 1e6
            bsf = np.sum(np.maximum(np.nan_to_num(ds["BaseflowStor_tavg"][:]), 0.0)) / 1e6

            daily_stocks.append({
                "date": sim_date_str,
                "RIVSTO_hm3": riv,
                "FLDSTO_hm3": fld,
                "RNFSTO_hm3": rnf,
                "BSFSTO_hm3": bsf,
                "TOTAL_hm3": riv + fld + rnf + bsf
            })

            flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if flow.ndim == 3: flow = flow[0]
            q_row = {"date": sim_date_str}
            for _, p in df_p.iterrows():
                sid = p["station_id"]
                r, c = int(p["row_hymap"]), int(p["col_hymap"])
                q_row[sid] = float(flow[r, c])
            qsim_records.append(q_row)

        if (idx + 1) % 365 == 0:
            print(f"  Extraction : {idx + 1}/{len(hist_files)} jours...")

    df_stocks_corr = pd.DataFrame(daily_stocks)
    df_stocks_corr.to_csv(os.path.join(out_dir, "t7_domain_storages_daily_corrigee.csv"), index=False)
    
    df_qsim_corr = pd.DataFrame(qsim_records).sort_values("date").reset_index(drop=True)
    df_qsim_corr.to_csv(os.path.join(out_dir, "t7_sim_daily_12stations_corrigee.csv"), index=False)

    # Pente annuelle BSFSTO corrigée
    t_days = np.arange(len(df_stocks_corr))
    reg_bsf = linregress(t_days, df_stocks_corr["BSFSTO_hm3"].to_numpy())
    slope_bsf_corr = reg_bsf.slope * 365.25
    bsf_mean_corr = df_stocks_corr["BSFSTO_hm3"].mean()
    bsf_start_corr = df_stocks_corr["BSFSTO_hm3"].iloc[0]
    bsf_end_corr = df_stocks_corr["BSFSTO_hm3"].iloc[-1]

    print(f"Stock nappe debut (2016-01-01) : {bsf_start_corr:.2f} hm3")
    print(f"Stock nappe fin   (2020-12-31) : {bsf_end_corr:.2f} hm3")
    print(f"Niveau moyen de stabilisation  : {bsf_mean_corr:.2f} hm3 (vs 14 000+ hm3 avant)")
    print(f"Pente annuelle BSFSTO          : {slope_bsf_corr:+.2f} hm3/an (vs +3677 hm3/an avant)")
    print(f"R2 de tendance linéaire        : {reg_bsf.rvalue**2:.4f}")

    # -------------------------------------------------------------------------
    # 3. RATIOS Vsim/Vin SUR LES 12 BASSINS
    # -------------------------------------------------------------------------
    print("\n3. RATIOS Vsim/Vin SUR LES 12 BASSINS (AVANT VS APRES)")
    print("-" * 65)
    df_t6 = pd.read_csv(t6_decomp_csv)
    df_t6_5y = df_t6[df_t6["periode"] == "2016-2020"].set_index("station_id")

    vsim_records = []
    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        vin_5y = df_t6_5y.loc[sid, "Vin_hm3"]
        vobs_5y = df_t6_5y.loc[sid, "Vobs_hm3"]
        vsim_avant = df_t6_5y.loc[sid, "Vsim_hm3"]
        vsim_sur_vin_avant = df_t6_5y.loc[sid, "Vsim_sur_Vin"]

        # Nouveau Vsim corrigé (m3/s -> hm3)
        vsim_corr_hm3 = float(np.sum(df_qsim_corr[sid].to_numpy()) * 86400.0 / 1e6)
        vsim_sur_vin_corr = vsim_corr_hm3 / vin_5y if vin_5y > 0 else 0.0

        vsim_records.append({
            "station_id": sid,
            "nom": nom,
            "bassin": bassin,
            "Vin_hm3": vin_5y,
            "Vsim_avant_hm3": vsim_avant,
            "Vsim_corr_hm3": vsim_corr_hm3,
            "Vsim_sur_Vin_avant": vsim_sur_vin_avant,
            "Vsim_sur_Vin_corr": vsim_sur_vin_corr
        })

    df_vsim_comp = pd.DataFrame(vsim_records)
    print(f"{'Station':16s} | {'Bassin':10s} | {'Vin (hm3)':10s} | {'Vsim Av':10s} | {'Vsim Corr':10s} | {'Vsim/Vin Av':12s} | {'Vsim/Vin Corr':13s}")
    print("-" * 92)
    for _, r in df_vsim_comp.iterrows():
        print(f"{r['nom']:16s} | {r['bassin']:10s} | {r['Vin_hm3']:10.1f} | {r['Vsim_avant_hm3']:10.1f} | {r['Vsim_corr_hm3']:10.1f} | {r['Vsim_sur_Vin_avant']*100:10.1f} % | {r['Vsim_sur_Vin_corr']*100:11.1f} %")
    print("=" * 92)

    # -------------------------------------------------------------------------
    # 4. COMPORTEMENT A L'ETIAGE : ASSECS A SIDI JABEUR ET ADAMNA
    # -------------------------------------------------------------------------
    print("\n4. COMPORTEMENT A L'ETIAGE : ASSECS A SIDI JABEUR ET ADAMNA")
    print("-" * 65)
    # Sidi Jabeur journalier
    q_sj_corr = df_qsim_corr["b_s_jabeur"].to_numpy()
    # Comparaison avec run avant
    df_qsim_avant = pd.read_csv(os.path.join(base_dir, "output/OPL_2016_2020/t6_sim_daily_12stations.csv"))
    q_sj_avant = df_qsim_avant["b_s_jabeur"].to_numpy()
    
    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_sj_obs = df_obs_daily[df_obs_daily["station_id"] == "b_s_jabeur"].dropna(subset=["discharge_m3s"])
    q_sj_obs = df_sj_obs["discharge_m3s"].to_numpy()

    print("Sidi Jabeur (Oued Grou, journalier) :")
    print(f"  Observed  : Min={q_sj_obs.min():.3f} m3/s | Q90={np.percentile(q_sj_obs, 10):.3f} m3/s | Nb assecs (Q=0)={np.sum(q_sj_obs == 0)} jours ({np.sum(q_sj_obs == 0)/len(q_sj_obs)*100:.1f} %)")
    print(f"  Run Avant : Min={q_sj_avant.min():.3f} m3/s | Q90={np.percentile(q_sj_avant, 10):.3f} m3/s | Nb assecs (Q=0)={np.sum(q_sj_avant == 0)} jours (Plancher artificiel)")
    print(f"  Run Corr  : Min={q_sj_corr.min():.3f} m3/s | Q90={np.percentile(q_sj_corr, 10):.3f} m3/s | Nb assecs (Q<0.01)={np.sum(q_sj_corr < 0.01)} jours")

    # Adamna mensuel
    df_qsim_corr["month"] = pd.to_datetime(df_qsim_corr["date"]).dt.to_period("M").astype(str)
    q_adamna_m_corr = df_qsim_corr.groupby("month")["adamna"].mean()
    df_qsim_avant["month"] = pd.to_datetime(df_qsim_avant["date"]).dt.to_period("M").astype(str)
    q_adamna_m_avant = df_qsim_avant.groupby("month")["adamna"].mean()

    df_obs_m = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_adamna_obs = df_obs_m[df_obs_m["station_id"] == "adamna"].dropna(subset=["discharge_m3s"])
    
    print("\nAdamna (Oued Ksob, mensuel) :")
    print(f"  Observed  : Min={df_adamna_obs['discharge_m3s'].min():.3f} m3/s | Mediane={df_adamna_obs['discharge_m3s'].median():.3f} m3/s")
    print(f"  Run Avant : Min={q_adamna_m_avant.min():.3f} m3/s | Mediane={q_adamna_m_avant.median():.3f} m3/s")
    print(f"  Run Corr  : Min={q_adamna_m_corr.min():.3f} m3/s | Mediane={q_adamna_m_corr.median():.3f} m3/s")

    # -------------------------------------------------------------------------
    # 5. FERMETURE DU BILAN DE MASSE (RUN CORRIGE 2018 ET 5 ANS)
    # -------------------------------------------------------------------------
    print("\n5. FERMETURE DU BILAN DE MASSE (RUN CORRIGE)")
    print("-" * 65)
    # RST 20171231 et 20181231
    rst_201712 = os.path.join(corr_routing_dir, "201712/LIS_RST_HYMAP2_router_201712312345.d01.nc")
    rst_201812 = os.path.join(corr_routing_dir, "201812/LIS_RST_HYMAP2_router_201812312345.d01.nc")
    s_2017 = read_rst_stocks(rst_201712)["tot"]
    s_2018 = read_rst_stocks(rst_201812)["tot"]
    delta_s_2018_hm3 = s_2018 - s_2017

    # Vin 2018 total domaine
    # Somme sur toutes les mailles de Qs + Qsb
    runoff_dir = os.path.join(base_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL")
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
    ds_ldt.close()

    rfiles_2018 = sorted(glob.glob(os.path.join(runoff_dir, "2018*/*.nc")))
    vin_domain_2018_hm3 = 0.0
    for rf in rfiles_2018:
        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds["Qs_tavg"][:])
            qsb = np.nan_to_num(ds["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]
            vin_domain_2018_hm3 += float(np.sum((np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0 / 1e6))

    # Vout exutoires mer 2018
    # Les exutoires marins sont les mailles terminales
    hfiles_2018 = sorted(glob.glob(os.path.join(corr_routing_dir, "2018*/LIS_HIST_*.d01.nc")))
    ds_ldt = nc.Dataset(ldt_path)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    R, C = flow_x.shape
    ds_ldt.close()

    # Mailles exutoires (flow vers l'exterieur ou -9999 ou mer)
    outlet_mask = np.zeros((R, C), dtype=bool)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx = int(round(flow_x[r, c]))
                vy = int(round(flow_y[r, c]))
                if vx < 1 or vx > C or vy < 1 or vy > R or (vx-1 == c and vy-1 == r):
                    outlet_mask[r, c] = True

    vout_domain_2018_hm3 = 0.0
    for hf in hfiles_2018:
        with nc.Dataset(hf) as ds:
            fl = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if fl.ndim == 3: fl = fl[0]
            vout_domain_2018_hm3 += float(np.sum(fl[outlet_mask]) * 86400.0 / 1e6)

    bilan_sum = vout_domain_2018_hm3 + delta_s_2018_hm3
    ecart_hm3 = vin_domain_2018_hm3 - bilan_sum
    err_bilan_pct = abs(ecart_hm3) / vin_domain_2018_hm3 * 100.0

    print(f"Bilan de masse 2018 (Domaine complet) :")
    print(f"  Vin total     : {vin_domain_2018_hm3:10.2f} hm3")
    print(f"  Vout exutoires: {vout_domain_2018_hm3:10.2f} hm3")
    print(f"  Delta S       : {delta_s_2018_hm3:+10.2f} hm3")
    print(f"  Vout + Delta S: {bilan_sum:10.2f} hm3")
    print(f"  Ecart résiduel: {ecart_hm3:+10.3f} hm3 ({err_bilan_pct:.4f} %)")
    print(f"Fermeture du bilan < 0.2 % : {'VALIDE' if err_bilan_pct < 0.2 else 'ECHEC'}")

    # -------------------------------------------------------------------------
    # 6. TABLEAU COMPARATIF COMPLET DES METRIQUES AVANT / APRES (12 STATIONS)
    # -------------------------------------------------------------------------
    print("\n6. TABLEAU COMPARATIF COMPLET DES METRIQUES AVANT / APRES (12 STATIONS)")
    print("-" * 65)

    df_metrics_avant = pd.read_csv(t5bis_metrics_csv).set_index("station_id")
    comp_records = []

    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        pas = p["pas_de_temps"]

        m_av = df_metrics_avant.loc[sid]

        if pas == "journalier":
            df_st_obs = df_obs_daily[df_obs_daily["station_id"] == sid].dropna(subset=["discharge_m3s"]).copy()
            df_st_obs["date"] = df_st_obs["date"].astype(str)
            df_merged = pd.merge(df_st_obs, df_qsim_corr[["date", sid]], on="date", how="inner")
            y_obs = df_merged["discharge_m3s"].to_numpy()
            y_sim = df_merged[sid].to_numpy()
        else:
            df_st_obs = df_obs_m[df_obs_m["station_id"] == sid].dropna(subset=["discharge_m3s"]).copy()
            df_st_obs["month"] = df_st_obs["month"].astype(str)
            
            # Agréger qsim mensuel
            df_q_m = df_qsim_corr.groupby("month")[sid].mean().reset_index()
            df_merged = pd.merge(df_st_obs, df_q_m, on="month", how="inner")
            y_obs = df_merged["discharge_m3s"].to_numpy()
            y_sim = df_merged[sid].to_numpy()

        # Calcul métriques corrigées
        r_val, _ = pearsonr(y_obs, y_sim) if len(y_obs) > 2 else (np.nan, np.nan)
        mean_obs = np.mean(y_obs)
        mean_sim = np.mean(y_sim)
        std_obs = np.std(y_obs, ddof=1) if len(y_obs) > 1 else np.nan
        std_sim = np.std(y_sim, ddof=1) if len(y_sim) > 1 else np.nan

        alpha_val = std_sim / std_obs if (std_obs > 0 and not np.isnan(std_obs)) else np.nan
        beta_val = mean_sim / mean_obs if mean_obs > 0 else np.nan
        pbias_val = float(np.sum(y_sim - y_obs) / np.sum(y_obs) * 100.0) if np.sum(y_obs) > 0 else np.nan
        kge_val = 1.0 - np.sqrt((r_val - 1.0)**2 + (alpha_val - 1.0)**2 + (beta_val - 1.0)**2)

        comp_records.append({
            "station_id": sid,
            "nom": nom,
            "bassin": bassin,
            "pas": pas,
            "KGE_avant": m_av["KGE"],
            "KGE_apres": kge_val,
            "r_avant": m_av["r_pearson"],
            "r_apres": r_val,
            "alpha_avant": m_av["alpha"],
            "alpha_apres": alpha_val,
            "beta_avant": m_av["beta"],
            "beta_apres": beta_val,
            "PBIAS_avant": m_av["PBIAS_pct"],
            "PBIAS_apres": pbias_val
        })

    df_comp = pd.DataFrame(comp_records)
    comp_csv = os.path.join(out_dir, "t7_metrics_before_after_comparison.csv")
    df_comp.to_csv(comp_csv, index=False)
    print(f"Table comparative avant/après sauvegardee dans : {comp_csv}")

    print("\n" + "=" * 125)
    print(f"{'Station':16s} | {'KGE Av':8s} | {'KGE Ap':8s} | {'r Av':6s} | {'r Ap':6s} | {'alpha Av':9s} | {'alpha Ap':9s} | {'beta Av':8s} | {'beta Ap':8s} | {'PBIAS Av':9s} | {'PBIAS Ap':9s}")
    print("-" * 125)
    for _, r in df_comp.iterrows():
        print(f"{r['nom']:16s} | {r['KGE_avant']:8.3f} | {r['KGE_apres']:8.3f} | {r['r_avant']:6.3f} | {r['r_apres']:6.3f} | {r['alpha_avant']:9.3f} | {r['alpha_apres']:9.3f} | {r['beta_avant']:8.3f} | {r['beta_apres']:8.3f} | {r['PBIAS_avant']:8.1f}% | {r['PBIAS_apres']:8.1f}%")
    print("=" * 125)

if __name__ == "__main__":
    main()
