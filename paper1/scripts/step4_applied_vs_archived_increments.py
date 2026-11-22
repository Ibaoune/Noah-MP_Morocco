#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step4_applied_vs_archived_increments.py
Calcul rigoureux des incréments appliqués vs archivés (version 2 corrigée)
sur la simulation haute-fréquence DA_nocdf_diag_15min_2018Nov (01 au 06-11-2018).

Points méthodologiques corrigés (par rapport au Lot 1c) :
1. Fenêtre temporelle exacte : LIS_diagnoseSurfaceOutputVar étant appelé AVANT
   la perturbation et l'analyse EnKF au pas T, l'état après analyse est diagnostiqué
   au pas T+15min. La variation brute d'analyse est donc SM(T+15min) - SM(T).
2. Correction de la tendance physique locale à l'aide des pas adjacents :
   Delta_phys = 0.5 * [(SM(T) - SM(T-15min)) + (SM(T+30min) - SM(T+15min))].
   Delta_analyse = Delta_raw - Delta_phys.
3. Déduction de la perturbation stochastique à l'aide des heures témoins sans analyse
   (03:00, 09:00, 21:00) : Delta_net = Delta_analyse - mean(Delta_temoin)
   pour les heures d'analyse coïncidant avec un cycle de perturbation (06:00, 18:00).
4. Restriction stricte aux mailles où l'incrément archivé est non nul (mailles observées).
5. Conversion en millimètres de colonne par couche (dz = 0.1, 0.3, 0.6, 1.0 m).
"""

import os
import sys
import glob
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
RUN_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/output")
HIST_DIR = os.path.join(RUN_DIR, "SURFACEMODEL/201811")
ENKF_DIR = os.path.join(RUN_DIR, "EnKF/201811")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")

os.makedirs(TABLES_DIR, exist_ok=True)

# Épaisseurs des 4 couches de sol Noah-MP (mètres -> mm)
DZ_MM = [100.0, 300.0, 600.0, 1000.0]

def load_soilm_inst(dt):
    dt_str = dt.strftime("%Y%m%d%H%M")
    fpath = os.path.join(HIST_DIR, f"LIS_HIST_{dt_str}.d01.nc")
    if not os.path.exists(fpath):
        return None
    with nc.Dataset(fpath) as ds:
        # Shape: (4, 121, 181)
        return ds["SoilMoist_inst"][:]

def compute_step_jump(dt):
    """Calcule le saut d'humidité corrigé de la tendance physique à l'instant dt."""
    sm_m15 = load_soilm_inst(dt - datetime.timedelta(minutes=15))
    sm_0   = load_soilm_inst(dt)
    sm_p15 = load_soilm_inst(dt + datetime.timedelta(minutes=15))
    sm_p30 = load_soilm_inst(dt + datetime.timedelta(minutes=30))

    if sm_m15 is None or sm_0 is None or sm_p15 is None or sm_p30 is None:
        return None

    raw_jump = sm_p15 - sm_0
    phys_trend = 0.5 * ((sm_0 - sm_m15) + (sm_p30 - sm_p15))
    corr_jump = raw_jump - phys_trend
    return corr_jump

def main():
    print(">>> 1. Calcul des sauts aux heures témoins (03:00, 09:00, 21:00)...")
    witness_jumps = []
    # Dates du 01 au 05 novembre 2018
    for day in range(1, 6):
        for hr in [3, 9, 21]:
            dt = datetime.datetime(2018, 11, day, hr, 0)
            jump = compute_step_jump(dt)
            if jump is not None:
                witness_jumps.append(jump)
                print(f"  Témoin {dt.strftime('%Y-%m-%d %H:%M')}: OK")

    witness_array = np.array(witness_jumps) # shape (N_witness, 4, 121, 181)
    mean_witness_jump = np.mean(witness_array, axis=0) # shape (4, 121, 181)
    print(f"  [OK] {len(witness_jumps)} pas témoins calculés et moyennés.")

    print("\n>>> 2. Analyse des 12 événements d'assimilation EnKF...")
    incr_files = sorted(glob.glob(os.path.join(ENKF_DIR, "LIS_DA_EnKF_*_incr.a01.d01.nc")))
    print(f"  Trouvé {len(incr_files)} fichiers d'incréments EnKF.")

    event_records = []
    all_applied_mm = {k: [] for k in range(5)} # 0..3 layers, 4 column
    all_archived_mm = {k: [] for k in range(5)}

    for f_incr in incr_files:
        fname = os.path.basename(f_incr)
        # Ex: LIS_DA_EnKF_201811010600_incr.a01.d01.nc
        date_str = fname.split("_")[3]
        dt = datetime.datetime.strptime(date_str, "%Y%m%d%H%M")
        hr = dt.hour

        # Saut corrigé à l'heure d'analyse
        corr_jump = compute_step_jump(dt)
        if corr_jump is None:
            print(f"  [WARN] Données HIST manquantes pour {dt}")
            continue

        # Si l'heure coïncide avec un cycle de perturbation d'état (toutes les 3h: 06h, 18h)
        is_pert_hr = (hr % 3 == 0)
        if is_pert_hr:
            net_jump = corr_jump - mean_witness_jump
        else:
            net_jump = corr_jump

        # Lecture de l'incrément archivé
        with nc.Dataset(f_incr) as ds:
            incr_arch = np.zeros_like(corr_jump)
            for k in range(4):
                incr_arch[k] = ds[f"anlys_incr_Soil Moisture Layer {k+1}_01"][:]

        # Masque des mailles avec incrément non nul sur la couche 1
        mask = (incr_arch[0] != -9999.0) & (~np.isnan(incr_arch[0])) & (incr_arch[0] != 0.0)
        n_cells = int(np.sum(mask))

        if n_cells == 0:
            print(f"  [{date_str}] Aucun incrément non nul.")
            continue

        # Calcul par couche et colonne
        col_app_mm = np.zeros(n_cells)
        col_arc_mm = np.zeros(n_cells)

        for k in range(4):
            dz = DZ_MM[k]
            app_vol = net_jump[k][mask]
            arc_vol = incr_arch[k][mask]

            app_mm = app_vol * dz
            arc_mm = arc_vol * dz

            col_app_mm += app_mm
            col_arc_mm += arc_mm

            all_applied_mm[k].extend(app_mm)
            all_archived_mm[k].extend(arc_mm)

            r_val = float(np.corrcoef(app_mm, arc_mm)[0, 1]) if np.std(app_mm) > 1e-9 and np.std(arc_mm) > 1e-9 else 1.0
            ratio = float(np.mean(app_mm) / np.mean(arc_mm)) if abs(np.mean(arc_mm)) > 1e-9 else 1.0

            event_records.append({
                "event_time": dt.strftime("%Y-%m-%d %H:%M"),
                "is_pert_hour": is_pert_hr,
                "layer": f"Layer {k+1}",
                "depth_mm": dz,
                "n_cells": n_cells,
                "mean_archived_mm": float(np.mean(arc_mm)),
                "mean_applied_mm": float(np.mean(app_mm)),
                "sum_archived_mm": float(np.sum(arc_mm)),
                "sum_applied_mm": float(np.sum(app_mm)),
                "correlation_r": r_val,
                "ratio_applied_archived": ratio
            })

        # Colonne totale
        all_applied_mm[4].extend(col_app_mm)
        all_archived_mm[4].extend(col_arc_mm)
        r_col = float(np.corrcoef(col_app_mm, col_arc_mm)[0, 1]) if np.std(col_app_mm) > 1e-9 and np.std(col_arc_mm) > 1e-9 else 1.0
        ratio_col = float(np.mean(col_app_mm) / np.mean(col_arc_mm)) if abs(np.mean(col_arc_mm)) > 1e-9 else 1.0

        event_records.append({
            "event_time": dt.strftime("%Y-%m-%d %H:%M"),
            "is_pert_hour": is_pert_hr,
            "layer": "Column Total",
            "depth_mm": 2000.0,
            "n_cells": n_cells,
            "mean_archived_mm": float(np.mean(col_arc_mm)),
            "mean_applied_mm": float(np.mean(col_app_mm)),
            "sum_archived_mm": float(np.sum(col_arc_mm)),
            "sum_applied_mm": float(np.sum(col_app_mm)),
            "correlation_r": r_col,
            "ratio_applied_archived": ratio_col
        })

        print(f"  [{dt.strftime('%Y-%m-%d %H:%M')}] {n_cells:4d} mailles | Col mean: arch={np.mean(col_arc_mm):+.3f} mm, app={np.mean(col_app_mm):+.3f} mm | r={r_col:.4f}, ratio={ratio_col:.4f}")

    df_events = pd.DataFrame(event_records)
    out_csv = os.path.join(TABLES_DIR, "applied_vs_archived_increments_v2.csv")
    df_events.to_csv(out_csv, index=False)
    print(f"\n[OK] Table détaillée sauvée dans : {out_csv}")

    # Synthèse globale par couche et pour la colonne totale
    summary_records = []
    layer_names = ["Layer 1 (0-10 cm)", "Layer 2 (10-40 cm)", "Layer 3 (40-100 cm)", "Layer 4 (100-200 cm)", "Column Total (0-200 cm)"]
    for k in range(5):
        arr_app = np.array(all_applied_mm[k])
        arr_arc = np.array(all_archived_mm[k])
        r_tot = float(np.corrcoef(arr_app, arr_arc)[0, 1])
        ratio_tot = float(np.mean(arr_app) / np.mean(arr_arc))
        summary_records.append({
            "level": layer_names[k],
            "depth_mm": DZ_MM[k] if k < 4 else 2000.0,
            "total_samples": len(arr_app),
            "mean_archived_mm": float(np.mean(arr_arc)),
            "mean_applied_mm": float(np.mean(arr_app)),
            "sum_archived_mm": float(np.sum(arr_arc)),
            "sum_applied_mm": float(np.sum(arr_app)),
            "correlation_r": r_tot,
            "ratio_applied_archived": ratio_tot
        })

    df_summary = pd.DataFrame(summary_records)
    out_summary_csv = os.path.join(TABLES_DIR, "applied_vs_archived_increments_summary_v2.csv")
    df_summary.to_csv(out_summary_csv, index=False)
    print(f"[OK] Table de synthèse globale sauvée dans : {out_summary_csv}")
    print("\n" + df_summary.to_string(index=False))

if __name__ == "__main__":
    main()
