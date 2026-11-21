#!/usr/bin/env python3
"""
a1_annual_precip.py -- Bloc A1 (paper1, lot 1).

Précipitation annuelle moyenne sur le domaine (mailles terre, LANDMASK du
fichier lis_input) pour 2016-2020, calculée à partir des sorties journalières
de OPL_noirr_2016_2020 (variable TotalPrecip_tavg = P réellement lue par le
modèle, kg m-2 s-1).

Convention LIS : le fichier LIS_HIST_YYYYMMDD0000 contient la moyenne du jour
précédent. Le jour J est donc lu dans le fichier daté J+1 00:00.
Une année Y couvre les fichiers datés Y-01-02 ... (Y+1)-01-01.

Les fichiers sont recherchés dans tous les dossiers output/*/SURFACEMODEL/*/ et
dédoublonnés par date. Les jours manquants sont listés explicitement (aucune
interpolation).

Sélection : année la plus sèche parmi les candidats (2017, 2019, 2020), sous
réserve qu'une restart DA_nocdf (surf + pert) existe au 1er janvier.

Sorties :
  paper1/tables/annual_precip_2016_2020.csv
  paper1/tables/dry_year_selection.csv
Lecture seule sur les sorties de production.
"""
import argparse
import datetime as dt
import glob
import os
import re

import netCDF4 as nc
import numpy as np
import pandas as pd

BASE = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
OPL = os.path.join(BASE, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output")
DA_RST = os.path.join(BASE, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts")
LIS_INPUT = os.path.join(BASE, "data/lis_input/lis_input_NorthMor_5km.nc")
OUT_DIR = os.path.join(BASE, "paper1/tables")
YEARS = [2016, 2017, 2018, 2019, 2020]
CANDIDATES = [2017, 2019, 2020]
VAR = "TotalPrecip_tavg"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()

    with nc.Dataset(LIS_INPUT) as ds:
        landmask = ds.variables["LANDMASK"][:].squeeze().astype(bool)

    # Index unique des fichiers journaliers par date
    files = {}
    dup = 0
    for f in sorted(glob.glob(os.path.join(OPL, "*", "SURFACEMODEL", "*", "LIS_HIST_*0000.d01.nc"))):
        m = re.search(r"LIS_HIST_(\d{8})0000\.d01\.nc$", f)
        if not m:
            continue
        d = dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        if d in files:
            dup += 1
            continue
        files[d] = f

    rows = []
    for y in YEARS:
        start = dt.date(y, 1, 2)
        end = dt.date(y + 1, 1, 1)
        n_exp = (end - start).days + 1
        total = 0.0
        n_found = 0
        missing = []
        n_land_valid_min = None
        for i in range(n_exp):
            d = start + dt.timedelta(days=i)
            f = files.get(d)
            if f is None:
                missing.append((d - dt.timedelta(days=1)).isoformat())
                continue
            with nc.Dataset(f) as ds:
                p = ds.variables[VAR][:].squeeze()
            p = np.ma.masked_less_equal(np.ma.masked_invalid(p), -9998.0)
            vals = p[landmask]
            nv = int(vals.count())
            n_land_valid_min = nv if n_land_valid_min is None else min(n_land_valid_min, nv)
            total += float(vals.mean()) * 86400.0
            n_found += 1
        rows.append({
            "year": y,
            "n_days_expected": n_exp,
            "n_days_found": n_found,
            "P_annual_mm_landmean": round(total, 2) if n_found == n_exp else np.nan,
            "P_sum_found_days_mm_landmean": round(total, 2),
            "n_land_cells_landmask": int(landmask.sum()),
            "n_land_cells_valid_min": n_land_valid_min,
            "source_variable": VAR,
            "source_run": "OPL_noirr_2016_2020",
            "missing_days": ";".join(missing),
            "is_candidate": y in CANDIDATES,
            "da_nocdf_surf_restart_0101_exists": os.path.isfile(os.path.join(DA_RST, "surf", f"LIS_RST_NOAHMP401_{y}01010000.d01.nc")),
            "da_nocdf_pert_restart_0101_exists": os.path.isfile(os.path.join(DA_RST, "pert", f"LIS_DAPERT_{y}01010000.d01.bin")),
        })

    df = pd.DataFrame(rows)
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, "annual_precip_2016_2020.csv")
    df.to_csv(out, index=False)
    print(df.drop(columns=["missing_days"]).to_string(index=False))
    print(f"[INFO] fichiers dupliqués ignorés : {dup}")
    print(f"[OK] {out}")

    cand = df[df.is_candidate & df.da_nocdf_surf_restart_0101_exists & df.da_nocdf_pert_restart_0101_exists
              & df.P_annual_mm_landmean.notna()]
    sel_rows = []
    if cand.empty:
        sel_rows.append({"selected_year": "", "P_annual_mm_landmean": np.nan,
                         "rule": "min P among 2017,2019,2020 with complete days and DA_nocdf restarts at 01-01",
                         "status": "NO_ELIGIBLE_CANDIDATE"})
    else:
        best = cand.loc[cand.P_annual_mm_landmean.idxmin()]
        sel_rows.append({"selected_year": int(best.year), "P_annual_mm_landmean": best.P_annual_mm_landmean,
                         "rule": "min P among 2017,2019,2020 with complete days and DA_nocdf restarts at 01-01",
                         "status": "OK"})
    sel = pd.DataFrame(sel_rows)
    out2 = os.path.join(args.out_dir, "dry_year_selection.csv")
    sel.to_csv(out2, index=False)
    print(sel.to_string(index=False))
    print(f"[OK] {out2}")


if __name__ == "__main__":
    main()
