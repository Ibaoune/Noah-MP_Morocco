#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération du rapport factuel REPORT_A1.md à partir des tables CSV produites par l'étape A1.
Ne contient aucune phrase d'interprétation ni spéculation.
Comptage dynamique des mailles depuis les masques (aucun chiffre tapé en dur).
"""

import os
import tifffile
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A1.md")

def df_to_markdown_simple(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = (ds_in.variables["LANDMASK"][:] == 1.0)
    landcover_20 = ds_in.variables["LANDCOVER"][:]
    dom_lc_181 = np.argmax(landcover_20, axis=0) + 1
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

ldt_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
with nc.Dataset(ldt_path) as ds_ldt:
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]

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
cells_azzaba = get_catchment(75, 108)

def make_mask_121(ccells):
    w = np.zeros((121, 181), dtype=bool)
    for r, c in ccells:
        w[r, c] = True
        w[r, c+1] = True
        w[r+1, c] = True
        w[r+1, c+1] = True
    return w & landmask_181

mask_dom_veg = landmask_181 & (dom_lc_181 != 13) & (dom_lc_181 != 16)

REGIONS = {
    "Domaine complet": landmask_181,
    "Domaine hors classes 13 et 16": mask_dom_veg,
    "Lalla Chafia": make_mask_121(cells_lalla),
    "Sidi Jabeur": make_mask_121(cells_jabeur),
    "Sebou amont": make_mask_121(cells_azzaba),
}

# WaPOR valid mask
def get_wapor_valid_count():
    f_e = os.path.join(BASE_DIR, "data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_2018.tif")
    if not os.path.exists(f_e): return 0
    raw_img = tifffile.imread(f_e).astype(np.float32)
    h_w, w_w = raw_img.shape
    lat_max_w, lon_0_w, d_w = 36.02, -7.50, 0.0022457882102988038
    cov_mask = np.zeros((121, 181), dtype=bool)
    for j in range(121):
        lat_c = lat_181[j]
        r0 = int(np.floor((lat_max_w - (lat_c + 0.025)) / d_w))
        r1 = int(np.ceil((lat_max_w - (lat_c - 0.025)) / d_w))
        if r0 < 0 or r1 > h_w or r0 >= r1: continue
        for i in range(181):
            lon_c = lon_181[i]
            c0 = int(np.floor(((lon_c - 0.025) - lon_0_w) / d_w))
            c1 = int(np.ceil(((lon_c + 0.025) - lon_0_w) / d_w))
            if c0 < 0 or c1 > w_w or c0 >= c1: continue
            block = raw_img[r0:r1, c0:c1]
            n_tot = (r1 - r0) * (c1 - c0)
            valid = ~np.isnan(block) & (block >= 0) & (block < 10000)
            if np.count_nonzero(valid) / n_tot >= 0.80:
                cov_mask[j, i] = True
    return int(np.count_nonzero(cov_mask & landmask_181))

cnt_wp = get_wapor_valid_count()
n_land = int(np.count_nonzero(landmask_181))
cnt_lc = int(np.count_nonzero(REGIONS["Lalla Chafia"]))
cnt_sj = int(np.count_nonzero(REGIONS["Sidi Jabeur"]))
cnt_sa = int(np.count_nonzero(REGIONS["Sebou amont"]))
cnt_dom_veg = int(np.count_nonzero(REGIONS["Domaine hors classes 13 et 16"]))

LANDCOVER_NAMES = {
    1: "Evergreen Needleleaf Forest", 2: "Evergreen Broadleaf Forest", 3: "Deciduous Needleleaf Forest",
    4: "Deciduous Broadleaf Forest", 5: "Mixed Forest", 6: "Closed Shrublands", 7: "Open Shrublands",
    8: "Woody Savannas", 9: "Savannas", 10: "Grasslands", 11: "Permanent Wetlands", 12: "Croplands",
    13: "Urban and Built-Up", 14: "Cropland/Natural Vegetation Mosaic", 15: "Snow and Ice",
    16: "Barren or Sparsely Vegetated", 17: "Water Bodies", 18: "Wooded Tundra", 19: "Mixed Tundra",
    20: "Barren Tundra"
}

unique_lc = sorted(list(np.unique(dom_lc_181[landmask_181])))
LANDCOVER_MASKS = {}
for lc_id in unique_lc:
    cname = LANDCOVER_NAMES.get(lc_id, f"Classe_{lc_id}")
    label = f"Classe {lc_id} - {cname}"
    LANDCOVER_MASKS[label] = (dom_lc_181 == lc_id) & landmask_181

df_lai = pd.read_csv(os.path.join(TABLES_DIR, "A1_lai_model_vs_modis.csv"))
df_delta_lai = pd.read_csv(os.path.join(TABLES_DIR, "A1_delta_lai_assimilation.csv"))
df_et_levels = pd.read_csv(os.path.join(TABLES_DIR, "A1_et_partitioning_levels.csv"))
df_et_contrasts = pd.read_csv(os.path.join(TABLES_DIR, "A1_et_partitioning_contrasts.csv"))
df_wapor_comp = pd.read_csv(os.path.join(TABLES_DIR, "A1_wapor_et_comparison.csv"))
df_doc = pd.read_csv(os.path.join(TABLES_DIR, "A1_wapor_direction_of_change.csv"))

rep_lines = [
    "# Rapport d'Étape A1 — Végétation et partition de l'ET (H1)",
    "",
    "Ce rapport présente les résultats quantitatifs de l'étape A1, sans interprétation subjective ni spéculation.",
    "Tous les chiffres sont issus des scripts de post-traitement sur les sorties de simulation LIS et les observations MODIS LAI et WaPOR v3.",
    "",
    "## 1. Méthodes d'Agrégation et Données",
    "",
    "### 1.1 Grille et Masques",
    "- **Grille LIS NorthMor** : 121 rangées × 181 colonnes (résolution 0,05°, domaine 30,0°N à 36,0°N, 10,0°O à 1,0°O).",
    f"- **Nombre total de mailles terrestres (LANDMASK=1)** : {n_land} mailles.",
    f"- **Domaine hors classes 13 et 16** : {cnt_dom_veg} mailles.",
    f"- **Bassin de Lalla Chafia** : {cnt_lc} mailles.",
    f"- **Bassin de Sidi Jabeur** : {cnt_sj} mailles.",
    f"- **Bassin de Sebou amont** : {cnt_sa} mailles.",
    "",
    "### 1.2 Occupation du Sol (MODIS-IGBP NCEP-modified)",
    "Classes dominantes présentes sur le domaine terrestre :",
]
for lc_id in unique_lc:
    cname = LANDCOVER_NAMES.get(lc_id, f"Classe_{lc_id}")
    label = f"Classe {lc_id} - {cname}"
    n_pix = int(np.count_nonzero(LANDCOVER_MASKS[label]))
    pct = n_pix / n_land * 100.0
    rep_lines.append(f"- **{label}** : {n_pix} mailles ({pct:.2f} %)")

rep_lines.extend([
    "",
    "### 1.3 MODIS LAI (MCD15A2H.006)",
    "- **Résolution native** : ~500 m (1/240°).",
    "- **Agrégation spatiale** : blocs de 12 × 12 pixels sur chaque maille 5 km LIS (moyenne des pixels valides avec QC <= 100, facteur d'échelle 0,1).",
    "- **Agrégation temporelle** : composites 8 jours groupés par mois civil (selon la date centrale du composite) pour chaque mois de 2018 (46 fichiers) et de 2016–2020.",
    "- **Règle pour OL_DAIC** : la variable `LAI_tavg` n'a pas été demandée en sortie (fichier MODEL_OUTPUT_LIST hourly). Selon l'instruction, les valeurs de `ENS_corr` sont utilisées comme substitut factuel et explicitement indiquées par la mention `substitut=ENS_corr`.",
    "",
    "### 1.4 WaPOR v3 (2018–2020)",
    "- **Résolution native** : ~250 m (0,002246°).",
    "- **Emprise archivée** : Longitudes -7,50° à -2,99° ; Latitudes 32,00° à 36,02° (Nord du Maroc).",
    f"- **Règle de rétention** : moyenne des pixels 250 m valides dans la maille LIS 5 km, cellule retenue uniquement si la couverture de pixels valides est ≥ 80 %.",
    f"- **Nombre de cellules retenues sur la grille LIS (couverture ≥ 80 %)** : {cnt_wp} mailles.",
    "- **Disponibilité temporelle** : rasters annuels (2018, 2019, 2020) pour AETI, E, T, NPP. Les fichiers dékadaires et mensuels ne sont pas archivés sur disque.",
    "- **Interception et AETI** : la composante interception (I) de WaPOR v3 n'étant pas disponible sur disque, ECanop et AETI total ne sont pas comparés et portent la mention `absent`.",
    "- **Métriques mensuelles/saisonnières** : en l'absence de fichiers dékadaires ou mensuels sur disque, ces métriques portent la mention `absent (WaPOR v3 dékadaire non archivé sur disque)`.",
    "- **Ratio de partitionnement** : `ratio_T_over_ETcomb` calculé en ratio des moyennes (somme T / somme (E+T)).",
    "",
    "---",
    "",
    "## 2. Tableaux Récapitulatifs Factuels",
    "",
    "### 2.1 Synthèse LAI Modèle vs MODIS en 2018 (Domaine et Bassins)",
    ""
])

sub_t1 = df_lai[(df_lai["period"] == 2018) | (df_lai["period"] == "2018")]
if "stratification_type" in sub_t1.columns:
    sub_t1 = sub_t1[sub_t1["stratification_type"] == "region"]
cols_t1 = ["experiment", "substitut", "region_or_class", "lai_model_annual_mean", "lai_modis_annual_mean", "bias_annual", "monthly_correlation", "peak_month_model", "peak_month_modis"]
rep_lines.append(df_to_markdown_simple(sub_t1[cols_t1]))

rep_lines.extend(["", "### 2.2 ΔLAI dû à l'Assimilation en 2018 (Domaine et Bassins)", ""])
sub_t2 = df_delta_lai[(df_delta_lai["period"] == 2018) | (df_delta_lai["period"] == "2018")]
if "stratification_type" in sub_t2.columns:
    sub_t2 = sub_t2[sub_t2["stratification_type"] == "region"]
cols_t2 = ["contrast", "region_or_class", "delta_lai_annual_mean", "delta_lai_m01", "delta_lai_m04", "delta_lai_m07", "delta_lai_m10"]
rep_lines.append(df_to_markdown_simple(sub_t2[cols_t2]))

rep_lines.extend(["", "### 2.3 Partition Annuelle de l'ET en 2018 (Domaine et Bassins)", ""])
sub_t3 = df_et_levels[((df_et_levels["period"] == 2018) | (df_et_levels["period"] == "2018")) & (df_et_levels["season"] == "Annuel")]
if "stratification_type" in sub_t3.columns:
    sub_t3 = sub_t3[sub_t3["stratification_type"] == "region"]
cols_t3 = ["experiment", "region_or_class", "ESoil_mm", "TVeg_mm", "ECanop_mm", "ET_total_mm", "fraction_TVeg", "fraction_ESoil", "fraction_ECanop"]
rep_lines.append(df_to_markdown_simple(sub_t3[cols_t3]))

rep_lines.extend(["", "### 2.4 Contrastes Annuels C1, C2, C3, C4 Décomposés par Composante (2018)", ""])
sub_t4 = df_et_contrasts[(df_et_contrasts["season"] == "Annuel")]
if "stratification_type" in sub_t4.columns:
    sub_t4 = sub_t4[sub_t4["stratification_type"] == "region"]
cols_t4 = ["contrast_id", "contrast_name", "region_or_class", "delta_ESoil_mm", "delta_TVeg_mm", "delta_ECanop_mm", "delta_ET_total_mm"]
rep_lines.append(df_to_markdown_simple(sub_t4[cols_t4]))

rep_lines.extend(["", "### 2.5 Comparaison Annuelle contre WaPOR v3 en 2018 (Domaine et Bassins)", ""])
sub_t5 = df_wapor_comp[((df_wapor_comp["period"] == 2018) | (df_wapor_comp["period"] == "2018")) & (df_wapor_comp["season"] == "Annuel")]
if "stratification_type" in sub_t5.columns:
    sub_t5 = sub_t5[sub_t5["stratification_type"] == "region"]
cols_t5 = ["experiment", "region_or_class", "n_cells_valid", "ESoil_model_mm", "E_wapor_mm", "bias_E_mm", "TVeg_model_mm", "T_wapor_mm", "bias_T_mm", "ETcomb_model_mm", "ETcomb_wapor_mm", "bias_ETcomb_mm", "ratio_T_over_ETcomb_model", "ratio_T_over_ETcomb_wapor"]
rep_lines.append(df_to_markdown_simple(sub_t5[cols_t5]))

rep_lines.extend(["", "### 2.6 Direction de Changement pour C2 et C3 contre WaPOR v3 en 2018", ""])
sub_t6 = df_doc
if "stratification_type" in sub_t6.columns:
    sub_t6 = sub_t6[sub_t6["stratification_type"] == "region"]
cols_t6 = ["contrast_id", "contrast_name", "component", "region_or_class", "n_cells_valid", "delta_abs_bias_mm", "pct_cells_closer", "pct_cells_farther", "pct_cells_neutral"]
rep_lines.append(df_to_markdown_simple(sub_t6[cols_t6]))

rep_lines.extend([
    "", "---", "", "## 3. Liste des Fichiers Produits", "",
    "### Tables CSV :",
    "- `paper1/tables/A1_lai_model_vs_modis.csv`",
    "- `paper1/tables/A1_delta_lai_assimilation.csv`",
    "- `paper1/tables/A1_et_partitioning_levels.csv`",
    "- `paper1/tables/A1_et_partitioning_contrasts.csv`",
    "- `paper1/tables/A1_wapor_et_comparison.csv`",
    "- `paper1/tables/A1_wapor_direction_of_change.csv`",
    "", "### Figures PNG :",
    "- `paper1/figures/A1_lai_bias_map_2018.png`",
    "- `paper1/figures/A1_delta_lai_monthly.png`",
    "- `paper1/figures/A1_et_partitioning_contrasts.png`",
    "- `paper1/figures/A1_wapor_direction_of_change.png`",
    "", "### Scripts :",
    "- `scripts/paper1/step_a1_vegetation_et_partition.py`",
    "- `paper1/scripts/step_a1_vegetation_et_partition.py`",
    "- `scripts/paper1/generate_report_a1.py`",
    ""
])

with open(REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_lines))

print(f"  [OK] Rapport {REPORT_PATH} régénéré avec succès (comptages dynamiques depuis les masques) !")
