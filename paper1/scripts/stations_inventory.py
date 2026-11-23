#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stations_inventory.py — État des lieux des pluviomètres (lecture seule).

Lit (sans modifier) :
  ~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/SCRIPTS/paper_dataset_precip/data/raw/stations/ABH_stations_plusziz_and_abhbc.csv
Produit :
  paper1/STATIONS_INVENTORY.md
  paper1/tables/stations_inventory.csv

Environnement : ~/.conda/envs/postproc_env/bin/python (geopandas, netCDF4).
Aucun téléchargement, aucune correction des données.
"""
import os
import re
import csv
import glob
import calendar
import subprocess
import datetime as dt
from collections import deque

import numpy as np
import pandas as pd
import geopandas as gpd
import netCDF4 as nc

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco")
DSROOT = os.path.join(HOME, "lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/SCRIPTS/paper_dataset_precip")
DATA = os.path.join(DSROOT, "data")
F = os.path.join(DATA, "raw/stations/ABH_stations_plusziz_and_abhbc.csv")

OUT_MD = os.path.join(REPO, "paper1/STATIONS_INVENTORY.md")
OUT_CSV = os.path.join(REPO, "paper1/tables/stations_inventory.csv")

P0, P1 = pd.Timestamp("2001-01-01"), pd.Timestamp("2014-12-31")
NDAYS = (P1 - P0).days + 1
THR_VALID = 80.0
THR_ABERR = 300.0

BASINS = {
    "Bouregreg": os.path.join(REPO, "domain/NorthMor/Basins_limits/BV_Bouregreg_ExportFeatures.shp"),
    "Sebou": os.path.join(REPO, "domain/NorthMor/Basins_limits/Limite_ABHS_Export.shp"),
}
LDT_FILE = os.path.join(REPO, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
# Exutoires (ligne, colonne) 0-based tels qu'utilisés dans paper1/scripts/step13_upstream_catchments_da_corr.py
HYMAP_OUTLETS = {"Lalla Chafia (amont HyMAP)": (75, 71), "Sidi Jabeur (amont HyMAP)": (71, 71)}

IMERG_RAW = os.path.join(REPO, "data/forcing/IMERG/raw")
MERRA_FLX = os.path.join(REPO, "data/forcing/MERRA2/M2T1NXFLX")

md = []


def w(s=""):
    md.append(s)


def rel(p):
    return p.replace(HOME, "~")


# ---------------------------------------------------------------- 1. Structure
size_b = os.path.getsize(F)
with open(F, "r", newline="") as fh:
    head_lines = [next(fh).rstrip("\n") for _ in range(6)]
dialect = csv.Sniffer().sniff(head_lines[0] + "\n" + head_lines[1])
sep = dialect.delimiter
with open(F, "rb") as fh:
    n_lines = sum(1 for _ in fh)

raw = pd.read_csv(F, sep=sep, dtype=str, keep_default_na=False)
inferred = pd.read_csv(F, sep=sep, nrows=200000).dtypes
n_rows, n_cols = raw.shape

empty_counts = {c: int((raw[c].str.strip() == "").sum()) for c in raw.columns}
prec = pd.to_numeric(raw["Precipitation"], errors="coerce")
lon = pd.to_numeric(raw["Longitude"], errors="coerce")
lat = pd.to_numeric(raw["Latitude"], errors="coerce")
date = pd.to_datetime(raw["Date"], format="%Y-%m-%d", errors="coerce")

df = pd.DataFrame({"Station": raw["Station"], "Date": date, "P": prec, "lon": lon, "lat": lat})

w("# Inventaire des pluviomètres — ABH_stations_plusziz_and_abhbc.csv")
w()
w(f"Généré par `paper1/scripts/stations_inventory.py` le {dt.datetime.now():%Y-%m-%d %H:%M}. "
  "Lecture seule : aucune donnée source modifiée, aucun téléchargement.")
w()
w(f"Fichier : `{rel(F)}`")
w()
w("## 1. Structure")
w()
w(f"- Taille : {size_b} octets ({size_b/1024**2:.1f} Mio)")
w(f"- Lignes (en-tête inclus) : {n_lines}")
w(f"- Séparateur détecté : `{sep}`")
w(f"- Lignes de données : {n_rows} ; colonnes : {n_cols}")
w()
w("6 premières lignes brutes :")
w()
w("```")
for l in head_lines:
    w(l)
w("```")
w()
w("| Colonne | Type inféré (pandas, 200 000 premières lignes) | Cellules vides | Valeurs non convertibles |")
w("|---|---|---|---|")
nonconv = {"Date": int(date.isna().sum()), "Station": "n/a", "Precipitation": int(prec.isna().sum()),
           "Longitude": int(lon.isna().sum()), "Latitude": int(lat.isna().sum())}
for c in raw.columns:
    w(f"| {c} | {inferred.get(c)} | {empty_counts[c]} | {nonconv.get(c, 'n/a')} |")
w()
w("- Format : **long** (une ligne par couple station × date ; colonnes `Date`, `Station`, `Precipitation`, "
  "`Longitude`, `Latitude`).")
w()

# ---------------------------------------------------------------- 2. Contenu
stations = sorted(df["Station"].unique())
n_st = len(stations)
coords = df.groupby("Station")[["lon", "lat"]].nunique()
multi_coord = coords[(coords["lon"] > 1) | (coords["lat"] > 1)].index.tolist()
st_coord = df.groupby("Station")[["lon", "lat"]].first()

single_letter = [s for s in stations if re.fullmatch(r"[A-Z]", s)]

folds_path = os.path.join(DATA, "raw/Foldes/station_folds3.csv")
folds = pd.read_csv(folds_path) if os.path.exists(folds_path) else None

w("## 2. Contenu")
w()
w(f"- Nombre de stations (valeurs distinctes de `Station`) : **{n_st}**")
w("- Identifiant : seule la colonne `Station` (nom en texte) identifie les stations ; "
  "aucune colonne d'identifiant numérique.")
w("- Nom : colonne `Station`.")
w("- Source (ABH/DGM) : **aucune colonne du fichier ne l'indique** (colonnes présentes : "
  + ", ".join(f"`{c}`" for c in raw.columns) + ").")
w("  - Le `README.md` du même dossier déclare 34 stations DGM + 183 stations ABH = 217 stations, "
  "et 10 mailles ERA5 auxiliaires dans le sud ; cette répartition n'est pas codée dans le fichier.")
w(f"  - Stations dont le nom est une seule lettre majuscule : {len(single_letter)} "
  f"({', '.join(single_letter)}) ; stations restantes : {n_st - len(single_letter)}.")
w("- Coordonnées : présentes (colonnes `Longitude`, `Latitude`) ; unité et système de référence "
  "non indiqués dans le fichier.")
w(f"  - Longitude : min {st_coord['lon'].min():.5f}, max {st_coord['lon'].max():.5f}")
w(f"  - Latitude : min {st_coord['lat'].min():.5f}, max {st_coord['lat'].max():.5f}")
w(f"  - Stations avec plus d'un couple de coordonnées : {len(multi_coord)}"
  + (f" ({', '.join(multi_coord)})" if multi_coord else ""))
dupcoord = st_coord.round(6).duplicated(keep=False)
w(f"  - Stations partageant exactement les mêmes coordonnées qu'une autre station : {int(dupcoord.sum())}"
  + (f" ({', '.join(st_coord.index[dupcoord])})" if dupcoord.any() else ""))
w("- Altitude : **absente** du fichier.")
w()

# ---------------------------------------------------------------- 3. Temps
dmin, dmax = df["Date"].min(), df["Date"].max()
dups_all = df.duplicated(["Station", "Date"], keep=False)
n_dup_rows = int(df.duplicated(["Station", "Date"]).sum())
dup_groups = df[dups_all].groupby(["Station", "Date"])["P"].nunique()
n_dup_conflict = int((dup_groups > 1).sum())
st_dup = sorted(df[dups_all]["Station"].unique())

dd = df.drop_duplicates(["Station", "Date"]).sort_values(["Station", "Date"])
steps = dd.groupby("Station")["Date"].diff().dropna().dt.days
step_counts = steps.value_counts().sort_index()

neg = df[df["P"] < 0]
aberr = df[df["P"] > THR_ABERR]
nan_p = int(df["P"].isna().sum())

w("## 3. Temps et valeurs")
w()
w(f"- Période totale : {dmin:%Y-%m-%d} → {dmax:%Y-%m-%d}")
w(f"- Pas de temps : écarts entre dates successives (par station, doublons exclus) — "
  f"{int(step_counts.get(1, 0))} écarts de 1 jour sur {int(step_counts.sum())} ; "
  f"{int(step_counts[step_counts.index > 1].sum())} écarts > 1 jour (lacunes) ; "
  f"écart max {int(steps.max()) if len(steps) else 'n/a'} jours.")
w("- Unité des valeurs : non indiquée dans le fichier (en-tête `Precipitation`). "
  "Le `README.md` du dossier mentionne des « daily precipitation records ».")
w(f"- Valeurs de `Precipitation` : min {df['P'].min()}, max {df['P'].max()}, moyenne {df['P'].mean():.4f}")
w(f"- Code de valeur manquante : aucune cellule vide, aucune valeur non numérique ({nan_p} NaN) ; "
  "valeurs sentinelles testées : "
  + ", ".join(f"{v} → {int((df['P'] == v).sum())}" for v in [-999, -9999, -99, -1, 999, 9999]) + ".")
w("  Les jours manquants correspondent à des dates **absentes** du fichier (pas de ligne).")
w(f"- Valeurs négatives : **{len(neg)}**")
w(f"- Valeurs > {THR_ABERR:.0f} mm/jour : **{len(aberr)}** (non corrigées)")
if len(aberr):
    w()
    w("| Station | Date | Precipitation |")
    w("|---|---|---|")
    for _, r in aberr.sort_values(["Station", "Date"]).iterrows():
        w(f"| {r.Station} | {r.Date:%Y-%m-%d} | {r.P} |")
w()
w(f"- Couples (station, date) dupliqués : {n_dup_rows} lignes en surplus ; "
  f"{len(dup_groups)} couples concernés dont {n_dup_conflict} avec des valeurs différentes ; "
  f"{len(st_dup)} stations concernées"
  + (f" ({', '.join(st_dup)})" if st_dup else "") + ".")
w()

# ---------------------------------------------------------------- 4. Couverture 2001–2014
per = dd[(dd["Date"] >= P0) & (dd["Date"] <= P1) & dd["P"].notna() & (dd["P"] >= 0)]
n_valid = per.groupby("Station")["Date"].nunique().reindex(stations).fillna(0).astype(int)
pct_valid = (100.0 * n_valid / NDAYS).round(2)
first = dd.groupby("Station")["Date"].min()
last = dd.groupby("Station")["Date"].max()
n_ge80 = int((pct_valid >= THR_VALID).sum())

bins = [0, 1e-9, 20, 40, 60, 80, 95, 100.0001]
labels = ["0 %", "]0–20[ %", "[20–40[ %", "[40–60[ %", "[60–80[ %", "[80–95[ %", "[95–100] %"]
hist = pd.cut(pct_valid, bins=bins, labels=labels, right=False).value_counts().reindex(labels)

w("## 4. Couverture 2001-01-01 → 2014-12-31")
w()
w(f"- Nombre de jours de la période : {NDAYS}")
w("- Jour valide : date présente dans le fichier pour la station, valeur numérique non manquante et ≥ 0 "
  "(doublons comptés une fois ; valeurs > 300 mm/jour conservées).")
w(f"- Stations avec ≥ {THR_VALID:.0f} % de jours valides : **{n_ge80}** / {n_st}")
w(f"  - dont stations au nom d'une seule lettre : {sum(1 for s in single_letter if pct_valid[s] >= THR_VALID)}")
w(f"- Stations avec 0 % (aucune donnée sur la période) : {int((pct_valid == 0).sum())}")
w()
w("| Classe de % valide | Stations |")
w("|---|---|")
for k, v in hist.items():
    w(f"| {k} | {int(v)} |")
w()
w("Le détail par station est dans `paper1/tables/stations_inventory.csv`.")
w()

# ---------------------------------------------------------------- 5. Position / bassins
pts = gpd.GeoDataFrame({"Station": st_coord.index},
                       geometry=gpd.points_from_xy(st_coord["lon"], st_coord["lat"]), crs="EPSG:4326")
basin_of = {s: [] for s in stations}
basin_rows = []
for bname, shp in BASINS.items():
    if not os.path.exists(shp):
        basin_rows.append((bname, rel(shp), "contour absent", "", "", ""))
        continue
    g = gpd.read_file(shp)
    attrs = "; ".join(f"{c}={g.iloc[0][c]}" for c in g.columns if c in ("Name", "Agence", "HydroID"))
    gp = pts.to_crs(g.crs)
    inside = gp.geometry.apply(lambda p: bool(g.geometry.covers(p).any()))
    ins = gp.loc[inside, "Station"].tolist()
    for s in ins:
        basin_of[s].append(bname)
    n80 = sum(1 for s in ins if pct_valid[s] >= THR_VALID)
    basin_rows.append((bname, f"`{rel(shp).replace(rel(REPO) + '/', '')}`", f"EPSG:{g.crs.to_epsg()} ; {attrs}",
                       len(ins), n80, ", ".join(s for s in ins if pct_valid[s] >= THR_VALID)))

if os.path.exists(LDT_FILE):
    with nc.Dataset(LDT_FILE) as ds:
        flow_x = ds["HYMAP_flow_direction_x"][:]
        flow_y = ds["HYMAP_flow_direction_y"][:]
        glat = np.asarray(ds["lat"][:])
        glon = np.asarray(ds["lon"][:])
        dx = float(ds.getncattr("DX"))
        dy = float(ds.getncattr("DY"))
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

    def get_catchment(o_r, o_c):
        vis = {(o_r, o_c)}
        q = deque([(o_r, o_c)])
        while q:
            cur = q.popleft()
            for p in parents.get(cur, []):
                if p not in vis:
                    vis.add(p)
                    q.append(p)
        return vis

    lat0, lon0 = float(glat[0, 0]), float(glon[0, 0])
    st_cell = {}
    for s in stations:
        r = int(np.floor((st_coord.loc[s, "lat"] - (lat0 - dy / 2)) / dy))
        c = int(np.floor((st_coord.loc[s, "lon"] - (lon0 - dx / 2)) / dx))
        if 0 <= r < R and 0 <= c < C:
            st_cell[s] = (r, c)
    for bname, (orow, ocol) in HYMAP_OUTLETS.items():
        cells = get_catchment(orow, ocol)
        ins = [s for s in stations if st_cell.get(s) in cells]
        for s in ins:
            basin_of[s].append(bname)
        n80 = sum(1 for s in ins if pct_valid[s] >= THR_VALID)
        basin_rows.append((bname, f"`{rel(LDT_FILE).replace(rel(REPO) + '/', '')}` (D8 HyMAP, exutoire ligne {orow}, "
                                  f"colonne {ocol} ; {len(cells)} mailles de {dx:.2f}°)",
                           f"centre maille exutoire : lat {glat[orow, ocol]:.3f}, lon {glon[orow, ocol]:.3f}",
                           len(ins), n80, ", ".join(s for s in ins if pct_valid[s] >= THR_VALID)))
else:
    for bname in HYMAP_OUTLETS:
        basin_rows.append((bname, rel(LDT_FILE), "contour absent (fichier LDT HyMAP introuvable)", "", "", ""))

w("## 5. Position par rapport aux bassins")
w()
w("- Hypothèse de calcul : coordonnées des stations lues comme longitude/latitude WGS84 (EPSG:4326), "
  "le fichier n'indiquant pas de système de référence ; reprojetées dans le SCR de chaque contour.")
w("- Bouregreg et Sebou : test point-dans-polygone (bord inclus). Le contour « Sebou » disponible est "
  "`domain/NorthMor/Basins_limits/Limite_ABHS_Export.shp` (attribut `Agence=ABHS`) ; une copie aux "
  "attributs identiques existe sous `domain/sebou/shapefiles/Sebou_limits/Limite_ABHS.shp`.")
w("- Lalla Chafia et Sidi Jabeur : aucun polygone dans le dépôt ; les bassins amont sont des ensembles "
  "de mailles HyMAP obtenus par remontée D8 (même algorithme et mêmes exutoires que "
  "`paper1/scripts/step13_upstream_catchments_da_corr.py`). Une station est comptée si la maille "
  "qui la contient appartient à l'ensemble.")
w()
w("| Bassin | Contour utilisé | SCR / attributs | Stations dans le bassin | dont ≥ 80 % valides 2001–2014 | Stations ≥ 80 % |")
w("|---|---|---|---|---|---|")
for row in basin_rows:
    w("| " + " | ".join(str(x) for x in row) + " |")
w()


# ---------------------------------------------------------------- 6. Autres fichiers
def quick_period(path):
    hdr = pd.read_csv(path, nrows=0).columns.tolist()
    if "Date" in hdr:
        usecols = [c for c in ("Date", "Station") if c in hdr]
        t = pd.read_csv(path, usecols=usecols)
        d = pd.to_datetime(t["Date"], errors="coerce")
        nst = t["Station"].nunique() if "Station" in t else ""
        return hdr, f"{d.min():%Y-%m-%d} → {d.max():%Y-%m-%d}", nst, len(t)
    t = pd.read_csv(path)
    nst = t["Station"].nunique() if "Station" in t else ""
    return hdr, "pas de colonne Date", nst, len(t)


w("## 6. Autres fichiers liés (non traités)")
w()
w("Dossiers parcourus : `data/raw/stations/` (y compris fichiers cachés) et `data/` (récursif, "
  "fichiers .csv/.xlsx/.xls/.txt).")
w()
w("| Fichier | Taille (octets) | Colonnes | Période (`Date`) | Stations distinctes | Lignes |")
w("|---|---|---|---|---|---|")
others = []
n_hydro = 0
HYDRO = os.path.join(DATA, "generated/hydrological_simulations")
for p in sorted(glob.glob(os.path.join(DATA, "**", "*"), recursive=True)):
    if os.path.isdir(p) or os.path.abspath(p) == os.path.abspath(F):
        continue
    if p.lower().endswith((".csv", ".xlsx", ".xls", ".txt")):
        if p.startswith(HYDRO + "/"):
            n_hydro += 1
            continue
        others.append(p)
for p in sorted(glob.glob(os.path.join(DATA, "raw/stations", ".*", "*"))):
    others.append(p)
for p in others:
    sz = os.path.getsize(p)
    rp = rel(p).replace(rel(DATA) + "/", "data/")
    if p.endswith(".csv"):
        try:
            hdr, period, nst, nl = quick_period(p)
            w(f"| `{rp}` | {sz} | {', '.join(hdr)} | {period} | {nst} | {nl} |")
        except Exception as e:  # noqa
            w(f"| `{rp}` | {sz} | lecture impossible ({e}) | | | |")
    else:
        w(f"| `{rp}` | {sz} | non lu | | | |")
w()
w(f"Racine `data/` = `{rel(DATA)}`. Non listés : {n_hydro} fichiers tabulaires sous "
  "`data/generated/hydrological_simulations/` (sorties de simulations GR4J/HBV par bassin, noms `simulated_b_*.xlsx`).")
w()
if folds is not None:
    w(f"- `station_folds3.csv` : {folds['Station'].nunique()} stations avec coordonnées, `Region`, "
      f"`IsSpecial` (True : {int(folds['IsSpecial'].astype(str).eq('True').sum())}) et `Fold` ; "
      "pas de colonne source ABH/DGM ni altitude.")
    only_f = sorted(set(folds["Station"]) - set(stations))
    only_s = sorted(set(stations) - set(folds["Station"]))
    w(f"  - Stations présentes seulement dans `station_folds3.csv` : {len(only_f)}"
      + (f" ({', '.join(only_f)})" if only_f else "") + f" ; seulement dans le fichier principal : {len(only_s)}"
      + (f" ({', '.join(only_s)})" if only_s else "") + ".")
w("- Aucun fichier séparé DGM ou ABH n'a été trouvé dans `data/`.")
pp = os.path.join(REPO, "domain/NorthMor/Basins_limits/Postes_pluvio.shp")
if os.path.exists(pp):
    g = gpd.read_file(pp)
    de = pd.to_numeric(g["De"], errors="coerce")
    au = pd.to_numeric(g["Au"], errors="coerce")
    xl = pd.Timestamp("1899-12-30")
    w(f"- Hors dossier demandé, dans le dépôt NoahMP_Morocco : `domain/NorthMor/Basins_limits/Postes_pluvio.shp` "
      f"({len(g)} postes ; colonnes {', '.join(c for c in g.columns if c != 'geometry')}) ; "
      f"`De` numérique min = {de.min():.0f} ({int(de.isna().sum())} non numériques), "
      f"`Au` numérique max = {au.max():.0f} ({int(au.isna().sum())} non numériques) ; "
      f"lus comme numéros de série Excel : {xl + pd.Timedelta(days=int(de.min())):%Y-%m-%d}"
      f" → {xl + pd.Timedelta(days=int(au.max())):%Y-%m-%d}.")
w()

# ---------------------------------------------------------------- 7. Forçages
w("## 7. Disponibilité IMERG V07B et MERRA-2 (2001–2014)")
w()
years = range(2001, 2015)
if os.path.isdir(IMERG_RAW):
    subdirs = sorted(d for d in os.listdir(IMERG_RAW) if os.path.isdir(os.path.join(IMERG_RAW, d)))
    months = [d for d in subdirs if re.fullmatch(r"\d{6}", d)]
    others_dirs = [d for d in subdirs if not re.fullmatch(r"\d{6}", d)]
    prods = {}
    slots = set()
    n_files_all = 0
    misplaced = {}
    pat = re.compile(r"(3B-[A-Z]+)\.\S*?3IMERG\.(\d{8})-S(\d{6})-E\d{6}\.\d{4}\.(V\d+[A-Z]?)\.HDF5$")
    for d in subdirs:
        for f_ in os.listdir(os.path.join(IMERG_RAW, d)):
            mm = pat.match(f_)
            if not mm:
                continue
            n_files_all += 1
            day = mm.group(2)
            if re.fullmatch(r"\d{6}", d) and day[:6] != d:
                misplaced[d] = misplaced.get(d, 0) + 1
            if 2001 <= int(day[:4]) <= 2014:
                key = (mm.group(1), mm.group(4))
                prods[key] = prods.get(key, 0) + 1
                slots.add((day, mm.group(3)))
    per_day = pd.Series([s[0] for s in slots]).value_counts()
    all_days = [d.strftime("%Y%m%d") for d in pd.date_range(P0, P1)]
    n_full = sum(1 for d in all_days if per_day.get(d, 0) == 48)
    part = [d for d in all_days if 0 < per_day.get(d, 0) < 48]
    absent = [d for d in all_days if per_day.get(d, 0) == 0]
    w(f"- IMERG : `{rel(IMERG_RAW)}` — sous-dossiers mensuels {months[0]} → {months[-1]} ({len(months)})"
      + (f" ; autres sous-dossiers : {', '.join(others_dirs)}" if others_dirs else "") + ".")
    w("  - Produits datés 2001–2014 (préfixe, version → nombre de fichiers, tous sous-dossiers) : "
      + ", ".join(f"{k[0]} {k[1]} → {v}" for k, v in sorted(prods.items())) + ".")
    w("  - Pas de temps des fichiers : demi-horaire (`3B-HHR`, 48 créneaux/jour) ; pas de produit journalier.")
    w(f"  - Créneaux demi-horaires distincts 2001–2014 (date et heure lues dans le nom de fichier) : "
      f"{len(slots)} / {48 * NDAYS} attendus ; jours complets (48/48) : {n_full} / {NDAYS} ; "
      f"jours partiels : {len(part)} ; jours sans aucun fichier : {len(absent)}.")
    if part:
        w(f"    - Jours partiels : " + ", ".join(f"{d} ({int(per_day[d])})" for d in part) + ".")
    if absent:
        w(f"    - Jours sans fichier : " + ", ".join(absent) + ".")
    if misplaced:
        w("  - Fichiers rangés dans un sous-dossier mensuel ne correspondant pas à leur date : "
          + ", ".join(f"{k} → {v}" for k, v in sorted(misplaced.items())) + ".")
    root_files = [f_ for f_ in os.listdir(IMERG_RAW) if not os.path.isdir(os.path.join(IMERG_RAW, f_))]
    if root_files:
        sizes = [os.path.getsize(os.path.join(IMERG_RAW, f_)) for f_ in root_files]
        w(f"  - Fichiers non rangés à la racine de `raw/` : {len(root_files)} "
          f"(préfixes : {', '.join(sorted({f_.split('_')[0] for f_ in root_files}))} ; "
          f"taille totale {sum(sizes)} octets ; {sum(1 for s in sizes if s == 0)} de taille nulle) ; non inclus dans les comptes ci-dessus.")
    daily_local = glob.glob(os.path.join(REPO, "data/forcing/IMERG/**/3B-DAY*"), recursive=True)
    w(f"  - Fichiers journaliers `3B-DAY*` sous `data/forcing/IMERG/` : {len(daily_local)}.")
    sub = os.path.join(REPO, "data/forcing/IMERG/subset")
    if os.path.isdir(sub):
        w(f"  - `data/forcing/IMERG/subset/` : {len(os.listdir(sub))} fichier(s).")
else:
    w(f"- IMERG : dossier `{rel(IMERG_RAW)}` absent.")

if os.path.isdir(MERRA_FLX):
    fl = sorted(os.listdir(MERRA_FLX))
    days = {}
    for f_ in fl:
        mm = re.search(r"\.(\d{8})\.nc4$", f_)
        if mm:
            days[mm.group(1)] = f_
    alld = sorted(days)
    n_exp = sum(366 if calendar.isleap(y) else 365 for y in years)
    n_have = sum(1 for d in alld if 2001 <= int(d[:4]) <= 2014)
    missing = [d.strftime("%Y%m%d") for d in pd.date_range(P0, P1) if d.strftime("%Y%m%d") not in days]
    sample = days.get("20010101") or fl[0]
    with nc.Dataset(os.path.join(MERRA_FLX, sample)) as ds:
        pvars = [v for v in ds.variables if v.startswith("PREC")]
        nt = len(ds.dimensions["time"]) if "time" in ds.dimensions else "?"
        units = {v: getattr(ds[v], "units", "?") for v in pvars}
        nlat = len(ds.dimensions["lat"]) if "lat" in ds.dimensions else "?"
        nlon = len(ds.dimensions["lon"]) if "lon" in ds.dimensions else "?"
    w(f"- MERRA-2 : `{rel(MERRA_FLX)}` (collection `tavg1_2d_flx_Nx`) — fichiers journaliers "
      f"{alld[0]} → {alld[-1]} ({len(alld)} fichiers).")
    w(f"  - Jours 2001–2014 attendus : {n_exp} ; présents : {n_have} ; manquants : {len(missing)}"
      + (f" ({', '.join(missing)})" if missing else "") + ".")
    w(f"  - Fichier témoin `{sample}` : {nt} pas de temps, grille {nlat}×{nlon} ; variables de précipitation : "
      + ", ".join(f"`{v}` ({units[v]})" for v in pvars) + ".")
    w("  - `data/forcing/MERRA2/MERRA2_400/Yyyyy/Mmm/` contient des liens symboliques vers M2T1NXFLX "
      "(et RAD, SLV) ; `MERRA2_100/200/300` sont des liens vers `MERRA2_400`.")
else:
    w(f"- MERRA-2 : dossier `{rel(MERRA_FLX)}` absent.")

search_roots = [os.path.join(HOME, "lustre/empowermed-ahl6xm8o7mg/"),
                os.path.join(HOME, "lustre/climat-um6p-st-iwri-7ksifkvwkuy/")]
cmd = (["timeout", "1200", "find", "-H"] + search_roots +
       ["-maxdepth", "7", "(", "-iname", "*3B-DAY*", "-o", "-iname", "*imerg*", "-o", "-iname", "*merra*", ")",
        "-not", "-path", "*/NoahMP_Morocco/data/forcing/IMERG/raw/*",
        "-not", "-path", "*/M2T1NX*/*", "-not", "-path", "*/MERRA2_400/*", "-not", "-path", "*/src/*"])
try:
    res = subprocess.run(cmd, capture_output=True, text=True)
    found = [l for l in res.stdout.splitlines()
             if not re.search(r"\.(py|ipynb|sh|log|config|md|txt|png|pdf|lock)$", l, re.I)]
    status = f"code retour {res.returncode}"
except Exception as e:  # noqa
    found, status = [], f"échec ({e})"
daily_found = [p for p in found if "3B-DAY" in os.path.basename(p).upper()]
w()
w("- Recherche complémentaire (`find -H … -maxdepth 7`, noms contenant `3B-DAY`, `imerg` ou `merra`, "
  "hors sous-dossiers déjà décrits et hors `src/`, sur les deux espaces lustre) : "
  f"{status} ; {len(found)} résultats ; fichiers `3B-DAY*` : {len(daily_found)}.")
if found:
    w()
    for p in sorted(found):
        kind = "dossier" if os.path.isdir(p) else f"fichier, {os.path.getsize(p)} octets"
        w(f"  - `{rel(p)}` ({kind})")
w()

# ---------------------------------------------------------------- CSV
folds_special = dict(zip(folds["Station"], folds["IsSpecial"])) if folds is not None else {}
out = pd.DataFrame({
    "id": stations,
    "nom": stations,
    "source": ["non indiquée" for _ in stations],
    "lat": [st_coord.loc[s, "lat"] for s in stations],
    "lon": [st_coord.loc[s, "lon"] for s in stations],
    "debut": [f"{first[s]:%Y-%m-%d}" for s in stations],
    "fin": [f"{last[s]:%Y-%m-%d}" for s in stations],
    "n_jours_valides_2001_2014": [int(n_valid[s]) for s in stations],
    "pct_valide_2001_2014": [float(pct_valid[s]) for s in stations],
    "bassin": [";".join(basin_of[s]) for s in stations],
    "foldes_IsSpecial": [folds_special.get(s, "") for s in stations],
})
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
out.to_csv(OUT_CSV, index=False)

w("## Fichiers produits")
w()
w(f"- `paper1/tables/stations_inventory.csv` ({len(out)} lignes) : id, nom, source, lat, lon, debut, fin, "
  "n_jours_valides_2001_2014, pct_valide_2001_2014, bassin (plusieurs bassins séparés par `;`, vide si aucun), "
  "foldes_IsSpecial (colonne `IsSpecial` de `station_folds3.csv`).")
w("- `id` = `nom` = valeur de la colonne `Station` (pas d'identifiant distinct dans le fichier) ; "
  "`debut`/`fin` = première/dernière date présente pour la station.")
w()

with open(OUT_MD, "w") as fh:
    fh.write("\n".join(md) + "\n")
print("Écrit :", OUT_MD)
print("Écrit :", OUT_CSV)
