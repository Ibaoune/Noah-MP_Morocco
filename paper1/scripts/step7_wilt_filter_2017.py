#!/usr/bin/env python3
"""
step7_wilt_filter_2017.py
-------------------------
Partie B2 : Évaluation du filtre de flétrissement en 2017.
- Fraction des retrievals rejetés par mois et par texture (DA_nocdf vs DA_nocdf_nowilt 2017)
- Delta ET par texture (annuel, JJA, MAM)
Sortie : paper1/tables/e5_2017_by_texture.csv
"""

import os
import glob
import numpy as np
import pandas as pd
import netCDF4 as nc
from datetime import datetime, timedelta

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
PARAM_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# Chemins des runs 2017
DIR_NOCDF = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output")
DIR_NOWILT = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/output")

TEXTURE_NAMES = {
    1: "Sand",
    3: "Sandy Loam",
    4: "Silt Loam",
    6: "Loam",
    7: "Sandy Clay Loam",
    9: "Clay Loam",
    12: "Clay"
}

def main():
    print("=== PARTIE B2 : FILTRE DE FLÉTRISSEMENT EN 2017 ===")
    
    # 1. Masques géographiques et textures
    with nc.Dataset(PARAM_NC) as ds:
        landmask = ds.variables["LANDMASK"][:].squeeze() > 0.5
        tex_raw = ds.variables["TEXTURE"][:]
    
    dom_tex = np.argmax(tex_raw, axis=0) + 1  # 1..16
    
    # 2. Comptage des observations par mois et par texture
    print("\n>>> Comptage des observations EnKF par mois et par texture...")
    obs_monthly_tex = []
    
    for m in range(1, 13):
        m_str = f"2017-{m:02d}"
        ym = f"2017{m:02d}"
        
        # Files DA_nocdf
        files_nocdf = sorted(glob.glob(os.path.join(DIR_NOCDF, f"{m_str}/EnKF/{ym}/*_innov.*.nc")))
        # Files DA_nowilt
        files_nowilt = sorted(glob.glob(os.path.join(DIR_NOWILT, f"EnKF/{ym}/*_innov.*.nc")))
        
        counts = {
            "nocdf": {t: 0 for t in list(TEXTURE_NAMES.keys()) + [0]},
            "nowilt": {t: 0 for t in list(TEXTURE_NAMES.keys()) + [0]}
        }
        
        for f in files_nocdf:
            with nc.Dataset(f) as ds:
                d = ds.variables["innov_01"][:]
                valid = (d != -9999.0) & (~np.isnan(d))
                if np.any(valid):
                    counts["nocdf"][0] += int(np.sum(valid))
                    rows_v, cols_v = np.where(valid)
                    for r, c in zip(rows_v, cols_v):
                        tid = dom_tex[r, c]
                        if tid in counts["nocdf"]:
                            counts["nocdf"][tid] += 1
                            
        for f in files_nowilt:
            with nc.Dataset(f) as ds:
                d = ds.variables["innov_01"][:]
                valid = (d != -9999.0) & (~np.isnan(d))
                if np.any(valid):
                    counts["nowilt"][0] += int(np.sum(valid))
                    rows_v, cols_v = np.where(valid)
                    for r, c in zip(rows_v, cols_v):
                        tid = dom_tex[r, c]
                        if tid in counts["nowilt"]:
                            counts["nowilt"][tid] += 1
                            
        # Enregistrer les stats pour le mois
        for tid in [0] + list(TEXTURE_NAMES.keys()):
            t_name = "Domain_All" if tid == 0 else TEXTURE_NAMES[tid]
            n_nc = counts["nocdf"][tid]
            n_nw = counts["nowilt"][tid]
            n_rej = n_nw - n_nc
            pct_rej = (n_rej / n_nw * 100.0) if n_nw > 0 else 0.0
            
            obs_monthly_tex.append({
                "period": m_str,
                "texture_id": tid,
                "texture_name": t_name,
                "n_obs_nocdf": n_nc,
                "n_obs_nowilt": n_nw,
                "n_obs_rejected": n_rej,
                "rejection_fraction_pct": round(pct_rej, 2)
            })
            
    df_obs = pd.DataFrame(obs_monthly_tex)
    
    # 3. Calcul de l'évaporation (ET) par texture
    print("\n>>> Calcul de l'ET par texture pour DA_nocdf et DA_nocdf_nowilt...")
    # Grille de cumul annuel et saisonnier pour chaque expérience
    et_grid_nocdf = np.zeros_like(dom_tex, dtype=np.float64)
    et_grid_nowilt = np.zeros_like(dom_tex, dtype=np.float64)
    
    et_mam_nocdf = np.zeros_like(dom_tex, dtype=np.float64)
    et_mam_nowilt = np.zeros_like(dom_tex, dtype=np.float64)
    
    et_jja_nocdf = np.zeros_like(dom_tex, dtype=np.float64)
    et_jja_nowilt = np.zeros_like(dom_tex, dtype=np.float64)
    
    # Mapper les fichiers NOWILT par mois calendaire (date_fichier - 1j)
    nw_by_month = {m: [] for m in range(1, 13)}
    for fp in sorted(glob.glob(os.path.join(DIR_NOWILT, "SURFACEMODEL/*/LIS_HIST_*.d01.nc"))):
        dstr = os.path.basename(fp).split("_")[2][:8]
        dt = datetime.strptime(dstr, "%Y%m%d") - timedelta(days=1)
        if dt.year == 2017:
            nw_by_month[dt.month].append(fp)
    
    for m in range(1, 13):
        m_str = f"2017-{m:02d}"
        ym = f"2017{m:02d}"
        
        hist_nc = sorted(glob.glob(os.path.join(DIR_NOCDF, f"{m_str}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
        hist_nw = nw_by_month[m]
        
        # Accumulate daily Evap (kg m-2 s-1 * 86400 = mm/day)
        for fn in hist_nc:
            with nc.Dataset(fn) as ds:
                evap = ds.variables["Evap_tavg"][:].squeeze() * 86400.0
                et_grid_nocdf += evap
                if m in [3, 4, 5]:
                    et_mam_nocdf += evap
                elif m in [6, 7, 8]:
                    et_jja_nocdf += evap
                    
        for fn in hist_nw:
            with nc.Dataset(fn) as ds:
                evap = ds.variables["Evap_tavg"][:].squeeze() * 86400.0
                et_grid_nowilt += evap
                if m in [3, 4, 5]:
                    et_mam_nowilt += evap
                elif m in [6, 7, 8]:
                    et_jja_nowilt += evap
                    
    # Calcul des moyennes d'ET par texture
    tex_et_records = {}
    for tid in [0] + list(TEXTURE_NAMES.keys()):
        if tid == 0:
            mask = landmask
        else:
            mask = landmask & (dom_tex == tid)
            
        n_pix = int(np.sum(mask))
        if n_pix > 0:
            ann_nc = float(np.mean(et_grid_nocdf[mask]))
            ann_nw = float(np.mean(et_grid_nowilt[mask]))
            mam_nc = float(np.mean(et_mam_nocdf[mask]))
            mam_nw = float(np.mean(et_mam_nowilt[mask]))
            jja_nc = float(np.mean(et_jja_nocdf[mask]))
            jja_nw = float(np.mean(et_jja_nowilt[mask]))
            
            tex_et_records[tid] = {
                "n_pixels": n_pix,
                "ET_ann_nocdf_mm": round(ann_nc, 2),
                "ET_ann_nowilt_mm": round(ann_nw, 2),
                "Delta_ET_ann_mm": round(ann_nw - ann_nc, 2),
                "ET_mam_nocdf_mm": round(mam_nc, 2),
                "ET_mam_nowilt_mm": round(mam_nw, 2),
                "Delta_ET_mam_mm": round(mam_nw - mam_nc, 2),
                "ET_jja_nocdf_mm": round(jja_nc, 2),
                "ET_jja_nowilt_mm": round(jja_nw, 2),
                "Delta_ET_jja_mm": round(jja_nw - jja_nc, 2)
            }
            
    # 4. Assembler la table finale e5_2017_by_texture.csv
    # Ajouter les totaux annuels et saisonniers d'observations
    final_rows = []
    
    # Lignes mensuelles
    for idx, row in df_obs.iterrows():
        tid = row["texture_id"]
        et_data = tex_et_records.get(tid, {})
        final_rows.append({
            "period": row["period"],
            "texture_id": tid,
            "texture_name": row["texture_name"],
            "n_pixels": et_data.get("n_pixels", 0),
            "n_obs_nocdf": row["n_obs_nocdf"],
            "n_obs_nowilt": row["n_obs_nowilt"],
            "n_obs_rejected": row["n_obs_rejected"],
            "rejection_fraction_pct": row["rejection_fraction_pct"],
            "ET_nocdf_mm": np.nan,  # Valeurs ET détaillées dans les bilans agrégés
            "ET_nowilt_mm": np.nan,
            "Delta_ET_mm": np.nan
        })
        
    # Totaux MAM, JJA, ANNUAL par texture
    for period_name, m_list, et_key in [("MAM_2017", ["2017-03", "2017-04", "2017-05"], "mam"),
                                        ("JJA_2017", ["2017-06", "2017-07", "2017-08"], "jja"),
                                        ("ANNUAL_2017", [f"2017-{m:02d}" for m in range(1, 13)], "ann")]:
        for tid in [0] + list(TEXTURE_NAMES.keys()):
            t_name = "Domain_All" if tid == 0 else TEXTURE_NAMES[tid]
            sub = df_obs[(df_obs["period"].isin(m_list)) & (df_obs["texture_id"] == tid)]
            tot_nc = int(sub["n_obs_nocdf"].sum())
            tot_nw = int(sub["n_obs_nowilt"].sum())
            tot_rej = tot_nw - tot_nc
            pct = round((tot_rej / tot_nw * 100.0), 2) if tot_nw > 0 else 0.0
            et_data = tex_et_records.get(tid, {})
            
            final_rows.append({
                "period": period_name,
                "texture_id": tid,
                "texture_name": t_name,
                "n_pixels": et_data.get("n_pixels", 0),
                "n_obs_nocdf": tot_nc,
                "n_obs_nowilt": tot_nw,
                "n_obs_rejected": tot_rej,
                "rejection_fraction_pct": pct,
                "ET_nocdf_mm": et_data.get(f"ET_{et_key}_nocdf_mm", np.nan),
                "ET_nowilt_mm": et_data.get(f"ET_{et_key}_nowilt_mm", np.nan),
                "Delta_ET_mm": et_data.get(f"Delta_ET_{et_key}_mm", np.nan)
            })
            
    df_final = pd.DataFrame(final_rows)
    out_csv = os.path.join(TABLES_DIR, "e5_2017_by_texture.csv")
    df_final.to_csv(out_csv, index=False)
    print(f"\n[OK] Table générée et sauvegardée avec succès : {out_csv}")
    print(df_final[df_final["period"] == "ANNUAL_2017"][["texture_name", "n_pixels", "n_obs_nocdf", "n_obs_nowilt", "rejection_fraction_pct", "Delta_ET_mm"]])

if __name__ == "__main__":
    main()
