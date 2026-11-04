#!/usr/bin/env python3
"""
mass_balance_2018.py
Calcul du bilan de masse hydrologique annuel complet sur l'annee 2018 (365 jours)
pour la simulation OPL continue 2016-2020.
Formule fixee en 1c:
  Vin = somme_jours somme_mailles (Qs + Qsb) * 1e-3 * HYMAP_grid_area * 86400
  Vout = somme_jours Q_exutoire * 86400
  DeltaS = S(2018-12-31 23:45) - S(2017-12-31 23:45) via fichiers RST
"""

import os
import glob
import csv
import netCDF4 as nc
import numpy as np

def main():
    csv_path = "experiments/NorthMor/routing/stations/stations.csv"
    ldt_path = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
    rst_start_path = "experiments/NorthMor/routing/output/OPL_2016_2020/ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc"
    rst_end_path = "experiments/NorthMor/routing/output/OPL_2016_2020/ROUTING/201812/LIS_RST_HYMAP2_router_201812312345.d01.nc"
    runoff_dir = "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"
    routing_dir = "experiments/NorthMor/routing/output/OPL_2016_2020/ROUTING"

    # 1. Charger LDT et reconstituer l'arborescence
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0) # (120, 180)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    ds_ldt.close()

    # Reconstituer down_r, down_c
    down_r = np.full((120, 180), -1, dtype=int)
    down_c = np.full((120, 180), -1, dtype=int)
    seqx = []
    seqy = []
    for c in range(180):
        for r in range(120):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                seqx.append(c)
                seqy.append(r)
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

    # 2. Lire l'appariement des 9 stations
    stations = []
    pairing_csv = "experiments/NorthMor/routing/output/OPL_201801/stations_hymap_pairing.csv"
    with open(pairing_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations.append({
                "nom": row["nom"],
                "row": int(row["row_hymap"]),
                "col": int(row["col_hymap"]),
                "aire_off": float(row["aire_off_km2"]) if row["aire_off_km2"] else None,
                "aire_hymap": float(row["aire_hymap_km2"])
            })

    basin_masks = {}
    for st in stations:
        basin_masks[st["nom"]] = get_basin_mask(st["row"], st["col"])

    # 3. Calcul de Vin sur 2018 (365 jours)
    print("Calcul de Vin sur 2018 (365 jours)...")
    runoff_files = sorted(glob.glob(os.path.join(runoff_dir, "2018*/*.nc")))
    print(f"Trouve {len(runoff_files)} fichiers de ruissellement pour 2018")
    assert len(runoff_files) == 365, f"Attendu 365 fichiers, trouve {len(runoff_files)}"

    Vin = {st["nom"]: 0.0 for st in stations}
    for rf in runoff_files:
        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds["Qs_tavg"][:])
            qsb = np.nan_to_num(ds["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]
            daily_vol = (np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0
            for st in stations:
                Vin[st["nom"]] += np.sum(daily_vol[basin_masks[st["nom"]]])

    # 4. Calcul de Vout sur 2018 (365 jours)
    print("Calcul de Vout sur 2018 (365 jours)...")
    routing_files = sorted(glob.glob(os.path.join(routing_dir, "2018*/LIS_HIST_*.d01.nc")))
    print(f"Trouve {len(routing_files)} fichiers de routage pour 2018")
    assert len(routing_files) == 365, f"Attendu 365 fichiers de routage, trouve {len(routing_files)}"

    Vout = {st["nom"]: 0.0 for st in stations}
    for hf in routing_files:
        with nc.Dataset(hf) as ds:
            flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if flow.ndim == 3: flow = flow[0]
            for st in stations:
                r, c = st["row"], st["col"]
                Vout[st["nom"]] += float(flow[r, c]) * 86400.0

    # 5. Calcul de Delta S via les fichiers RST
    print("Calcul de Delta S via fichiers RST 20171231 et 20181231...")
    def load_rst_2d(rst_path):
        with nc.Dataset(rst_path) as ds:
            riv = ds["RIVSTO"][:]
            fld = ds["FLDSTO"][:]
            rnf = ds["RNFSTO"][:]
            bsf = ds["BSFSTO"][:]
            
            riv_val = np.where(riv > 0, riv, 0.0)
            fld_val = np.where(fld > 0, fld, 0.0)
            rnf_val = np.where(rnf > 0, rnf, 0.0)
            bsf_val = np.where(bsf > 0, bsf, 0.0)
            tot_1d = riv_val + fld_val + rnf_val + bsf_val
            
            tot_2d = np.zeros((120, 180), dtype=np.float64)
            for i in range(len(seqx)):
                r = seqy[i]
                c = seqx[i]
                tot_2d[r, c] = tot_1d[i]
            return tot_2d

    S_start_2d = load_rst_2d(rst_start_path)
    S_end_2d = load_rst_2d(rst_end_path)

    DeltaS = {}
    for st in stations:
        mask = basin_masks[st["nom"]]
        s0 = np.sum(S_start_2d[mask])
        s1 = np.sum(S_end_2d[mask])
        DeltaS[st["nom"]] = s1 - s0

    # 6. Afficher et sauvegarder la table de bilan
    print("\n" + "="*95)
    print("TABLE DU BILAN DE MASSE ANNUEL 2018 (RUN OPL CONTINU 2016-2020) :")
    print("="*95)
    header = f"{'Bassin':16s} | {'Vin (hm3)':10s} | {'Vout (hm3)':10s} | {'DeltaS (hm3)':12s} | {'Vout+DeltaS':11s} | {'Ecart (hm3)':11s} | {'Erreur (%)':10s}"
    print(header)
    print("-"*95)

    res_table = []
    for st in stations:
        nom = st["nom"]
        vin_hm3 = Vin[nom] / 1e6
        vout_hm3 = Vout[nom] / 1e6
        ds_hm3 = DeltaS[nom] / 1e6
        sum_out = vout_hm3 + ds_hm3
        ecart = vin_hm3 - sum_out
        err_pct = (ecart / vin_hm3 * 100.0) if vin_hm3 > 0 else 0.0
        
        row_str = f"{nom:16s} | {vin_hm3:10.2f} | {vout_hm3:10.2f} | {ds_hm3:+12.2f} | {sum_out:11.2f} | {ecart:+11.3f} | {err_pct:+9.2f}%"
        print(row_str)
        res_table.append({
            "nom": nom,
            "Vin_hm3": vin_hm3,
            "Vout_hm3": vout_hm3,
            "DeltaS_hm3": ds_hm3,
            "Vout_plus_DeltaS_hm3": sum_out,
            "Ecart_hm3": ecart,
            "Erreur_pct": err_pct
        })
    print("="*95)

    # Sauvegarder dans CSV
    out_csv = "experiments/NorthMor/routing/output/OPL_2016_2020/mass_balance_2018.csv"
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nom", "Vin_hm3", "Vout_hm3", "DeltaS_hm3", "Vout_plus_DeltaS_hm3", "Ecart_hm3", "Erreur_pct"])
        writer.writeheader()
        writer.writerows(res_table)
    print(f"Table sauvegardee dans : {out_csv}")

if __name__ == "__main__":
    main()
