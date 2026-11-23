#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération du rapport factuel REPORT_A1.md à partir des tables CSV produites par l'étape A1.
Ne contient aucune phrase d'interprétation ni spéculation.
"""

import os
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

n_land = int(np.count_nonzero(landmask_181))
cnt_lc = 180
cnt_sj = 170
cnt_sa = 227
cnt_wp = 5379

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
    "",
    "---",
    "",
    "## 2. Tableaux Récapitulatifs Factuels",
    "",
    "### 2.1 Synthèse LAI Modèle vs MODIS en 2018 (Domaine et Bassins)",
    ""
])

sub_t1 = df_lai[(df_lai["period"] == "2018") & (df_lai["stratification_type"] == "region")]
cols_t1 = ["experiment", "substitut", "region_or_class", "lai_model_annual_mean", "lai_modis_annual_mean", "bias_annual", "monthly_correlation", "peak_month_model", "peak_month_modis"]
rep_lines.append(df_to_markdown_simple(sub_t1[cols_t1]))

rep_lines.extend(["", "### 2.2 ΔLAI dû à l'Assimilation en 2018 (Domaine et Bassins)", ""])
sub_t2 = df_delta_lai[(df_delta_lai["period"] == "2018") & (df_delta_lai["stratification_type"] == "region")]
cols_t2 = ["contrast", "region_or_class", "delta_lai_annual_mean", "delta_lai_m01", "delta_lai_m04", "delta_lai_m07", "delta_lai_m10"]
rep_lines.append(df_to_markdown_simple(sub_t2[cols_t2]))

rep_lines.extend(["", "### 2.3 Partition Annuelle de l'ET en 2018 (Domaine et Bassins)", ""])
sub_t3 = df_et_levels[(df_et_levels["period"] == "2018") & (df_et_levels["season"] == "Annuel") & (df_et_levels["stratification_type"] == "region")]
cols_t3 = ["experiment", "region_or_class", "ESoil_mm", "TVeg_mm", "ECanop_mm", "ET_total_mm", "fraction_TVeg", "fraction_ESoil", "fraction_ECanop"]
rep_lines.append(df_to_markdown_simple(sub_t3[cols_t3]))

rep_lines.extend(["", "### 2.4 Contrastes Annuels C1, C2, C3, C4 Décomposés par Composante (2018)", ""])
sub_t4 = df_et_contrasts[(df_et_contrasts["season"] == "Annuel") & (df_et_contrasts["stratification_type"] == "region")]
cols_t4 = ["contrast_id", "contrast_name", "region_or_class", "delta_ESoil_mm", "delta_TVeg_mm", "delta_ECanop_mm", "delta_ET_total_mm"]
rep_lines.append(df_to_markdown_simple(sub_t4[cols_t4]))

rep_lines.extend(["", "### 2.5 Comparaison Annuelle contre WaPOR v3 en 2018 (Domaine et Bassins)", ""])
sub_t5 = df_wapor_comp[(df_wapor_comp["period"] == "2018") & (df_wapor_comp["season"] == "Annuel") & (df_wapor_comp["stratification_type"] == "region")]
cols_t5 = ["experiment", "region_or_class", "n_cells_valid", "ESoil_model_mm", "E_wapor_mm", "bias_E_mm", "TVeg_model_mm", "T_wapor_mm", "bias_T_mm", "ETcomb_model_mm", "ETcomb_wapor_mm", "bias_ETcomb_mm", "ratio_T_over_ETcomb_model", "ratio_T_over_ETcomb_wapor"]
rep_lines.append(df_to_markdown_simple(sub_t5[cols_t5]))

rep_lines.extend(["", "### 2.6 Direction de Changement pour C2 et C3 contre WaPOR v3 en 2018", ""])
sub_t6 = df_doc[(df_doc["stratification_type"] == "region")]
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
    ""
])

with open(REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_lines))

print(f"  [OK] Rapport {REPORT_PATH} généré avec succès !")
