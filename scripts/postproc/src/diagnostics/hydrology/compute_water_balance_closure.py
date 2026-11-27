#!/usr/bin/env python3
"""
compute_water_balance_closure.py
--------------------------------
Étape 7 : Calcul direct des incréments EnKF multi-couches et fermeture du bilan hydrique
pour OL, DA-NoCDF et DA-CDF v2 sur 2016–2020 (1 827 jours).

Auteur : M. El Aabaribaoune (@um6p)
"""

import os
import re
import glob
import time
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc

# Constantes physiques
SOIL_THICKNESS_MM = np.array([100.0, 300.0, 600.0, 1000.0], dtype=np.float64) # L1 à L4
N_ENS = 20

# Chemins absolus
BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

EXP_DIRS = {
    "OL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "DA_CDF": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
    "DA_NoCDF": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
}

RST_INITIAL = {
    "OL": os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc"),
    "DA_CDF": os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc"),
    "DA_NoCDF": os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc"),
}

RST_FINAL = {
    "OL": os.path.join(EXP_DIRS["OL"], "restarts/LIS_RST_NOAHMP401_202101010000.d01.nc"),
    "DA_CDF": os.path.join(EXP_DIRS["DA_CDF"], "restarts/surf/LIS_RST_NOAHMP401_202101010000.d01.nc"),
    "DA_NoCDF": os.path.join(EXP_DIRS["DA_NoCDF"], "restarts/surf/LIS_RST_NOAHMP401_202101010000.d01.nc"),
}

OUT_DIR = os.path.join(BASE_DIR, "scripts/postproc/outputs/matrix_2016_2020/tables/smap_cdf_sensitivity_2016_2020/water_balance")


def load_domain_mask():
    with nc.Dataset(LIS_INPUT) as ds:
        landmask = ds.variables["LANDMASK"][:].squeeze()
    land_idx = np.where(landmask == 1)
    n_land = len(land_idx[0])
    if n_land != 16030:
        raise ValueError(f"Points continentaux attendus: 16030, obtenus: {n_land}")
    return landmask, land_idx, n_land


def read_restart_stocks(rst_path, is_ensemble=False, n_ens=20):
    if not os.path.exists(rst_path):
        raise FileNotFoundError(f"Restart introuvable: {rst_path}")
    with nc.Dataset(rst_path) as ds:
        smc = ds.variables["SMC"][:] # (4, ntiles)
        wa = ds.variables["WA"][:]   # (ntiles,)
        canwat = ds.variables["CANWAT"][:]
        sneqv = ds.variables["SNEQV"][:]
    
    if is_ensemble:
        ntiles = smc.shape[1]
        expected = 16030 * n_ens
        if ntiles != expected:
            raise ValueError(f"ntiles ensemble inattendu: {ntiles} (attendu {expected}) dans {rst_path}")
        smc = smc.reshape((4, 16030, n_ens)).mean(axis=2)
        wa = wa.reshape((16030, n_ens)).mean(axis=1)
        canwat = canwat.reshape((16030, n_ens)).mean(axis=1)
        sneqv = sneqv.reshape((16030, n_ens)).mean(axis=1)
    
    # Moyenne spatiale sur les 16030 mailles continentales
    s_layers = [float(np.mean(smc[l])) * SOIL_THICKNESS_MM[l] for l in range(4)]
    s_sol = sum(s_layers)
    s_wa = float(np.mean(wa))
    s_can = float(np.mean(canwat))
    s_snq = float(np.mean(sneqv))
    s_tot = s_sol + s_wa + s_can + s_snq
    
    return {
        "s_sol": s_sol,
        "s_layers": s_layers,
        "s_wa": s_wa,
        "s_can": s_can,
        "s_snq": s_snq,
        "s_tot": s_tot,
    }


def accumulate_fluxes(exp_key, exp_dir, land_idx, n_land):
    hist_files = sorted(glob.glob(os.path.join(exp_dir, "output/**/LIS_HIST_*.d01.nc"), recursive=True))
    if len(hist_files) != 1827:
        raise ValueError(f"[{exp_key}] Fichiers historiques attendus: 1827, trouvés: {len(hist_files)}")
    
    flux_totals = {"P": 0.0, "ET": 0.0, "Qs": 0.0, "Qsb": 0.0}
    t0 = time.time()
    print(f"[{exp_key}] Intégration des flux sur 1 827 fichiers journaliers...")
    
    for f in hist_files:
        with nc.Dataset(f) as ds:
            p_land = ds.variables["TotalPrecip_tavg"][:].squeeze()[land_idx]
            et_land = ds.variables["Evap_tavg"][:].squeeze()[land_idx]
            qs_land = ds.variables["Qs_tavg"][:].squeeze()[land_idx]
            qsb_land = ds.variables["Qsb_tavg"][:].squeeze()[land_idx]
            
            # Conversion kg m-2 s-1 (mm/s) -> mm/jour
            flux_totals["P"] += float(np.mean(p_land)) * 86400.0
            flux_totals["ET"] += float(np.mean(et_land)) * 86400.0
            flux_totals["Qs"] += float(np.mean(qs_land)) * 86400.0
            flux_totals["Qsb"] += float(np.mean(qsb_land)) * 86400.0
            
    dt = time.time() - t0
    print(f"[{exp_key}] Flux intégrés en {dt:.1f} s : P={flux_totals['P']:.2f}, ET={flux_totals['ET']:.2f}, Qs={flux_totals['Qs']:.2f}, Qsb={flux_totals['Qsb']:.2f} mm")
    return flux_totals


def process_increments(exp_key, exp_dir, land_idx, n_land):
    incr_files = sorted(glob.glob(os.path.join(exp_dir, "output/**/LIS_DA_EnKF_*_incr.a01.d01.nc"), recursive=True))
    print(f"[{exp_key}] Traitement direct des incréments 4 couches sur {len(incr_files)} fichiers...")
    
    regex_date = re.compile(r"LIS_DA_EnKF_(\d{4})(\d{2})\d{6}_incr\.a01\.d01\.nc")
    
    monthly_data = {}
    
    t0 = time.time()
    for idx_f, f in enumerate(incr_files):
        m = regex_date.search(os.path.basename(f))
        if not m:
            continue
        ym = f"{m.group(1)}-{m.group(2)}"
        if ym not in monthly_data:
            monthly_data[ym] = {
                "n_files": 0,
                "pos": np.zeros(4, dtype=np.float64),
                "neg": np.zeros(4, dtype=np.float64),
                "net": np.zeros(4, dtype=np.float64),
            }
        
        monthly_data[ym]["n_files"] += 1
        
        with nc.Dataset(f) as ds:
            for l in range(4):
                vname = f"anlys_incr_Soil Moisture Layer {l+1}_01"
                data = ds.variables[vname][:].squeeze()[land_idx]
                
                # Zéro physique pour pixels non assimilés; sentinelles LIS masquées en 0
                valid = (data != -9999.0) & np.isfinite(data)
                vals = np.where(valid, data, 0.0)
                
                # Conversion m3/m3 -> mm
                pos_vals = np.maximum(vals, 0.0) * SOIL_THICKNESS_MM[l]
                neg_vals = np.minimum(vals, 0.0) * SOIL_THICKNESS_MM[l]
                
                mean_pos = float(np.mean(pos_vals))
                mean_neg = float(np.mean(neg_vals))
                
                monthly_data[ym]["pos"][l] += mean_pos
                monthly_data[ym]["neg"][l] += mean_neg
                monthly_data[ym]["net"][l] += (mean_pos + mean_neg)
                
    dt = time.time() - t0
    print(f"[{exp_key}] Incréments EnKF traités en {dt:.1f} s ({len(incr_files)/(dt+1e-5):.1f} fichiers/s).")
    
    # Synthèse globale 5 ans
    total_pos = np.zeros(4, dtype=np.float64)
    total_neg = np.zeros(4, dtype=np.float64)
    total_net = np.zeros(4, dtype=np.float64)
    total_files = len(incr_files)
    
    for ym, d in monthly_data.items():
        total_pos += d["pos"]
        total_neg += d["neg"]
        total_net += d["net"]
        
    summary = {
        "n_files": total_files,
        "pos_layers": total_pos,
        "neg_layers": total_neg,
        "net_layers": total_net,
        "pos_total": float(np.sum(total_pos)),
        "neg_total": float(np.sum(total_neg)),
        "net_total": float(np.sum(total_net)),
        "monthly": monthly_data,
    }
    return summary


def main():
    print("=" * 80)
    print(" ÉTAPE 7 : CALCUL DIRECT DES INCRÉMENTS EnKF ET BILAN HYDRIQUE 2016–2020")
    print("=" * 80)
    
    os.makedirs(OUT_DIR, exist_ok=True)
    
    landmask, land_idx, n_land = load_domain_mask()
    print(f"Domaine continental : {n_land} mailles (résolution 5 km, NorthMor)")
    
    # 1. Calcul des variations de stock depuis les fichiers restart
    print("\n--- 1. CALCUL DES VARIATIONS DE STOCK INSTANTANÉES (RESTARTS) ---")
    stocks = {}
    for exp_key in ["OL", "DA_NoCDF", "DA_CDF"]:
        is_ens = (exp_key != "OL")
        st0 = read_restart_stocks(RST_INITIAL[exp_key], is_ensemble=is_ens, n_ens=N_ENS)
        st1 = read_restart_stocks(RST_FINAL[exp_key], is_ensemble=is_ens, n_ens=N_ENS)
        
        delta_sol = st1["s_sol"] - st0["s_sol"]
        delta_wa = st1["s_wa"] - st0["s_wa"]
        delta_can = st1["s_can"] - st0["s_can"]
        delta_snq = st1["s_snq"] - st0["s_snq"]
        delta_tot = st1["s_tot"] - st0["s_tot"]
        
        stocks[exp_key] = {
            "Delta_S_sol": delta_sol,
            "Delta_S_wa": delta_wa,
            "Delta_S_can": delta_can,
            "Delta_S_snq": delta_snq,
            "Delta_S_tot": delta_tot,
        }
        print(f"[{exp_key:8s}] ΔS_sol={delta_sol:+.3f} mm, ΔS_wa={delta_wa:+.3f} mm, ΔS_tot={delta_tot:+.3f} mm")

    # 2. Intégration des flux journaliers (1 827 jours)
    print("\n--- 2. INTÉGRATION TEMPORELLE DES FLUX JOURNALIERS (1 827 JOURS) ---")
    fluxes = {}
    for exp_key in ["OL", "DA_NoCDF", "DA_CDF"]:
        fluxes[exp_key] = accumulate_fluxes(exp_key, EXP_DIRS[exp_key], land_idx, n_land)

    # 3. Traitement direct des incréments EnKF 4 couches
    print("\n--- 3. CALCUL DIRECT DES INCRÉMENTS EnKF (4 COUCHES) ---")
    increments = {}
    for exp_key in ["DA_NoCDF", "DA_CDF"]:
        increments[exp_key] = process_increments(exp_key, EXP_DIRS[exp_key], land_idx, n_land)
        
    increments["OL"] = {
        "n_files": 0,
        "pos_layers": np.zeros(4),
        "neg_layers": np.zeros(4),
        "net_layers": np.zeros(4),
        "pos_total": 0.0,
        "neg_total": 0.0,
        "net_total": 0.0,
        "monthly": {},
    }

    # 4. Construction et export du TABLEAU A (Incréments EnKF)
    print("\n" + "=" * 80)
    print(" TABLEAU A — INCRÉMENTS EnKF MESURÉS DIRECTEMENT (2016–2020)")
    print("=" * 80)
    
    table_a_rows = []
    for exp_label, exp_key in [("DA-NoCDF", "DA_NoCDF"), ("DA-CDF v2", "DA_CDF")]:
        inc = increments[exp_key]
        row = {
            "experience": exp_label,
            "n_files_analyses": inc["n_files"],
            "Wnet_L1_mm": inc["net_layers"][0],
            "Wnet_L2_mm": inc["net_layers"][1],
            "Wnet_L3_mm": inc["net_layers"][2],
            "Wnet_L4_mm": inc["net_layers"][3],
            "Wnet_total_mm": inc["net_total"],
            "Somme_positive_mm": inc["pos_total"],
            "Somme_negative_mm": inc["neg_total"],
            "Pos_L1_mm": inc["pos_layers"][0],
            "Neg_L1_mm": inc["neg_layers"][0],
            "Pos_L2_mm": inc["pos_layers"][1],
            "Neg_L2_mm": inc["neg_layers"][1],
            "Pos_L3_mm": inc["pos_layers"][2],
            "Neg_L3_mm": inc["neg_layers"][2],
            "Pos_L4_mm": inc["pos_layers"][3],
            "Neg_L4_mm": inc["neg_layers"][3],
        }
        table_a_rows.append(row)
        
    df_table_a = pd.DataFrame(table_a_rows)
    csv_table_a = os.path.join(OUT_DIR, "table_a_enkf_increments_2016_2020.csv")
    df_table_a.to_csv(csv_table_a, index=False)
    print(df_table_a.to_string(index=False))
    print(f"-> Sauvegardé : {csv_table_a}")

    # 5. Construction et export du TABLEAU B (Bilan hydrique complet et fermeture)
    print("\n" + "=" * 80)
    print(" TABLEAU B — BILAN HYDRIQUE ET FERMETURE COMPARATIVE (2016–2020)")
    print("=" * 80)
    
    table_b_rows = []
    for exp_label, exp_key in [("OL", "OL"), ("DA-NoCDF", "DA_NoCDF"), ("DA-CDF v2", "DA_CDF")]:
        fl = fluxes[exp_key]
        st = stocks[exp_key]
        inc = increments[exp_key]
        
        p = fl["P"]
        et = fl["ET"]
        qs = fl["Qs"]
        qsb = fl["Qsb"]
        outflow = et + qs + qsb
        
        wnet = inc["net_total"]
        inflow = p + wnet
        
        delta_sol = st["Delta_S_sol"]
        delta_wa = st["Delta_S_wa"]
        delta_tot = st["Delta_S_tot"]
        
        # Résidu R = P + Wnet - ET - Qs - Qsb - Delta_S_tot
        res = inflow - outflow - delta_tot
        res_rel_p = (res / p) * 100.0
        
        row = {
            "experience": exp_label,
            "P_mm": p,
            "ET_mm": et,
            "Qs_mm": qs,
            "Qsb_mm": qsb,
            "Outflow_mm": outflow,
            "Wnet_mesure_mm": wnet,
            "Inflow_mm": inflow,
            "Delta_S_sol_mm": delta_sol,
            "Delta_S_nappe_mm": delta_wa,
            "Delta_S_total_mm": delta_tot,
            "Residu_R_mm": res,
            "Residu_relatif_P_pct": res_rel_p,
        }
        table_b_rows.append(row)
        
    df_table_b = pd.DataFrame(table_b_rows)
    csv_table_b = os.path.join(OUT_DIR, "table_b_water_balance_closure_2016_2020.csv")
    df_table_b.to_csv(csv_table_b, index=False)
    print(df_table_b.to_string(index=False))
    print(f"-> Sauvegardé : {csv_table_b}")

    # 6. Construction et export du TABLEAU C (Évolution mensuelle des incréments)
    print("\n" + "=" * 80)
    print(" TABLEAU C — ÉVOLUTION MENSUELLE DES INCRÉMENTS PAR COUCHE (2016–2020)")
    print("=" * 80)
    
    table_c_rows = []
    all_months = sorted(set(list(increments["DA_CDF"]["monthly"].keys()) + list(increments["DA_NoCDF"]["monthly"].keys())))
    
    for ym in all_months:
        d_cdf = increments["DA_CDF"]["monthly"].get(ym, {"n_files": 0, "pos": np.zeros(4), "neg": np.zeros(4), "net": np.zeros(4)})
        d_nocdf = increments["DA_NoCDF"]["monthly"].get(ym, {"n_files": 0, "pos": np.zeros(4), "neg": np.zeros(4), "net": np.zeros(4)})
        
        row = {
            "mois": ym,
            # DA-CDF v2
            "CDF_n_files": d_cdf["n_files"],
            "CDF_net_L1_mm": d_cdf["net"][0],
            "CDF_net_L2_mm": d_cdf["net"][1],
            "CDF_net_L3_mm": d_cdf["net"][2],
            "CDF_net_L4_mm": d_cdf["net"][3],
            "CDF_net_total_mm": np.sum(d_cdf["net"]),
            "CDF_pos_total_mm": np.sum(d_cdf["pos"]),
            "CDF_neg_total_mm": np.sum(d_cdf["neg"]),
            # DA-NoCDF
            "NoCDF_n_files": d_nocdf["n_files"],
            "NoCDF_net_L1_mm": d_nocdf["net"][0],
            "NoCDF_net_L2_mm": d_nocdf["net"][1],
            "NoCDF_net_L3_mm": d_nocdf["net"][2],
            "NoCDF_net_L4_mm": d_nocdf["net"][3],
            "NoCDF_net_total_mm": np.sum(d_nocdf["net"]),
            "NoCDF_pos_total_mm": np.sum(d_nocdf["pos"]),
            "NoCDF_neg_total_mm": np.sum(d_nocdf["neg"]),
        }
        table_c_rows.append(row)
        
    df_table_c = pd.DataFrame(table_c_rows)
    csv_table_c = os.path.join(OUT_DIR, "table_c_monthly_increments_2016_2020.csv")
    df_table_c.to_csv(csv_table_c, index=False)
    print(f"Tableau mensuel généré : 60 mois x 16 colonnes.")
    print(f"-> Sauvegardé : {csv_table_c}")

    print("\n" + "=" * 80)
    print("CALCUL ET EXPORTS COMPLÉTÉS AVEC SUCCÈS DANS :", OUT_DIR)
    print("=" * 80)


if __name__ == "__main__":
    main()
