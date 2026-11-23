#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step13_upstream_catchments_da_corr.py
Partie 4 : Décomposition complète des bassins amont de Lalla Chafia et Sidi Jabeur pour DA_corr et les autres expériences :
- innovations moyennes mensuelles (Lalla Chafia et Sidi Jabeur)
- incréments par couche (couches 1 à 4)
- Qs, Qsb, TotalRunoff, Delta_WA, Delta_SMC, Delta_S
- Résidu

Met à jour :
  - paper1/tables/lalla_chafia_innovations_and_increments.csv (renommé/complété avec Sidi Jabeur)
  - paper1/tables/water_balance_upstream_catchments_annual_summary_2018.csv (avec Qs, Qsb, Delta_WA, Delta_S, Résidu)
"""

import os
import glob
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
PARAM_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

# 1. Masques et poids de bassin
with nc.Dataset(LDT_FILE) as ds:
    flow_x = ds["HYMAP_flow_direction_x"][:]
    flow_y = ds["HYMAP_flow_direction_y"][:]

R, C = flow_x.shape
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
            parents.setdefault((pr, pc), []).append((r, c))

def get_catchment(outlet_r, outlet_c):
    vis = set([(outlet_r, outlet_c)])
    q = [(outlet_r, outlet_c)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis

cells_lalla = get_catchment(75, 71)
cells_jabeur = get_catchment(71, 71)

weights_181 = {}
for cname, ccells in [("Lalla Chafia", cells_lalla), ("Sidi Jabeur", cells_jabeur)]:
    w = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w[r, c] += 0.25
        w[r, c+1] += 0.25
        w[r+1, c] += 0.25
        w[r+1, c+1] += 0.25
    w /= np.sum(w)
    weights_181[cname] = w

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

EXPERIMENTS_2018 = {
    "OL_DAIC": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
        "is_ens": False, "is_da": False, "style": "flat", "has_p": False,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    },
    "ENS_OPL": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
        "is_ens": True, "is_da": False, "style": "flat", "has_p": True,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    },
    "ENS_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018"),
        "is_ens": True, "is_da": False, "style": "flat", "has_p": True,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    },
    "DA_nocdf": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        "is_ens": True, "is_da": True, "style": "hierarchical", "has_p": True,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201901010000.d01.nc")
    },
    "DA_nocdf_nowilt": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018"),
        "is_ens": True, "is_da": True, "style": "flat", "has_p": True,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    },
    "DA_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018"),
        "is_ens": True, "is_da": True, "style": "flat", "has_p": True,
        "rst0": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "rst1": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    }
}

# Date ranges 2018
month_ranges_2018 = {}
for m in range(1, 13):
    if m == 1:
        s_ts = "201801020000"
        e_ts = "201802010000"
    elif m == 12:
        s_ts = "201812020000"
        e_ts = "201901010000"
    else:
        s_ts = f"2018{m:02d}020000"
        e_ts = f"2018{m+1:02d}010000"
    month_ranges_2018[m] = (s_ts, e_ts)

def read_storage_components(fp, w):
    with nc.Dataset(fp) as ds:
        smc = ds.variables["SMC"][:]
        wa = ds.variables["WA"][:]
        can = ds.variables["CANWAT"][:]
        sneqv = ds.variables["SNEQV"][:]
        if smc.ndim == 3:
            smc_m = np.mean(smc, axis=2)
            wa_m = np.mean(wa, axis=1)
            can_m = np.mean(can, axis=1)
            sn_m = np.mean(sneqv, axis=1)
        elif smc.ndim == 2 and smc.shape[1] == 320600:
            smc_m = np.mean(smc.reshape(4, 16030, 20), axis=2)
            wa_m = np.mean(wa.reshape(16030, 20), axis=1)
            can_m = np.mean(can.reshape(16030, 20), axis=1)
            sn_m = np.mean(sneqv.reshape(16030, 20), axis=1)
        else:
            smc_m, wa_m, can_m, sn_m = smc, wa, can, sneqv

        smc_col = np.sum(smc_m * dz[:, None], axis=0) * 1000.0
        lats = ds.variables["lat"][::20] if "lat" in ds.variables else None
        lons = ds.variables["lon"][::20] if "lon" in ds.variables else None
        
        grid_smc = np.zeros((121, 181), dtype=float)
        grid_wa = np.zeros((121, 181), dtype=float)
        grid_tot = np.zeros((121, 181), dtype=float)
        for i in range(len(lats)):
            gc = int(round((lons[i] - (-10.0)) / 0.05))
            gr = int(round((lats[i] - 30.0) / 0.05))
            grid_smc[gr, gc] = smc_col[i]
            grid_wa[gr, gc] = wa_m[i]
            grid_tot[gr, gc] = smc_col[i] + wa_m[i] + can_m[i] + sn_m[i]
            
        return float(np.sum(grid_smc * w)), float(np.sum(grid_wa * w)), float(np.sum(grid_tot * w))

print(">>> 1. Extraction annuelle des flux, stocks et incréments par bassin (2018)...")
annual_summary_records = []
ol_residuals = {}

for st_name in ["Lalla Chafia", "Sidi Jabeur"]:
    w = weights_181[st_name]
    m_catch = w > 0.0
    w_norm = w / np.sum(w[m_catch])
    
    for exp, cfg in EXPERIMENTS_2018.items():
        print(f"  Traitement {st_name} / {exp}...")
        exp_dir = cfg["dir"]
        if cfg["style"] == "hierarchical":
            all_hist = sorted(glob.glob(os.path.join(exp_dir, "output/*/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
        else:
            all_hist = sorted(glob.glob(os.path.join(exp_dir, "output/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
            
        hist_2018 = [f for f in all_hist if "201801020000" <= os.path.basename(f).replace("LIS_HIST_", "").replace(".d01.nc", "") <= "201901010000"]
        
        p_ann, et_ann, qs_ann, qsb_ann = 0.0, 0.0, 0.0, 0.0
        for f in hist_2018:
            with nc.Dataset(f) as ds:
                if cfg["has_p"]:
                    p_val = ds.variables["TotalPrecip_tavg"][:].squeeze() * 86400.0
                else:
                    # Unperturbed P from OPL
                    p_val = np.zeros((121, 181))
                et_val = ds.variables["Evap_tavg"][:].squeeze() * 86400.0
                qs_val = ds.variables["Qs_tavg"][:].squeeze() * 86400.0
                qsb_val = ds.variables["Qsb_tavg"][:].squeeze() * 86400.0
                
                p_ann += float(np.sum(p_val * w))
                et_ann += float(np.sum(et_val * w))
                qs_ann += float(np.sum(qs_val * w))
                qsb_ann += float(np.sum(qsb_val * w))
                
        if not cfg["has_p"]:
            # Remplacer P par la pluie unperturbed de OPL
            opl_dir = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")
            opl_hist = sorted(glob.glob(os.path.join(opl_dir, "output/*/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
            opl_2018 = [f for f in opl_hist if "201801020000" <= os.path.basename(f).replace("LIS_HIST_", "").replace(".d01.nc", "") <= "201901010000"]
            p_ann = 0.0
            for f in opl_2018:
                with nc.Dataset(f) as ds:
                    p_ann += float(np.sum(ds.variables["TotalPrecip_tavg"][:].squeeze() * 86400.0 * w))

        # Stocks
        smc0, wa0, s0 = read_storage_components(cfg["rst0"], w)
        smc1, wa1, s1 = read_storage_components(cfg["rst1"], w)
        d_smc = smc1 - smc0
        d_wa  = wa1 - wa0
        d_s   = s1 - s0
        
        # Incréments EnKF
        inc_ann = 0.0
        i1_ann, i2_ann, i3_ann, i4_ann = 0.0, 0.0, 0.0, 0.0
        if cfg["is_da"]:
            if cfg["style"] == "hierarchical":
                inc_files = sorted(glob.glob(os.path.join(exp_dir, "output/*/EnKF/*/*_incr.*.nc")))
            else:
                inc_files = sorted(glob.glob(os.path.join(exp_dir, "output/EnKF/*/*_incr.*.nc")))
            for f in inc_files:
                with nc.Dataset(f) as ds:
                    v1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
                    v2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
                    v3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
                    v4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
                    v1 = np.where(v1 == -9999.0, 0.0, v1)
                    v2 = np.where(v2 == -9999.0, 0.0, v2)
                    v3 = np.where(v3 == -9999.0, 0.0, v3)
                    v4 = np.where(v4 == -9999.0, 0.0, v4)
                    i1_ann += float(np.sum(v1 * w)) * dz[0] * 1000.0
                    i2_ann += float(np.sum(v2 * w)) * dz[1] * 1000.0
                    i3_ann += float(np.sum(v3 * w)) * dz[2] * 1000.0
                    i4_ann += float(np.sum(v4 * w)) * dz[3] * 1000.0
            inc_ann = i1_ann + i2_ann + i3_ann + i4_ann

        q_tot = qs_ann + qsb_ann
        res = p_ann - et_ann - q_tot - d_s + inc_ann
        
        if exp == "OL_DAIC":
            ol_residuals[st_name] = res

        annual_summary_records.append({
            "station": st_name,
            "experiment": exp,
            "P_mm": round(p_ann, 2),
            "ET_mm": round(et_ann, 2),
            "Qs_mm": round(qs_ann, 2),
            "Qsb_mm": round(qsb_ann, 2),
            "TotalRunoff_mm": round(q_tot, 2),
            "Delta_SMC_mm": round(d_smc, 2),
            "Delta_WA_mm": round(d_wa, 2),
            "Delta_S_mm": round(d_s, 2),
            "Incr_Layer1_mm": round(i1_ann, 2),
            "Incr_Layer2_mm": round(i2_ann, 2),
            "Incr_Layer3_mm": round(i3_ann, 2),
            "Incr_Layer4_mm": round(i4_ann, 2),
            "Incr_Total_mm": round(inc_ann, 2),
            "WaterBalance_Residual_mm": round(res, 2),
            "Delta_R_vs_OL_DAIC_mm": round(res - ol_residuals.get(st_name, 0.0), 2),
            "valid_closure_lt_1mm": abs(res) < 1.0
        })

df_ann = pd.DataFrame(annual_summary_records)
out_ann = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_annual_summary_2018.csv")
df_ann.to_csv(out_ann, index=False)
print(f"[OK] Sauvegardé {out_ann}")
print(df_ann.to_string())

print(">>> 2. Extraction des innovations et incréments mensuels pour DA_corr, DA_nocdf sur les deux bassins...")
innov_records = []
for st_name in ["Lalla Chafia", "Sidi Jabeur"]:
    w = weights_181[st_name]
    m_catch = w > 0.0
    w_norm = w / np.sum(w[m_catch])
    
    for da_exp in ["DA_corr", "DA_nocdf", "DA_nocdf_nowilt"]:
        cfg = EXPERIMENTS_2018[da_exp]
        exp_dir = cfg["dir"]
        
        all_innov_list = []
        n_obs_tot = 0
        i1_tot, i2_tot, i3_tot, i4_tot = 0.0, 0.0, 0.0, 0.0
        
        for m in range(1, 13):
            ym = f"2018{m:02d}"
            if cfg["style"] == "hierarchical":
                m_str = f"2018-{m:02d}"
                inv_files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_str}/EnKF/{ym}/*_innov.*.nc")))
                inc_files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_str}/EnKF/{ym}/*_incr.*.nc")))
            else:
                inv_files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/*_innov.*.nc")))
                inc_files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/*_incr.*.nc")))
                
            m_innovs = []
            n_obs_m = 0
            for f in inv_files:
                with nc.Dataset(f) as ds:
                    d = ds["innov_01"][:].squeeze()
                    valid = (d != -9999.0) & (~np.isnan(d)) & m_catch
                    if np.sum(valid) > 0:
                        n_obs_m += int(np.sum(valid))
                        m_innovs.extend(d[valid])
                        
            i1_m, i2_m, i3_m, i4_m = 0.0, 0.0, 0.0, 0.0
            for f in inc_files:
                with nc.Dataset(f) as ds:
                    v1 = np.where(ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze())
                    v2 = np.where(ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze())
                    v3 = np.where(ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze())
                    v4 = np.where(ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze())
                    i1_m += float(np.sum(v1 * w_norm))
                    i2_m += float(np.sum(v2 * w_norm))
                    i3_m += float(np.sum(v3 * w_norm))
                    i4_m += float(np.sum(v4 * w_norm))

            mean_inv_m = float(np.mean(m_innovs)) if len(m_innovs) > 0 else np.nan
            all_innov_list.extend(m_innovs)
            n_obs_tot += n_obs_m
            i1_tot += i1_m
            i2_tot += i2_m
            i3_tot += i3_m
            i4_tot += i4_m
            
            innov_records.append({
                "target": st_name,
                "experiment": da_exp,
                "period_type": "monthly_2018",
                "period": f"2018-{m:02d}",
                "n_obs_assimilated": n_obs_m,
                "mean_innovation_m3m3": round(mean_inv_m, 6) if not np.isnan(mean_inv_m) else np.nan,
                "incr_layer1_m3m3": round(i1_m, 6),
                "incr_layer2_m3m3": round(i2_m, 6),
                "incr_layer3_m3m3": round(i3_m, 6),
                "incr_layer4_m3m3": round(i4_m, 6),
                "incr_layer1_mm": round(i1_m * dz[0] * 1000.0, 4),
                "incr_layer2_mm": round(i2_m * dz[1] * 1000.0, 4),
                "incr_layer3_mm": round(i3_m * dz[2] * 1000.0, 4),
                "incr_layer4_mm": round(i4_m * dz[3] * 1000.0, 4),
                "incr_total_mm": round((i1_m*dz[0] + i2_m*dz[1] + i3_m*dz[2] + i4_m*dz[3]) * 1000.0, 4)
            })

        # Bilan annuel 2018
        mean_inv_ann = float(np.mean(all_innov_list)) if len(all_innov_list) > 0 else np.nan
        innov_records.append({
            "target": st_name,
            "experiment": da_exp,
            "period_type": "annual_2018",
            "period": "2018",
            "n_obs_assimilated": n_obs_tot,
            "mean_innovation_m3m3": round(mean_inv_ann, 6) if not np.isnan(mean_inv_ann) else np.nan,
            "incr_layer1_m3m3": round(i1_tot, 6),
            "incr_layer2_m3m3": round(i2_tot, 6),
            "incr_layer3_m3m3": round(i3_tot, 6),
            "incr_layer4_m3m3": round(i4_tot, 6),
            "incr_layer1_mm": round(i1_tot * dz[0] * 1000.0, 4),
            "incr_layer2_mm": round(i2_tot * dz[1] * 1000.0, 4),
            "incr_layer3_mm": round(i3_tot * dz[2] * 1000.0, 4),
            "incr_layer4_mm": round(i4_tot * dz[3] * 1000.0, 4),
            "incr_total_mm": round((i1_tot*dz[0] + i2_tot*dz[1] + i3_tot*dz[2] + i4_tot*dz[3]) * 1000.0, 4)
        })

df_innov = pd.DataFrame(innov_records)
out_innov = os.path.join(TABLES_DIR, "lalla_chafia_innovations_and_increments.csv")
df_innov.to_csv(out_innov, index=False)
print(f"[OK] Sauvegardé {out_innov}")

print(">>> TERMINÉ AVEC SUCCÈS !")
