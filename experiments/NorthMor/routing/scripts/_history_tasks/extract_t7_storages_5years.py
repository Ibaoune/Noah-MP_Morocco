#!/usr/bin/env python3
"""
extract_t7_storages_5years.py
Tâche 7 - Etape 1 :
1. Extraction des séries temporelles journalières des 4 composantes de stock du domaine :
   - RIVSTO (RiverStor_tavg)
   - FLDSTO (FloodStor_tavg)
   - RNFSTO (RunoffStor_tavg)
   - BSFSTO (BaseflowStor_tavg)
   sur les 1827 jours de la simulation OPL 2016-2020.
2. Calcul des pentes annuelles (hm3/an) de chacun des 4 stocks.
3. Calcul du ratio Qsb / (Qs + Qsb) du ruissellement Noah-MP par bassin et comparaison à (1 - Vsim/Vin).
4. Production du graphique t7_storages_5years_timeseries.png et des fichiers CSV associés.
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import linregress

def main():
    base_dir = "experiments/NorthMor/routing"
    routing_dir = os.path.join(base_dir, "output/OPL_2016_2020/ROUTING")
    runoff_dir = os.path.join(base_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL")
    ldt_path = os.path.join(base_dir, "ldt_hymap/lis_input.d01.nc")
    pairing_csv = os.path.join(base_dir, "output/OPL_2016_2020/t5bis_stations_pairing.csv")
    t6_decomp_csv = os.path.join(base_dir, "output/OPL_2016_2020/t6_three_volumes_decomposition.csv")
    out_dir = os.path.join(base_dir, "output/OPL_2016_2020")
    plot_dir = os.path.join(base_dir, "plots")
    os.makedirs(plot_dir, exist_ok=True)

    # =========================================================================
    # 1. EXTRACTION DES STOCKS DU DOMAINE (1827 JOURS)
    # =========================================================================
    print("=" * 80)
    print("1. EXTRACTION DES STOCKS DU DOMAINE SUR 2016-2020 (1827 SORTIES)")
    print("=" * 80)
    daily_csv = os.path.join(out_dir, "t7_domain_storages_daily.csv")
    
    if os.path.exists(daily_csv):
        print(f"Chargement depuis cache existant : {daily_csv}")
        df_stocks = pd.read_csv(daily_csv)
        df_stocks["date"] = pd.to_datetime(df_stocks["date"])
    else:
        hist_files = sorted(glob.glob(os.path.join(routing_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))
        print(f"Nombre de fichiers LIS_HIST trouves : {len(hist_files)}")
        assert len(hist_files) == 1827, f"Attendu 1827 fichiers, trouve {len(hist_files)}"

        records = []
        for idx, fpath in enumerate(hist_files):
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                sim_date_str = sim_dt.strftime("%Y-%m-%d")

                riv = np.sum(np.maximum(np.nan_to_num(ds["RiverStor_tavg"][:]), 0.0)) / 1e6 # hm3
                fld = np.sum(np.maximum(np.nan_to_num(ds["FloodStor_tavg"][:]), 0.0)) / 1e6 # hm3
                rnf = np.sum(np.maximum(np.nan_to_num(ds["RunoffStor_tavg"][:]), 0.0)) / 1e6 # hm3
                bsf = np.sum(np.maximum(np.nan_to_num(ds["BaseflowStor_tavg"][:]), 0.0)) / 1e6 # hm3

                tot = riv + fld + rnf + bsf
                records.append({
                    "date": sim_date_str,
                    "RIVSTO_hm3": riv,
                    "FLDSTO_hm3": fld,
                    "RNFSTO_hm3": rnf,
                    "BSFSTO_hm3": bsf,
                    "TOTAL_hm3": tot
                })

            if (idx + 1) % 365 == 0:
                print(f"  Progression : {idx + 1}/{len(hist_files)} jours extraits...")

        df_stocks = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        df_stocks.to_csv(daily_csv, index=False)
        df_stocks["date"] = pd.to_datetime(df_stocks["date"])
        print(f"Extraction terminee et sauvegardee dans {daily_csv}")

    # =========================================================================
    # 2. CALCUL DES PENTES ANNUELLES ET STATISTIQUES DE STATIONNARITE
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. PENTES ANNUELLES ET TENDANCES DES STOCKS (2016-2020)")
    print("=" * 80)
    
    n_days = len(df_stocks)
    t_days = np.arange(n_days)

    slopes = {}
    for col in ["RIVSTO_hm3", "FLDSTO_hm3", "RNFSTO_hm3", "BSFSTO_hm3", "TOTAL_hm3"]:
        res = linregress(t_days, df_stocks[col])
        slope_per_year = res.slope * 365.25 # hm3/an
        val_start = df_stocks[col].iloc[0]
        val_end = df_stocks[col].iloc[-1]
        delta_net = val_end - val_start
        mean_val = df_stocks[col].mean()
        slopes[col] = {
            "start_hm3": val_start,
            "end_hm3": val_end,
            "delta_net_hm3": delta_net,
            "mean_hm3": mean_val,
            "slope_hm3_an": slope_per_year,
            "r2": res.rvalue**2,
            "pvalue": res.pvalue
        }

    print(f"{'Stock':12s} | {'Debut (hm3)':12s} | {'Fin (hm3)':12s} | {'Delta net (hm3)':15s} | {'Pente (hm3/an)':15s} | {'R2':8s} | {'Stationnaire ?'}")
    print("-" * 88)
    for col in ["RIVSTO_hm3", "FLDSTO_hm3", "RNFSTO_hm3", "BSFSTO_hm3", "TOTAL_hm3"]:
        s = slopes[col]
        is_stat = "OUI (stationnaire)" if abs(s["slope_hm3_an"]) < 50.0 else "NON (Puits accumulateur)"
        print(f"{col:12s} | {s['start_hm3']:12.2f} | {s['end_hm3']:12.2f} | {s['delta_net_hm3']:+15.2f} | {s['slope_hm3_an']:+15.2f} | {s['r2']:8.4f} | {is_stat}")
    print("=" * 88)

    # =========================================================================
    # 3. CALCUL DU RATIO Qsb / (Qs + Qsb) PAR BASSIN ET COMPARAISON A 1 - Vsim/Vin
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. COMPARAISON DU RATIO SOUTERRAIN Qsb/(Qs+Qsb) A LA RETENTION (1 - Vsim/Vin)")
    print("=" * 80)

    # Charger LDT pour grille et drainage
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0) # (120, 180)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    R, C = flow_x.shape
    ds_ldt.close()

    down_r = np.full((R, C), -1, dtype=int)
    down_c = np.full((R, C), -1, dtype=int)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx = int(round(flow_x[r, c]))
                vy = int(round(flow_y[r, c]))
                if 1 <= vx <= C and 1 <= vy <= R:
                    down_c[r, c] = vx - 1
                    down_r[r, c] = vy - 1

    parents = {}
    for r in range(R):
        for c in range(C):
            pr, pc = down_r[r, c], down_c[r, c]
            if pr >= 0 and pc >= 0:
                if (pr, pc) not in parents:
                    parents[(pr, pc)] = []
                parents[(pr, pc)].append((r, c))

    def get_catchment(outlet_r, outlet_c):
        visited = set()
        queue = [(outlet_r, outlet_c)]
        visited.add((outlet_r, outlet_c))
        while queue:
            curr = queue.pop(0)
            if curr in parents:
                for parent in parents[curr]:
                    if parent not in visited:
                        visited.add(parent)
                        queue.append(parent)
        return visited

    df_p = pd.read_csv(pairing_csv)
    station_masks = {}
    for _, row in df_p.iterrows():
        sid = row["station_id"]
        r, c = int(row["row_hymap"]), int(row["col_hymap"])
        cat = get_catchment(r, c)
        mask = np.zeros((R, C), dtype=bool)
        for cr, cc in cat:
            mask[cr, cc] = True
        station_masks[sid] = mask

    runoff_files = sorted(glob.glob(os.path.join(runoff_dir, "*/*.nc")))
    print(f"Extraction des flux 5 ans Qs et Qsb depuis {len(runoff_files)} fichiers de ruissellement...")

    v_qs_5y = {sid: 0.0 for sid in station_masks}
    v_qsb_5y = {sid: 0.0 for sid in station_masks}

    for idx, rf in enumerate(runoff_files):
        fname = os.path.basename(rf)
        dt_str = fname.replace("LIS_HIST_", "").replace("0000.d01.nc", "")
        file_dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
        sim_dt = file_dt - datetime.timedelta(days=1)
        sim_date_str = sim_dt.strftime("%Y-%m-%d")
        if sim_date_str < "2016-01-01" or sim_date_str > "2020-12-31":
            continue

        with nc.Dataset(rf) as ds:
            qs = np.nan_to_num(ds.variables["Qs_tavg"][:])
            qsb = np.nan_to_num(ds.variables["Qsb_tavg"][:])
            if qs.ndim == 3: qs = qs[0]
            if qsb.ndim == 3: qsb = qsb[0]

            qs_vol = np.maximum(qs, 0.0) * 1e-3 * grid_area * 86400.0
            qsb_vol = np.maximum(qsb, 0.0) * 1e-3 * grid_area * 86400.0

            for sid, mask in station_masks.items():
                v_qs_5y[sid] += np.sum(qs_vol[mask])
                v_qsb_5y[sid] += np.sum(qsb_vol[mask])

        if (idx + 1) % 365 == 0:
            print(f"  Ruissellement traite : {idx + 1}/{len(runoff_files)} jours...")

    df_t6 = pd.read_csv(t6_decomp_csv)
    df_t6_5y = df_t6[df_t6["periode"] == "2016-2020"].copy()

    qsb_records = []
    for _, row in df_t6_5y.iterrows():
        sid = row["station_id"]
        nom = row["nom"]
        bassin = row["bassin"]
        v_qs_hm3 = v_qs_5y[sid] / 1e6
        v_qsb_hm3 = v_qsb_5y[sid] / 1e6
        vin_calc_hm3 = v_qs_hm3 + v_qsb_hm3
        ratio_qsb = v_qsb_hm3 / vin_calc_hm3 if vin_calc_hm3 > 0 else 0.0

        vsim_sur_vin = row["Vsim_sur_Vin"]
        perte_routage = 1.0 - vsim_sur_vin
        diff_abs = abs(ratio_qsb - perte_routage)

        qsb_records.append({
            "station_id": sid,
            "nom": nom,
            "bassin": bassin,
            "aire_km2": row["aire_km2"],
            "V_Qs_hm3": v_qs_hm3,
            "V_Qsb_hm3": v_qsb_hm3,
            "Vin_hm3": vin_calc_hm3,
            "Ratio_Qsb_sur_Vin": ratio_qsb,
            "Vsim_sur_Vin": vsim_sur_vin,
            "Perte_1_moins_VsimVin": perte_routage,
            "Difference": diff_abs
        })

    df_qsb = pd.DataFrame(qsb_records)
    out_qsb_csv = os.path.join(out_dir, "t7_qsb_ratio_catchments.csv")
    df_qsb.to_csv(out_qsb_csv, index=False)
    print(f"\nTable Qsb/(Qs+Qsb) vs (1 - Vsim/Vin) sauvegardee dans : {out_qsb_csv}")

    print("\n" + "=" * 105)
    print(f"{'Station':16s} | {'Bassin':10s} | {'Qs (hm3)':10s} | {'Qsb (hm3)':10s} | {'Qsb/(Qs+Qsb)':13s} | {'1 - Vsim/Vin':13s} | {'Ecart':10s}")
    print("-" * 105)
    for _, r in df_qsb.iterrows():
        print(f"{r['nom']:16s} | {r['bassin']:10s} | {r['V_Qs_hm3']:10.2f} | {r['V_Qsb_hm3']:10.2f} | {r['Ratio_Qsb_sur_Vin']*100:11.2f} % | {r['Perte_1_moins_VsimVin']*100:11.2f} % | {r['Difference']*100:8.2f} %")
    print("=" * 105)

    # =========================================================================
    # 4. GRAPHIQUE DES SERIES TEMPORELLES DES STOCKS DU DOMAINE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. TRACE DU GRAPHIQUE DES 4 STOCKS DU DOMAINE")
    print("=" * 80)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)

    ax1 = axes[0]
    ax1.plot(df_stocks["date"].dt.to_pydatetime(), df_stocks["BSFSTO_hm3"].to_numpy(), color="#8B0000", lw=2.2, label=f"BSFSTO (Stock Nappe) — Pente: {slopes['BSFSTO_hm3']['slope_hm3_an']:+.1f} hm3/an (R2={slopes['BSFSTO_hm3']['r2']:.3f})")
    ax1.plot(df_stocks["date"].dt.to_pydatetime(), df_stocks["TOTAL_hm3"].to_numpy(), color="#2F4F4F", lw=1.5, ls="--", label=f"Stock Total (RIV+FLD+RNF+BSF) — Pente: {slopes['TOTAL_hm3']['slope_hm3_an']:+.1f} hm3/an")
    ax1.set_ylabel("Volume de nappe (hm3)", fontsize=11, fontweight="bold", color="#8B0000")
    ax1.set_title("A. Dynamique de la nappe souterraine (BSFSTO) : Croissance monotone quasi-lineaire (Unique Puits)", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.35, ls=":")
    ax1.legend(loc="upper left", framealpha=0.9)

    ax2 = axes[1]
    ax2.plot(df_stocks["date"].dt.to_pydatetime(), df_stocks["RIVSTO_hm3"].to_numpy(), color="#1E90FF", lw=1.8, label=f"RIVSTO (Chenal) — Moyenne: {slopes['RIVSTO_hm3']['mean_hm3']:.1f} hm3, Pente: {slopes['RIVSTO_hm3']['slope_hm3_an']:+.2f} hm3/an")
    ax2.plot(df_stocks["date"].dt.to_pydatetime(), df_stocks["FLDSTO_hm3"].to_numpy(), color="#2E8B57", lw=1.8, label=f"FLDSTO (Plaine) — Moyenne: {slopes['FLDSTO_hm3']['mean_hm3']:.1f} hm3, Pente: {slopes['FLDSTO_hm3']['slope_hm3_an']:+.2f} hm3/an")
    ax2.plot(df_stocks["date"].dt.to_pydatetime(), df_stocks["RNFSTO_hm3"].to_numpy(), color="#FF8C00", lw=1.8, label=f"RNFSTO (Surface rapide) — Moyenne: {slopes['RNFSTO_hm3']['mean_hm3']:.1f} hm3, Pente: {slopes['RNFSTO_hm3']['slope_hm3_an']:+.2f} hm3/an")
    
    comb_surf = df_stocks["RIVSTO_hm3"].to_numpy() + df_stocks["FLDSTO_hm3"].to_numpy() + df_stocks["RNFSTO_hm3"].to_numpy()
    comb_slope = slopes['RIVSTO_hm3']['slope_hm3_an'] + slopes['FLDSTO_hm3']['slope_hm3_an'] + slopes['RNFSTO_hm3']['slope_hm3_an']
    ax2.plot(df_stocks["date"].dt.to_pydatetime(), comb_surf, color="#4B0082", lw=2.0, ls="-.", label=f"Surface Totale (RIV+FLD+RNF) — Moyenne: {comb_surf.mean():.1f} hm3, Pente: {comb_slope:+.2f} hm3/an")

    ax2.set_ylabel("Volume de surface & chenal (hm3)", fontsize=11, fontweight="bold", color="#1E90FF")
    ax2.set_xlabel("Date (2016-2020)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Dynamique des reservoirs de surface et chenal : Stationnarite et cycles saisonniers fermes", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.35, ls=":")
    ax2.legend(loc="upper left", framealpha=0.9)

    plt.tight_layout()
    plot_path = os.path.join(plot_dir, "t7_storages_5years_timeseries.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"Graphique sauvegarde : {plot_path}")

if __name__ == "__main__":
    main()
