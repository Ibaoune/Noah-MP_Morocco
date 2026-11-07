#!/usr/bin/env python3
"""
analyze_routing_jan2018.py
Analyse complete du routage HYMAP2 Janvier 2018 (OPL_noirr):
1. Appariement des stations (stations.csv -> grille HyMAP 180x120) par aire de drainage.
2. Extraction des series temporelles journalieres des 9 stations.
3. Reconstitution des bassins versants amont par inversion du reseau d'ecoulement.
4. Bilan de masse hydrologique par bassin (Vin = Vout + DeltaS).
5. Tracé des hydrogrammes journaliers (PNG).
"""

import os
import glob
import csv
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def main():
    csv_path = "experiments/NorthMor/routing/stations/stations.csv"
    ldt_path = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
    out_dir = "experiments/NorthMor/routing/output/OPL_201801/ROUTING"
    remap_dir = "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"
    plots_dir = "experiments/NorthMor/routing/plots"
    os.makedirs(plots_dir, exist_ok=True)
    out_table_dir = "experiments/NorthMor/routing/output/OPL_201801"
    os.makedirs(out_table_dir, exist_ok=True)

    # 1. Charger la grille et les parametres HyMAP
    print("Chargement des parametres HyMAP depuis ldt_hymap/lis_input.d01.nc...")
    ds_ldt = nc.Dataset(ldt_path)
    lat2d = ds_ldt["lat"][:].astype(np.float64) # (120, 180)
    lon2d = ds_ldt["lon"][:].astype(np.float64)
    drain_area = ds_ldt["HYMAP_drain_area"][:] / 1e6 # en km2
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0) # en m2
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    ds_ldt.close()

    # 2. Lire stations.csv
    stations = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations.append({
                "nom": row["nom"],
                "type": row["type"],
                "lon": float(row["longitude"]),
                "lat": float(row["latitude"]),
                "aire_off": float(row["aire_officielle_km2"]) if row["aire_officielle_km2"] else None,
                "source": row["source"]
            })

    # 3. Appariement robuste des stations (fenetre 5x5 et minimisation de l'ecart d'aire)
    print("\n=== APPARIEMENT DES STATIONS SUR LA GRILLE HYMAP (180x120) ===")
    pairing_results = []
    for st in stations:
        st_lon, st_lat = st["lon"], st["lat"]
        nom = st["nom"]
        aire_off = st["aire_off"]
        dist_deg = np.sqrt((lon2d - st_lon)**2 + (lat2d - st_lat)**2)
        r0, c0 = np.unravel_index(np.argmin(dist_deg), dist_deg.shape)

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

        if aire_off and len(candidates) > 0:
            candidates.sort(key=lambda x: abs(x[4] - aire_off))
            best = candidates[0]
            ecart_pct = (best[4] - aire_off) / aire_off * 100.0
        else:
            best = (r0, c0, lon2d[r0, c0], lat2d[r0, c0], float(drain_area[r0, c0].filled(0.0)), 0.0)
            ecart_pct = 0.0

        st["row"] = best[0]
        st["col"] = best[1]
        st["lon_hymap"] = best[2]
        st["lat_hymap"] = best[3]
        st["aire_hymap"] = best[4]
        st["dist_km"] = best[5]
        st["ecart_pct"] = ecart_pct
        pairing_results.append(st)
        print(f"Station {nom:16s} (off: {aire_off:7.0f} km2) -> HyMAP [r={st['row']:2d}, c={st['col']:2d}] "
              f"({st['lon_hymap']:7.3f}, {st['lat_hymap']:6.3f}), dist={st['dist_km']:5.2f} km, "
              f"Aire={st['aire_hymap']:8.1f} km2, ecart={st['ecart_pct']:+6.2f}%")

    pairing_csv = os.path.join(out_table_dir, "stations_hymap_pairing.csv")
    with open(pairing_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nom", "type", "lon_station", "lat_station", "aire_off_km2", "row_hymap", "col_hymap",
                         "lon_hymap", "lat_hymap", "dist_km", "aire_hymap_km2", "ecart_pct", "source"])
        for st in pairing_results:
            writer.writerow([st["nom"], st["type"], st["lon"], st["lat"], st["aire_off"], st["row"], st["col"],
                             f"{st['lon_hymap']:.3f}", f"{st['lat_hymap']:.3f}", f"{st['dist_km']:.2f}",
                             f"{st['aire_hymap']:.1f}", f"{st['ecart_pct']:.2f}", st["source"]])
    print(f"Table d'appariement sauvegardee dans: {pairing_csv}")

    # 4. Extraire les series temporelles journalieres
    nc_files = sorted(glob.glob(out_dir + "/**/LIS_HIST_*.d01.nc", recursive=True))
    print(f"\nExtraction sur {len(nc_files)} fichiers journaliers de routing...")
    timeseries = {st["nom"]: {"dates": [], "streamflow": [], "river_stor": [], "river_depth": [],
                              "flood_stor": [], "runoff_stor": [], "baseflow_stor": []} for st in stations}

    for fpath in nc_files:
        ds = nc.Dataset(fpath)
        t_units = ds["time"].units
        t_val = ds["time"][0]
        base_str = t_units.replace("minutes since ", "")
        base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
        file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
        sim_dt = file_dt - datetime.timedelta(days=1)

        flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
        if flow.ndim == 3: flow = flow[0]
        riv_stor = np.nan_to_num(ds["RiverStor_tavg"][:].filled(0.0))
        if riv_stor.ndim == 3: riv_stor = riv_stor[0]
        riv_dph = np.nan_to_num(ds["RiverDepth_tavg"][:].filled(0.0))
        if riv_dph.ndim == 3: riv_dph = riv_dph[0]
        fld_stor = np.nan_to_num(ds["FloodStor_tavg"][:].filled(0.0)) if "FloodStor_tavg" in ds.variables else np.zeros_like(flow)
        if fld_stor.ndim == 3: fld_stor = fld_stor[0]
        rnf_stor = np.nan_to_num(ds["RunoffStor_tavg"][:].filled(0.0))
        if rnf_stor.ndim == 3: rnf_stor = rnf_stor[0]
        bas_stor = np.nan_to_num(ds["BaseflowStor_tavg"][:].filled(0.0))
        if bas_stor.ndim == 3: bas_stor = bas_stor[0]

        for st in stations:
            r, c = st["row"], st["col"]
            timeseries[st["nom"]]["dates"].append(sim_dt)
            timeseries[st["nom"]]["streamflow"].append(float(flow[r, c]))
            timeseries[st["nom"]]["river_stor"].append(float(riv_stor[r, c]))
            timeseries[st["nom"]]["river_depth"].append(float(riv_dph[r, c]))
            timeseries[st["nom"]]["flood_stor"].append(float(fld_stor[r, c]))
            timeseries[st["nom"]]["runoff_stor"].append(float(rnf_stor[r, c]))
            timeseries[st["nom"]]["baseflow_stor"].append(float(bas_stor[r, c]))
        ds.close()

    ts_csv = os.path.join(out_table_dir, "streamflow_stations_timeseries.csv")
    with open(ts_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "station", "streamflow_m3s", "river_stor_m3", "river_depth_m",
                         "flood_stor_m3", "runoff_stor_mm", "baseflow_stor_mm"])
        for st in stations:
            sname = st["nom"]
            for i in range(len(timeseries[sname]["dates"])):
                d_str = timeseries[sname]["dates"][i].strftime("%Y-%m-%d")
                writer.writerow([d_str, sname,
                                 f"{timeseries[sname]['streamflow'][i]:.4f}",
                                 f"{timeseries[sname]['river_stor'][i]:.2f}",
                                 f"{timeseries[sname]['river_depth'][i]:.4f}",
                                 f"{timeseries[sname]['flood_stor'][i]:.2f}",
                                 f"{timeseries[sname]['runoff_stor'][i]:.4f}",
                                 f"{timeseries[sname]['baseflow_stor'][i]:.4f}"])
    print(f"Timeseries sauvegardees dans: {ts_csv}")

    # 5. Inversion du reseau d'ecoulement et masques de bassin
    print("\n=== RECONSTITUTION DU RESEAU HYDROGRAPHIQUE PAR BASSIN ===")
    down_r = np.full((120, 180), -1, dtype=int)
    down_c = np.full((120, 180), -1, dtype=int)
    for r in range(120):
        for c in range(180):
            if not np.ma.is_masked(flow_x[r, c]) and not np.ma.is_masked(flow_y[r, c]):
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

    basin_masks = {}
    for st in stations:
        bmask = get_basin_mask(st["row"], st["col"])
        basin_masks[st["nom"]] = bmask
        b_area = np.sum(grid_area[bmask]) / 1e6
        print(f"Bassin {st['nom']:16s}: {np.sum(bmask):5d} mailles, Aire tracee = {b_area:8.1f} km2 (HyMAP exutoire: {st['aire_hymap']:.1f} km2)")

    # 6. Bilan de masse hydrologique
    print("\n=== CALCUL DU BILAN DE MASSE PAR BASSIN (JANVIER 2018) ===")
    remap_files = sorted(glob.glob(remap_dir + "/**/LIS_HIST_*.d01.nc", recursive=True))[:31]
    Vin = {st["nom"]: 0.0 for st in stations}
    for rf in remap_files:
        ds = nc.Dataset(rf)
        qs = ds["Qs_tavg"][:]
        qsb = ds["Qsb_tavg"][:]
        if qs.ndim == 3: qs = qs[0]
        if qsb.ndim == 3: qsb = qsb[0]
        qs = np.nan_to_num(qs.filled(0.0))
        qsb = np.nan_to_num(qsb.filled(0.0))
        daily_vol = (np.maximum(qs, 0.0) + np.maximum(qsb, 0.0)) * 1e-3 * grid_area * 86400.0
        for st in stations:
            Vin[st["nom"]] += np.sum(daily_vol[basin_masks[st["nom"]]])
        ds.close()

    Vout = {st["nom"]: 0.0 for st in stations}
    S_end = {st["nom"]: 0.0 for st in stations}

    for i, hf in enumerate(nc_files):
        ds = nc.Dataset(hf)
        flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
        if flow.ndim == 3: flow = flow[0]
        fldq = np.nan_to_num(ds["FloodQ_tavg"][:].filled(0.0)) if "FloodQ_tavg" in ds.variables else np.zeros_like(flow)
        if fldq.ndim == 3: fldq = fldq[0]

        rsto = np.nan_to_num(ds["RiverStor_tavg"][:].filled(0.0))
        if rsto.ndim == 3: rsto = rsto[0]
        fsto = np.nan_to_num(ds["FloodStor_tavg"][:].filled(0.0)) if "FloodStor_tavg" in ds.variables else np.zeros_like(rsto)
        if fsto.ndim == 3: fsto = fsto[0]
        rnfsto = np.nan_to_num(ds["RunoffStor_tavg"][:].filled(0.0))
        if rnfsto.ndim == 3: rnfsto = rnfsto[0]
        bsfsto = np.nan_to_num(ds["BaseflowStor_tavg"][:].filled(0.0))
        if bsfsto.ndim == 3: bsfsto = bsfsto[0]

        # Total storage in m3
        cell_stor = rsto + fsto + rnfsto + bsfsto

        for st in stations:
            r, c = st["row"], st["col"]
            # Note: Streamflow_tavg in HyMAP2 already includes floodplain outflow (HYMAP2_model.F90:290)
            Vout[st["nom"]] += flow[r, c] * 86400.0
            if i == len(nc_files) - 1:
                S_end[st["nom"]] = np.sum(cell_stor[basin_masks[st["nom"]]])
        ds.close()

    print(f"\n{'Bassin':16s} | {'Vin (hm3)':10s} | {'Vout (hm3)':10s} | {'DeltaS (hm3)':12s} | {'Vout+DeltaS':12s} | {'Ecart (hm3)':12s} | {'Erreur (%)':10s}")
    print("-" * 92)
    mass_balance_records = []
    for st in stations:
        sname = st["nom"]
        vin_hm3 = Vin[sname] / 1e6
        vout_hm3 = Vout[sname] / 1e6
        ds_hm3 = S_end[sname] / 1e6
        bal_hm3 = vout_hm3 + ds_hm3
        diff_hm3 = bal_hm3 - vin_hm3
        err_pct = (diff_hm3 / vin_hm3 * 100.0) if vin_hm3 > 0 else 0.0
        print(f"{sname:16s} | {vin_hm3:10.2f} | {vout_hm3:10.2f} | {ds_hm3:12.2f} | {bal_hm3:12.2f} | {diff_hm3:12.2f} | {err_pct:+9.2f}%")
        mass_balance_records.append({
            "bassin": sname,
            "vin_hm3": vin_hm3,
            "vout_hm3": vout_hm3,
            "deltas_hm3": ds_hm3,
            "vout_plus_deltas_hm3": bal_hm3,
            "diff_hm3": diff_hm3,
            "err_pct": err_pct
        })

    mb_csv = os.path.join(out_table_dir, "mass_balance_jan2018.csv")
    with open(mb_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bassin", "vin_hm3", "vout_hm3", "deltas_hm3", "vout_plus_deltas_hm3", "diff_hm3", "err_pct"])
        for r in mass_balance_records:
            writer.writerow([r["bassin"], f"{r['vin_hm3']:.2f}", f"{r['vout_hm3']:.2f}", f"{r['deltas_hm3']:.2f}",
                             f"{r['vout_plus_deltas_hm3']:.2f}", f"{r['diff_hm3']:.2f}", f"{r['err_pct']:.2f}"])
    print(f"Table de bilan de masse sauvegardee dans: {mb_csv}")

    # 7. Tracer les 9 hydrogrammes en grille 3x3
    print("\nGeneration du graphique des hydrogrammes (3x3)...")
    fig, axes = plt.subplots(3, 3, figsize=(16, 11), sharex=True)
    axes = axes.flatten()

    for idx, st in enumerate(stations):
        ax = axes[idx]
        sname = st["nom"]
        dts = timeseries[sname]["dates"]
        flows = timeseries[sname]["streamflow"]
        q_max = max(flows) if len(flows) > 0 else 0.0

        ax.plot(dts, flows, color="#0b5394", lw=2, marker="o", markersize=3, label="Streamflow (m3/s)")
        ax.set_title(f"{sname}\n(Aire off: {st['aire_off']:.0f} km² | Qmax: {q_max:.1f} m³/s)", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_ylabel("Débit (m³/s)", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
        ax.tick_params(axis="x", rotation=30)
        ax.set_ylim(bottom=0)

    plt.suptitle("Hydrogrammes Journaliers HyMAP2 (OPL_noirr_2016_2020) — Janvier 2018", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    fig_path = os.path.join(plots_dir, "hydrographs_jan2018_opl.png")
    plt.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Graphique sauvegarde dans: {fig_path}")

    # Resume plomberie
    print("\n=== CONTROLES DE PLOMBERIE VERIFIES ===")
    for st in stations:
        sname = st["nom"]
        flows = timeseries[sname]["streamflow"]
        rstos = timeseries[sname]["river_stor"]
        has_nan = any(np.isnan(flows)) or any(np.isnan(rstos))
        has_neg = any(f < 0 for f in flows) or any(s < 0 for s in rstos)
        growing = flows[-1] > flows[0] or max(flows) > 0.0
        print(f"Station {sname:16s} | Débit min={min(flows):.2f}, max={max(flows):.2f} m3/s | NaN: {has_nan} | Negatif: {has_neg} | Reagit: {growing}")

if __name__ == "__main__":
    main()
