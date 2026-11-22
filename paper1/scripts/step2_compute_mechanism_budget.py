#!/usr/bin/env python3
"""
Compute March 2018 mechanism water budget from instrumented runs.
Outputs:
  - paper1/tables/march2018_mechanism_budget.csv (overall domain summary per run)
  - paper1/tables/march2018_mechanism_by_theta1_class.csv (by m20 theta1 class on 01-03)
  - paper1/tables/march2018_mechanism_by_texture.csv (by dominant soil texture)
"""

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

REPO_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
DIAG_BASE = os.path.join(REPO_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech")
RYU_TEST_CSV = os.path.join(REPO_DIR, "paper1/tables/march2018_ryu_test.csv")
RST_PATH = os.path.join(REPO_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")
INPUT_NC = os.path.join(REPO_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

TEXTURE_NAMES = {
    1: "Sand",
    2: "Loamy Sand",
    3: "Sandy Loam",
    4: "Silt Loam",
    5: "Silt",
    6: "Loam",
    7: "Sandy Clay Loam",
    8: "Silty Clay Loam",
    9: "Clay Loam",
    10: "Sandy Clay",
    11: "Silty Clay",
    12: "Clay",
    13: "Organic material",
    14: "Water",
    15: "Bedrock",
    16: "Other"
}

RUNS = [
    {"name": "ENS_STATE_201803", "ryu_run_name": "STATE"},
    {"name": "ENS_STATE_201803_noRyu", "ryu_run_name": "STATE_noRyu"},
    {"name": "ENS_FORC_201803", "ryu_run_name": "FORC"},
    {"name": "ENS_FORC_201803_noRyu", "ryu_run_name": "FORC_noRyu"}
]

def load_cell_attributes():
    # Load theta1 of member 20 at 2018-03-01 00:00
    ds_rst = nc.Dataset(RST_PATH)
    lats = ds_rst.variables["lat"][:]
    lons = ds_rst.variables["lon"][:]
    smc = ds_rst.variables["SMC"][:] # (4, 12700)
    
    # 635 cells, m20 is index (i*20 + 19)
    m20_idx = np.arange(19, 12700, 20)
    theta1_m20 = smc[0, m20_idx] # (635,)
    
    cell_cols = np.round((lons[::20] - (-10.0)) / 0.05).astype(int) + 1
    cell_rows = np.round((lats[::20] - 30.0) / 0.05).astype(int) + 1
    ds_rst.close()
    
    # Load texture from lis_input
    ds_in = nc.Dataset(INPUT_NC)
    tex_3d = ds_in.variables["TEXTURE"][:] # (16, 121, 181)
    dom_tex = np.argmax(tex_3d, axis=0) + 1 # (121, 181)
    ds_in.close()
    
    cell_dict = {}
    for i in range(len(m20_idx)):
        col = cell_cols[i]
        row = cell_rows[i]
        th1 = theta1_m20[i]
        
        # Texture class (row-1, col-1 in 0-indexed python)
        tex_id = int(dom_tex[row - 1, col - 1])
        tex_name = TEXTURE_NAMES.get(tex_id, f"Tex_{tex_id}")
        
        # theta1 class
        if th1 < 0.05:
            th1_class = "< 0.05"
        elif th1 < 0.10:
            th1_class = "0.05-0.10"
        elif th1 < 0.20:
            th1_class = "0.10-0.20"
        else:
            th1_class = "> 0.20"
            
        cell_dict[(col, row)] = {
            "gid": i + 1,
            "col": col,
            "row": row,
            "theta1_m20": float(th1),
            "theta1_class": th1_class,
            "texture_id": tex_id,
            "texture_name": tex_name
        }
        
    return cell_dict

def parse_run_diagnostics(run_name, cell_dict):
    out_dir = os.path.join(DIAG_BASE, run_name, "output")
    files = sorted(glob.glob(os.path.join(out_dir, "mech_diag.*.txt")))
    if not files:
        print(f"[WARN] No diagnostic files found for {run_name} in {out_dir}")
        return None
        
    print(f"Parsing {len(files)} diagnostic files for {run_name}...")
    
    # Per-cell accumulators: (col, row) -> dict of sums
    cell_accum = {k: {
        "w_pert": 0.0,
        "w_ryu": 0.0,
        "w_qc": 0.0,
        "w_mid": 0.0,
        "w_rec": 0.0,
        "n_clip_low": 0,
        "n_clip_high": 0,
        "n_invalid": 0,
        "n_midrange": 0,
        "n_iter": 0
    } for k in cell_dict.keys()}
    
    for fpath in files:
        if os.path.getsize(fpath) == 0:
            continue
        with open(fpath, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 8:
                    continue
                rtype = parts[6]
                gid = int(parts[7])
                col = int(parts[8])
                row = int(parts[9])
                cell_key = (col, row)
                
                if cell_key not in cell_accum:
                    continue
                    
                acc = cell_accum[cell_key]
                
                if rtype == "PERT":
                    # parts: yr, mo, da, hr, mn, ss, 'PERT', gid, col, row, w_pert(1..4), w_ryu(1..4)
                    w_pert_tot = sum(float(parts[10 + j]) for j in range(4))
                    w_ryu_tot  = sum(float(parts[14 + j]) for j in range(4))
                    acc["w_pert"] += w_pert_tot
                    acc["w_ryu"]  += w_ryu_tot
                elif rtype == "QCSM":
                    # parts: yr, mo, da, hr, mn, ss, 'QCSM', gid, col, row, n_low, n_high, w_qc_l1
                    n_low = int(parts[10])
                    n_high = int(parts[11])
                    w_qc = float(parts[12])
                    acc["n_clip_low"] += n_low
                    acc["n_clip_high"] += n_high
                    acc["w_qc"] += w_qc
                elif rtype == "SETM":
                    # parts: yr, mo, da, hr, mn, ss, 'SETM', gid, col, row, n_inv, n_mid, w_mid(1..4), n_iter, w_rec(1..4)
                    n_inv = int(parts[10])
                    n_mid = int(parts[11])
                    w_mid_tot = sum(float(parts[12 + j]) for j in range(4))
                    n_it = int(parts[16])
                    w_rec_tot = sum(float(parts[17 + j]) for j in range(4))
                    acc["n_invalid"] += n_inv
                    acc["n_midrange"] += n_mid
                    acc["w_mid"] += w_mid_tot
                    acc["n_iter"] += n_it
                    acc["w_rec"] += w_rec_tot
                    
    # Build cell DataFrame
    records = []
    for cell_key, acc in cell_accum.items():
        attr = cell_dict[cell_key]
        records.append({
            "gid": attr["gid"],
            "col": attr["col"],
            "row": attr["row"],
            "theta1_class": attr["theta1_class"],
            "texture_id": attr["texture_id"],
            "texture_name": attr["texture_name"],
            "w_pert": acc["w_pert"],
            "w_ryu": acc["w_ryu"],
            "w_qc": acc["w_qc"],
            "w_mid": acc["w_mid"],
            "w_rec": acc["w_rec"],
            "w_sum": acc["w_pert"] + acc["w_ryu"] + acc["w_qc"] + acc["w_mid"] + acc["w_rec"]
        })
    return pd.DataFrame(records)

def main():
    cell_dict = load_cell_attributes()
    
    # Load Residu R from march2018_ryu_test.csv
    df_ryu = pd.read_csv(RYU_TEST_CSV)
    r_dict = dict(zip(df_ryu["run"], df_ryu["Residu_mm"]))
    
    overall_rows = []
    th1_rows = []
    tex_rows = []
    
    for r in RUNS:
        run_name = r["name"]
        ryu_name = r["ryu_run_name"]
        residu_R = r_dict.get(ryu_name, np.nan)
        
        df_cells = parse_run_diagnostics(run_name, cell_dict)
        if df_cells is None:
            overall_rows.append({
                "run": run_name,
                "status": "RUNNING_OR_PENDING",
                "R_mm": residu_R,
                "minus_R_mm": -residu_R if pd.notnull(residu_R) else np.nan,
                "w_pert_mm": np.nan,
                "w_ryu_mm": np.nan,
                "w_qc_mm": np.nan,
                "w_mid_mm": np.nan,
                "w_rec_mm": np.nan,
                "w_sum_mm": np.nan,
                "gap_minusR_minus_sum_mm": np.nan
            })
            continue
            
        # Domain mean (sum / 635)
        n_tot = len(df_cells)
        w_pert = df_cells["w_pert"].mean()
        w_ryu  = df_cells["w_ryu"].mean()
        w_qc   = df_cells["w_qc"].mean()
        w_mid  = df_cells["w_mid"].mean()
        w_rec  = df_cells["w_rec"].mean()
        w_sum  = w_pert + w_ryu + w_qc + w_mid + w_rec
        minus_R = -residu_R
        gap = minus_R - w_sum
        
        overall_rows.append({
            "run": run_name,
            "status": "COMPLETED",
            "R_mm": round(residu_R, 4),
            "minus_R_mm": round(minus_R, 4),
            "w_pert_mm": round(w_pert, 4),
            "w_ryu_mm": round(w_ryu, 4),
            "w_qc_mm": round(w_qc, 4),
            "w_mid_mm": round(w_mid, 4),
            "w_rec_mm": round(w_rec, 4),
            "w_sum_mm": round(w_sum, 4),
            "gap_minusR_minus_sum_mm": round(gap, 4)
        })
        
        # Breakdown by theta1 class
        for th_cls, grp in df_cells.groupby("theta1_class"):
            th1_rows.append({
                "run": run_name,
                "theta1_class": th_cls,
                "n_cells": len(grp),
                "w_pert_mm": round(grp["w_pert"].mean(), 4),
                "w_ryu_mm": round(grp["w_ryu"].mean(), 4),
                "w_qc_mm": round(grp["w_qc"].mean(), 4),
                "w_mid_mm": round(grp["w_mid"].mean(), 4),
                "w_rec_mm": round(grp["w_rec"].mean(), 4),
                "w_sum_mm": round(grp["w_sum"].mean(), 4)
            })
            
        # Breakdown by texture
        for tex_name, grp in df_cells.groupby("texture_name"):
            tex_rows.append({
                "run": run_name,
                "texture": tex_name,
                "n_cells": len(grp),
                "w_pert_mm": round(grp["w_pert"].mean(), 4),
                "w_ryu_mm": round(grp["w_ryu"].mean(), 4),
                "w_qc_mm": round(grp["w_qc"].mean(), 4),
                "w_mid_mm": round(grp["w_mid"].mean(), 4),
                "w_rec_mm": round(grp["w_rec"].mean(), 4),
                "w_sum_mm": round(grp["w_sum"].mean(), 4)
            })
            
    df_overall = pd.DataFrame(overall_rows)
    df_th1 = pd.DataFrame(th1_rows)
    df_tex = pd.DataFrame(tex_rows)
    
    out_csv = os.path.join(REPO_DIR, "paper1/tables/march2018_mechanism_budget.csv")
    out_th1 = os.path.join(REPO_DIR, "paper1/tables/march2018_mechanism_by_theta1_class.csv")
    out_tex = os.path.join(REPO_DIR, "paper1/tables/march2018_mechanism_by_texture.csv")
    
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df_overall.to_csv(out_csv, index=False)
    df_th1.to_csv(out_th1, index=False)
    df_tex.to_csv(out_tex, index=False)
    
    print(f"Overall mechanism budget written to: {out_csv}")
    print(df_overall.to_string())
    if not df_th1.empty:
        print(f"\nBy theta1 class written to: {out_th1}")
    if not df_tex.empty:
        print(f"\nBy texture written to: {out_tex}")

if __name__ == "__main__":
    main()
