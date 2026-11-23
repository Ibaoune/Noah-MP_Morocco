#!/usr/bin/env python3
"""
step21_compare_ol_daic_vs_ens_corr.py
-------------------------------------
Point 5 : Comparaison détaillée 2018 entre OL_DAIC et ENS_corr.
- Variables : ESoil, TVeg, ECanop, SoilMoist (4 couches et total colonne)
- Échelles : domaine complet, mensuel (1-12), saisonnier (MAM, JJA) et annuel
- Distribution spatiale des écarts par maille (ENS_corr - OL_DAIC) : moyenne, écart-type, min, p25, médiane, p75, max
Sortie : paper1/tables/ol_daic_vs_ens_corr_fluxes_2018.csv
"""

import os
import glob
import time
import numpy as np
import pandas as pd
import netCDF4 as nc
from multiprocessing import Pool

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)
INPUT_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

DIR_OL = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output")
DIR_EC = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output")

DZ = np.array([0.1, 0.3, 0.6, 1.0]) # épaisseurs des couches de sol en m

with nc.Dataset(INPUT_NC) as ds:
    landmask = (ds.variables["LANDMASK"][:].squeeze() == 1)

def get_month_files(exp_dir, m):
    ym = f"2018{m:02d}"
    files = sorted(glob.glob(os.path.join(exp_dir, f"SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")))
    # Ajouter le fichier de clôture s'il est dans le mois suivant
    if m < 12:
        closure = os.path.join(exp_dir, f"SURFACEMODEL/2018{m+1:02d}/LIS_HIST_2018{m+1:02d}010000.d01.nc")
    else:
        closure = os.path.join(exp_dir, "SURFACEMODEL/201901/LIS_HIST_201901010000.d01.nc")
    if os.path.exists(closure) and closure not in files:
        files.append(closure)
    return files

def process_month(m):
    files_ol = get_month_files(DIR_OL, m)
    files_ec = get_month_files(DIR_EC, m)
    
    n_days = len(files_ol)
    assert len(files_ol) == len(files_ec), f"Mois {m}: mismatch files count {len(files_ol)} vs {len(files_ec)}"
    
    # Cumuls mensuels des flux (mm) et moyennes mensuelles d'humidité (m3/m3)
    # Formats grilles (121, 181)
    esoil_ol = np.zeros((121, 181), dtype=np.float64)
    tveg_ol = np.zeros((121, 181), dtype=np.float64)
    ecanop_ol = np.zeros((121, 181), dtype=np.float64)
    sm_ol = np.zeros((4, 121, 181), dtype=np.float64)
    
    esoil_ec = np.zeros((121, 181), dtype=np.float64)
    tveg_ec = np.zeros((121, 181), dtype=np.float64)
    ecanop_ec = np.zeros((121, 181), dtype=np.float64)
    sm_ec = np.zeros((4, 121, 181), dtype=np.float64)
    
    for f_ol, f_ec in zip(files_ol, files_ec):
        with nc.Dataset(f_ol) as ds_o:
            esoil_ol += ds_o.variables["ESoil_tavg"][:].squeeze() * 86400.0
            tveg_ol += ds_o.variables["TVeg_tavg"][:].squeeze() * 86400.0
            ecanop_ol += ds_o.variables["ECanop_tavg"][:].squeeze() * 86400.0
            sm_ol += ds_o.variables["SoilMoist_tavg"][:].squeeze()
            
        with nc.Dataset(f_ec) as ds_e:
            esoil_ec += ds_e.variables["ESoil_tavg"][:].squeeze() * 86400.0
            tveg_ec += ds_e.variables["TVeg_tavg"][:].squeeze() * 86400.0
            ecanop_ec += ds_e.variables["ECanop_tavg"][:].squeeze() * 86400.0
            sm_ec += ds_e.variables["SoilMoist_tavg"][:].squeeze()
            
    # Moyenne temporelle pour l'humidité
    sm_ol /= n_days
    sm_ec /= n_days
    
    return {
        "m": m,
        "n_days": n_days,
        "esoil_ol": esoil_ol,
        "tveg_ol": tveg_ol,
        "ecanop_ol": ecanop_ol,
        "sm_ol": sm_ol,
        "esoil_ec": esoil_ec,
        "tveg_ec": tveg_ec,
        "ecanop_ec": ecanop_ec,
        "sm_ec": sm_ec
    }

def summarize_diff(arr_ec, arr_ol, landmask):
    v_ec = arr_ec[landmask]
    v_ol = arr_ol[landmask]
    diff = v_ec - v_ol
    return {
        "mean_OL_DAIC": float(np.mean(v_ol)),
        "mean_ENS_corr": float(np.mean(v_ec)),
        "diff_domain_mean": float(np.mean(diff)),
        "diff_std": float(np.std(diff)),
        "diff_min": float(np.min(diff)),
        "diff_p25": float(np.percentile(diff, 25)),
        "diff_median": float(np.median(diff)),
        "diff_p75": float(np.percentile(diff, 75)),
        "diff_max": float(np.max(diff))
    }

def main():
    print("=== STEP 21 : COMPARAISON OL_DAIC VS ENS_CORR (2018) ===")
    t0 = time.time()
    with Pool(processes=12) as pool:
        month_data = pool.map(process_month, range(1, 13))
    print(f"Extraction terminée en {time.time()-t0:.1f} s.")
    
    # Dictionnaires par mois
    m_dict = {d["m"]: d for d in month_data}
    
    # Agrégation des périodes : Mensuel 1..12, MAM, JJA, ANNUAL
    periods = {}
    for m in range(1, 13):
        periods[f"2018-{m:02d}"] = [m]
    periods["MAM_2018"] = [3, 4, 5]
    periods["JJA_2018"] = [6, 7, 8]
    periods["ANNUAL_2018"] = list(range(1, 13))
    
    rows = []
    
    for pname, mlist in periods.items():
        tot_days = sum(m_dict[m]["n_days"] for m in mlist)
        
        # Flux : somme des cumuls mensuels
        esoil_o = sum(m_dict[m]["esoil_ol"] for m in mlist)
        tveg_o = sum(m_dict[m]["tveg_ol"] for m in mlist)
        ecanop_o = sum(m_dict[m]["ecanop_ol"] for m in mlist)
        et_tot_o = esoil_o + tveg_o + ecanop_o
        
        esoil_e = sum(m_dict[m]["esoil_ec"] for m in mlist)
        tveg_e = sum(m_dict[m]["tveg_ec"] for m in mlist)
        ecanop_e = sum(m_dict[m]["ecanop_ec"] for m in mlist)
        et_tot_e = esoil_e + tveg_e + ecanop_e
        
        # Humidité : moyenne pondérée par les jours
        sm_o = sum(m_dict[m]["sm_ol"] * m_dict[m]["n_days"] for m in mlist) / tot_days
        sm_e = sum(m_dict[m]["sm_ec"] * m_dict[m]["n_days"] for m in mlist) / tot_days
        
        # Humidité totale colonne (mm d'eau)
        sm_tot_o = np.sum(sm_o * DZ[:, None, None], axis=0) * 1000.0
        sm_tot_e = np.sum(sm_e * DZ[:, None, None], axis=0) * 1000.0
        
        var_pairs = [
            ("ESoil_mm", esoil_e, esoil_o, "Évaporation sol nu (mm)"),
            ("TVeg_mm", tveg_e, tveg_o, "Transpiration végétale (mm)"),
            ("ECanop_mm", ecanop_e, ecanop_o, "Évaporation canopée (mm)"),
            ("ET_Total_mm", et_tot_e, et_tot_o, "Évapotranspiration totale (mm)"),
            ("SoilMoist_Layer1_m3m3", sm_e[0], sm_o[0], "Humidité sol couche 1 (0-10cm, m3/m3)"),
            ("SoilMoist_Layer2_m3m3", sm_e[1], sm_o[1], "Humidité sol couche 2 (10-40cm, m3/m3)"),
            ("SoilMoist_Layer3_m3m3", sm_e[2], sm_o[2], "Humidité sol couche 3 (40-100cm, m3/m3)"),
            ("SoilMoist_Layer4_m3m3", sm_e[3], sm_o[3], "Humidité sol couche 4 (100-200cm, m3/m3)"),
            ("SoilMoist_Total_mm", sm_tot_e, sm_tot_o, "Stock d'eau total profil 0-2m (mm)")
        ]
        
        for vname, arr_e, arr_o, vdesc in var_pairs:
            stats = summarize_diff(arr_e, arr_o, landmask)
            rows.append({
                "period": pname,
                "variable": vname,
                "description": vdesc,
                "mean_OL_DAIC": round(stats["mean_OL_DAIC"], 4),
                "mean_ENS_corr": round(stats["mean_ENS_corr"], 4),
                "diff_domain_mean": round(stats["diff_domain_mean"], 4),
                "diff_std": round(stats["diff_std"], 4),
                "diff_min": round(stats["diff_min"], 4),
                "diff_p25": round(stats["diff_p25"], 4),
                "diff_median": round(stats["diff_median"], 4),
                "diff_p75": round(stats["diff_p75"], 4),
                "diff_max": round(stats["diff_max"], 4)
            })
            
    df_res = pd.DataFrame(rows)
    out_csv = os.path.join(TABLES_DIR, "ol_daic_vs_ens_corr_fluxes_2018.csv")
    df_res.to_csv(out_csv, index=False)
    print(f"[OK] Table sauvegardée : {out_csv}")
    
    # Afficher un résumé synthétique Annuel et JJA
    ann_sub = df_res[df_res["period"] == "ANNUAL_2018"][["variable", "mean_OL_DAIC", "mean_ENS_corr", "diff_domain_mean", "diff_median", "diff_std"]]
    print("\n>>> Résumé Annuel 2018 (OL_DAIC vs ENS_corr) :")
    print(ann_sub.to_string(index=False))

if __name__ == "__main__":
    main()
