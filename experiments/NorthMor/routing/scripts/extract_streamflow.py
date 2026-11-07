#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction unifiee des debits journaliers simules HyMAP aux stations hydrometriques.

Lit les sorties NetCDF LIS_HIST journalieres pour les simulations validees :
  - OPL : output/OPL_2016_2020_corrigee/
  - DA-NoCDF : output/DA_nocdf_2016_2020/
  - DA-CDF : output/DA_cdf_2016_2020/

Utilise la table de reference unique : stations/hymap_stations_pairing.csv
Produit les caches CSV journaliers (1 827 jours, 2016-01-01 a 2020-12-31).
Evite tout retraitement lourd si les caches sont deja disponibles et valides (sauf --force).
"""

import os
import sys
import glob
import argparse
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

EXPERIMENT_CONFIGS = {
    "opl": {
        "name": "Open-Loop (OPL corrigee)",
        "output_sub": "output/OPL_2016_2020_corrigee",
        "cache_file": "t7_sim_daily_12stations_corrigee.csv",
    },
    "nocdf": {
        "name": "DA-NoCDF",
        "output_sub": "output/DA_nocdf_2016_2020",
        "cache_file": "t8_sim_daily_12stations_da_nocdf.csv",
    },
    "cdf": {
        "name": "DA-CDF",
        "output_sub": "output/DA_cdf_2016_2020",
        "cache_file": "t9_sim_daily_12stations_da_cdf.csv",
    },
}

EXPECTED_DAYS = 1827

def is_cache_valid(cache_path, expected_stations):
    if not os.path.exists(cache_path):
        return False
    try:
        df = pd.read_csv(cache_path)
        if len(df) != EXPECTED_DAYS:
            return False
        if "date" not in df.columns:
            return False
        for sid in expected_stations:
            if sid not in df.columns:
                return False
        if df.isna().any().any():
            return False
        return True
    except Exception:
        return False

def extract_experiment(exp_key, routing_dir, df_stations, force=False, test_days=None):
    cfg = EXPERIMENT_CONFIGS[exp_key]
    exp_dir = os.path.join(routing_dir, cfg["output_sub"])
    cache_path = os.path.join(exp_dir, cfg["cache_file"])
    expected_stations = list(df_stations["station_id"])

    print(f"\n[{exp_key.upper()}] Traitement de {cfg['name']}...")
    print(f"   Repertoire : {exp_dir}")
    print(f"   Cache cible : {cache_path}")

    if not force and test_days is None:
        if is_cache_valid(cache_path, expected_stations):
            print(f"   [OK] Cache valide existant ({EXPECTED_DAYS} jours). Extraction ignoree.")
            print(f"        (Utilisez --force pour forcer la re-extraction complete).")
            return cache_path

    routing_nc_dir = os.path.join(exp_dir, "ROUTING")
    if not os.path.exists(routing_nc_dir):
        print(f"   [ERREUR] Repertoire ROUTING introuvable : {routing_nc_dir}")
        return None

    # Recherche des NetCDF journaliers
    hist_files = sorted(glob.glob(os.path.join(routing_nc_dir, "20*/**/LIS_HIST_*.nc"), recursive=True))
    if not hist_files:
        hist_files = sorted(glob.glob(os.path.join(routing_nc_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))

    if not hist_files:
        print(f"   [ERREUR] Aucun fichier LIS_HIST NetCDF trouve dans {routing_nc_dir}")
        return None

    total_files = len(hist_files)
    print(f"   {total_files} fichiers NetCDF detectes.")

    if test_days is not None:
        hist_files = hist_files[:test_days]
        print(f"   [MODE TEST] Limitation aux {len(hist_files)} premiers jours.")

    records = []
    for idx, fpath in enumerate(hist_files):
        with nc.Dataset(fpath) as ds:
            # Extraction temporelle
            t_units = ds["time"].units
            t_val = ds["time"][0]
            base_str = t_units.replace("minutes since ", "")
            base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
            file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
            sim_dt = file_dt - datetime.timedelta(days=1)
            dt_str = sim_dt.strftime("%Y-%m-%d")

            # Extraction debit
            flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if flow.ndim == 3:
                flow = flow[0]

            row_dict = {"date": dt_str}
            for _, row in df_stations.iterrows():
                sid = row["station_id"]
                r, c = int(row["row_hymap"]), int(row["col_hymap"])
                row_dict[sid] = float(flow[r, c])
            records.append(row_dict)

        if (idx + 1) % 365 == 0 or (idx + 1) == len(hist_files):
            print(f"   Progression : {idx + 1}/{len(hist_files)} fichiers traites...")

    df_out = pd.DataFrame(records).sort_values("date").reset_index(drop=True)

    if test_days is None:
        df_out.to_csv(cache_path, index=False)
        print(f"   [SUCCES] Cache enregistre : {cache_path} ({len(df_out)} lignes).")
    else:
        test_out = os.path.join(exp_dir, f"test_{cfg['cache_file']}")
        df_out.to_csv(test_out, index=False)
        print(f"   [TEST] Sortie partielle enregistree : {test_out} ({len(df_out)} lignes).")

    return cache_path

def main():
    parser = argparse.ArgumentParser(
        description="Extraction unifiee des debits journaliers HyMAP aux stations hydrometriques."
    )
    parser.add_argument(
        "--experiment", "-e",
        choices=["opl", "nocdf", "cdf", "all"],
        default="all",
        help="Experience a extraire (opl, nocdf, cdf, ou all)."
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Forcer la re-extraction complete meme si le cache existe."
    )
    parser.add_argument(
        "--routing-dir",
        default=None,
        help="Repertoire racine de routing (par defaut: detecte automatiquement)."
    )
    parser.add_argument(
        "--stations-csv",
        default=None,
        help="Chemin de la table d'appariement des stations."
    )
    parser.add_argument(
        "--test-days",
        type=int,
        default=None,
        help="Optionnel: limiter l'extraction aux N premiers jours pour test rapide."
    )

    args = parser.parse_args()

    # Resolution dynamique des repertoires
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.routing_dir:
        routing_dir = os.path.abspath(args.routing_dir)
    else:
        routing_dir = os.path.abspath(os.path.join(script_dir, ".."))

    if args.stations_csv:
        stations_csv = os.path.abspath(args.stations_csv)
    else:
        stations_csv = os.path.join(routing_dir, "stations/hymap_stations_pairing.csv")

    if not os.path.exists(stations_csv):
        print(f"Erreur : table des stations introuvable : {stations_csv}")
        sys.exit(1)

    df_stations = pd.read_csv(stations_csv)
    print(f"Table des stations chargee : {stations_csv} ({len(df_stations)} stations)")

    target_exps = ["opl", "nocdf", "cdf"] if args.experiment == "all" else [args.experiment]

    for exp in target_exps:
        extract_experiment(
            exp_key=exp,
            routing_dir=routing_dir,
            df_stations=df_stations,
            force=args.force,
            test_days=args.test_days
        )

    print("\nExtraction terminee avec succes.")

if __name__ == "__main__":
    main()
