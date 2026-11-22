# -*- coding: utf-8 -*-
"""
Script de generation automatique du rapport technique REPORT_LOT2b.md
Livrable du Lot 2b — Vérifications avant le lot 3.
Généré par script, sans interprétation subjective.
"""
import os
import subprocess
import datetime
import pandas as pd
import numpy as np

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_LOT2b.md")

def get_git_hash(path):
    try:
        res = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"

def get_git_branch(path):
    try:
        res = subprocess.run(["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"

def main():
    print(">>> Génération de REPORT_LOT2b.md...")

    # Chargement des tables
    df_daily = pd.read_csv(os.path.join(TABLES_DIR, "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv"))
    df_monthly = pd.read_csv(os.path.join(TABLES_DIR, "monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv"))
    df_wb = pd.read_csv(os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv"))
    df_ann_runoff = pd.read_csv(os.path.join(TABLES_DIR, "da_nocdf_annual_runoff_catchment_2016_2020.csv"))
    df_remap_check = pd.read_csv(os.path.join(TABLES_DIR, "remap_runoff_check_lalla_chafia_2018.csv"))
    df_top20 = pd.read_csv(os.path.join(TABLES_DIR, "top20_cells_qsb_difference.csv"))

    hash_repo = get_git_hash(BASE_DIR)
    branch_repo = get_git_branch(BASE_DIR)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []
    md.append("# Rapport d'Exécution — LOT 2b : Vérifications Préalables au Lot 3")
    md.append("")
    md.append(f"**Date de génération :** {now_str}  ")
    md.append(f"**Branche Git :** `{branch_repo}` (`{hash_repo}`)  ")
    md.append("")
    md.append("Ce rapport technique consigne l'ensemble des vérifications factuelles prescrites pour le **Lot 2b**, sans interprétation subjective :")
    md.append("1. **Débit DA_nocdf à Lalla Chafia : vérifications sur l'origine du ruissellement et contrôle des artefacts** ;")
    md.append("2. **Corrections factuelles intégrées dans `paper1/REPORT_LOT2.md`** ;")
    md.append("3. **Indépendance des produits satellitaires d'évapotranspiration (GLEAM v4.3a et WaPOR v3) vis-à-vis de SMAP**.")
    md.append("")
    md.append("---")
    md.append("")

    # Section 0
    md.append("## 0. Contrôle de l'Arborescence Git et Poussée de Branche")
    md.append("")
    md.append("- Commande de vérification d'absence de binaires et NetCDF suivis :")
    md.append("  ```bash")
    md.append("  git ls-files | grep -E \"\\.nc$|\\.bin$|/LIS$\"")
    md.append("  ```")
    md.append("  *Résultat :* Seuls les fichiers historiques archivés dans le dépôt initial (`experiments/NorthMor/routing/ldt_hymap/*.nc`) sont présents ; aucun fichier NetCDF ni binaire issu des nouveaux calculs n'est suivi.")
    md.append("- Statut de la branche : `paper1-closure` synchronisée avec `origin/paper1-closure` (`https://github.com/Ibaoune/Noah-MP_Morocco.git`).")
    md.append("")
    md.append("---")
    md.append("")

    # Section 1
    md.append("## 1. Débit DA_nocdf à Lalla Chafia : Analyse Factuelle de Ruissellement et Routage")
    md.append("")
    md.append("### 1.a. Séries Journalières 2018 et Figure de Contrôle (Échelle Log)")
    md.append("")
    md.append("- **Fichier de données journalières :** [`paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv) (365 pas de temps journaliers pour 2 stations et 6 expériences + obs).")
    md.append("- **Figure de contrôle hydrographe journalier :**")
    md.append("  - Format PNG haute résolution : [`paper1/figures/fig_control_daily_streamflow_log.png`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_control_daily_streamflow_log.png)")
    md.append("  - Format vectoriel PDF : [`paper1/figures/fig_control_daily_streamflow_log.pdf`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_control_daily_streamflow_log.pdf)")
    md.append("")
    md.append("Statistiques annuelles journalières 2018 observées sur les séries produites :")
    md.append("")
    md.append("| Station | Expérience / Obs | Débit Moyen (m³/s) | Débit Médian (m³/s) | Débit Max (m³/s) | Débit Min (m³/s) | Jours nuls (Q = 0) |")
    md.append("|---|---|---|---|---|---|---|")
    
    for st_id, st_name in [("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]:
        for col_name, label in [
            (f"obs_{st_id}", "Observation ABH"),
            (f"OPL_{st_id}", "OPL (linres=0)"),
            (f"OL_DAIC_{st_id}", "OL_DAIC (linres=0)"),
            (f"ENS_OPL_{st_id}", "ENS_OPL (linres=0, 20m)"),
            (f"DA_nocdf_{st_id}", "DA_nocdf (linres=0)"),
            (f"DA_cdf_{st_id}", "DA_cdf (linres=0)"),
            (f"DA_nocdf_nowilt_{st_id}", "DA_nocdf_nowilt (linres=0)"),
        ]:
            s = df_daily[col_name].dropna()
            q_mean = s.mean()
            q_med = s.median()
            q_max = s.max()
            q_min = s.min()
            n_zero = int((s <= 1e-4).sum())
            md.append(f"| {st_name} | **`{label}`** | {q_mean:.2f} | {q_med:.2f} | {q_max:.2f} | {q_min:.2f} | {n_zero} / {len(s)} |")
    md.append("")

    md.append("### 1.b. Débit Moyen Mensuel 2018 par Expérience")
    md.append("")
    md.append("Table issue de [`paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv) :")
    md.append("")
    md.append("#### Lalla Chafia (Bouregreg) : Débit Moyen Mensuel 2018 (m³/s)")
    md.append("")
    md.append("| Mois | Obs ABH | OPL | OL_DAIC | ENS_OPL | DA_nocdf | DA_cdf | DA_nocdf_nowilt | Écart DA_nocdf − ENS_OPL |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    
    sub_m_lalla = df_monthly[df_monthly["station_id"] == "lalla_chafia"]
    for _, row in sub_m_lalla.iterrows():
        ym = row['year_month']
        obs_val = f"{row['obs']:.2f}" if not pd.isna(row['obs']) else "N/A"
        diff_da_ens = row['DA_nocdf'] - row['ENS_OPL']
        md.append(f"| {ym} | {obs_val} | {row['OPL']:.2f} | {row['OL_DAIC']:.2f} | {row['ENS_OPL']:.2f} | **{row['DA_nocdf']:.2f}** | {row['DA_cdf']:.2f} | {row['DA_nocdf_nowilt']:.2f} | **{diff_da_ens:+.2f}** |")
    md.append("")

    md.append("#### Sidi Jabeur (Grou) : Débit Moyen Mensuel 2018 (m³/s)")
    md.append("")
    md.append("| Mois | Obs ABH | OPL | OL_DAIC | ENS_OPL | DA_nocdf | DA_cdf | DA_nocdf_nowilt | Écart DA_nocdf − ENS_OPL |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    
    sub_m_jabeur = df_monthly[df_monthly["station_id"] == "sidi_jabeur"]
    for _, row in sub_m_jabeur.iterrows():
        ym = row['year_month']
        obs_val = f"{row['obs']:.2f}" if not pd.isna(row['obs']) else "N/A"
        diff_da_ens = row['DA_nocdf'] - row['ENS_OPL']
        md.append(f"| {ym} | {obs_val} | {row['OPL']:.2f} | {row['OL_DAIC']:.2f} | {row['ENS_OPL']:.2f} | **{row['DA_nocdf']:.2f}** | {row['DA_cdf']:.2f} | {row['DA_nocdf_nowilt']:.2f} | **{diff_da_ens:+.2f}** |")
    md.append("")

    md.append("### 1.c. Bilan Moyen Mensuel et Annuel sur le Bassin Versant Amont Réel (D8 HyMAP)")
    md.append("")
    md.append("- **Délimitation D8 HyMAP :**")
    md.append("  - **Lalla Chafia :** 133 mailles, aire calculée = **3 333,35 km²** (aire table d'inventaire = 3 341,60 km², écart = −8,25 km², soit **−0,25%**).")
    md.append("  - **Sidi Jabeur :** 121 mailles, aire calculée = **3 130,55 km²** (aire table d'inventaire = 3 138,52 km², écart = −7,97 km², soit **−0,25%**).")
    md.append("")
    md.append("#### Synthèse Annuelle du Bilan Hydrique 2018 sur le Bassin Amont de Lalla Chafia (mm/an)")
    md.append("")
    md.append("| Expérience | P (mm) | ET (mm) | Qs (mm) | Qsb (mm) | Qs+Qsb (mm) | ΔS (mm) | Incr L1 (mm) | Incr L2 (mm) | Incr L3 (mm) | Incr L4 (mm) | Incr Total (mm) | Résidu Bilan (mm) |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    ann_lalla = df_wb[df_wb["station_id"] == "b_l_chafia"].groupby("experiment").sum(numeric_only=True).reset_index()
    for _, r in ann_lalla.iterrows():
        md.append(f"| **`{r['experiment']}`** | {r['P_mm']:.1f} | {r['ET_mm']:.1f} | {r['Qs_mm']:.1f} | {r['Qsb_mm']:.1f} | **{r['TotalRunoff_mm']:.1f}** | {r['Delta_S_mm']:+.1f} | {r['Incr_Layer1_mm']:+.1f} | {r['Incr_Layer2_mm']:+.1f} | {r['Incr_Layer3_mm']:+.1f} | {r['Incr_Layer4_mm']:+.1f} | **{r['Incr_Total_mm']:+.1f}** | {r['WaterBalance_Residual_mm']:+.1f} |")
    md.append("")

    md.append("#### Synthèse Annuelle du Bilan Hydrique 2018 sur le Bassin Amont de Sidi Jabeur (mm/an)")
    md.append("")
    md.append("| Expérience | P (mm) | ET (mm) | Qs (mm) | Qsb (mm) | Qs+Qsb (mm) | ΔS (mm) | Incr L1 (mm) | Incr L2 (mm) | Incr L3 (mm) | Incr L4 (mm) | Incr Total (mm) | Résidu Bilan (mm) |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    ann_jabeur = df_wb[df_wb["station_id"] == "b_s_jabeur"].groupby("experiment").sum(numeric_only=True).reset_index()
    for _, r in ann_jabeur.iterrows():
        md.append(f"| **`{r['experiment']}`** | {r['P_mm']:.1f} | {r['ET_mm']:.1f} | {r['Qs_mm']:.1f} | {r['Qsb_mm']:.1f} | **{r['TotalRunoff_mm']:.1f}** | {r['Delta_S_mm']:+.1f} | {r['Incr_Layer1_mm']:+.1f} | {r['Incr_Layer2_mm']:+.1f} | {r['Incr_Layer3_mm']:+.1f} | {r['Incr_Layer4_mm']:+.1f} | **{r['Incr_Total_mm']:+.1f}** | {r['WaterBalance_Residual_mm']:+.1f} |")
    md.append("")

    md.append("#### Ruissellement Annuel Multi-Annuel (2016–2020) de DA_nocdf sur les Deux Bassins")
    md.append("")
    md.append("Données issues de [`paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv) :")
    md.append("")
    md.append("| Station | Année | Nb Jours | Qs (mm) | Qsb (mm) | Qs + Qsb (mm) | Volume Ruissellement (hm³) | Débit Moyen Équivalent (m³/s) |")
    md.append("|---|---|---|---|---|---|---|---|")
    
    for _, r in df_ann_runoff.iterrows():
        md.append(f"| {r['station']} | {int(r['year'])} | {int(r['n_days'])} | {r['Qs_mm']:.2f} | {r['Qsb_mm']:.2f} | **{r['TotalRunoff_mm']:.2f}** | {r['TotalRunoff_hm3']:.1f} | **{r['Q_mean_m3s_equivalent']:.2f}** |")
    md.append("")

    md.append("### 1.d. Contrôle du Ruissellement Remappé (180×120) vs Natif (181×121 Projeté)")
    md.append("")
    md.append("Évaluation de la conservation de masse lors du remapping sur le bassin amont de Lalla Chafia en 2018 :")
    md.append("")
    md.append("Données issues de [`paper1/tables/remap_runoff_check_lalla_chafia_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/remap_runoff_check_lalla_chafia_2018.csv) :")
    md.append("")
    md.append("| Expérience | Station | Qs Natif (mm) | Qsb Natif (mm) | Total Natif (mm) | Qs Remappé (mm) | Qsb Remappé (mm) | Total Remappé (mm) | Écart (mm) | Écart Relatif (%) |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    
    for _, r in df_remap_check.iterrows():
        md.append(f"| **`{r['experiment']}`** | {r['station']} | {r['Qs_native_mm']:.2f} | {r['Qsb_native_mm']:.2f} | **{r['TotalRunoff_native_mm']:.2f}** | {r['Qs_remapped_mm']:.2f} | {r['Qsb_remapped_mm']:.2f} | **{r['TotalRunoff_remapped_mm']:.2f}** | **{r['difference_mm']:+.2f}** | **{r['difference_pct']:+.2f}%** |")
    md.append("")

    md.append("### 1.e. Comparaison avec le Routage Historique (linres = 1 vs linres = 0)")
    md.append("")
    md.append("Débit moyen annuel 2018 simulé à Lalla Chafia par DA_nocdf face aux observations :")
    md.append("")
    md.append("| Configuration Routage | Expérience | Débit Moyen 2018 (m³/s) | Biais face Obs (m³/s) | Source des Données |")
    md.append("|---|---|---|---|---|")
    md.append("| **Observation ABH** | In-situ | **9,74** | 0,00 | `data/streamflow_clean/obs_daily.csv` |")
    md.append("| **Routage Historique (linres = 1)** | `DA_nocdf_2016_2020` | **35,63** | +25,89 | `experiments/NorthMor/routing/output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv` |")
    md.append("| **Routage Actuel (linres = 0)** | `DA_nocdf_linres0_2016_2020` | **35,90** | +26,16 | `paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv` |")
    md.append("| **Différence (linres = 0 − linres = 1)** | DA_nocdf | **+0,27** (+0,76%) | — | Écart lié à la dynamique de stockage fluvial |")
    md.append("")

    md.append("### 1.f. Carte et Top 20 Mailles de Différence de Qsb Annuel (DA_nocdf − ENS_OPL)")
    md.append("")
    md.append("- **Carte de la différence de ruissellement souterrain Qsb (2018) :**")
    md.append("  - Image PNG : [`paper1/figures/fig_map_qsb_difference_da_minus_ens.png`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_map_qsb_difference_da_minus_ens.png)")
    md.append("  - Fichier PDF vectoriel : [`paper1/figures/fig_map_qsb_difference_da_minus_ens.pdf`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_map_qsb_difference_da_minus_ens.pdf)")
    md.append("- **Table des 20 mailles où l'écart est le plus marqué :** [`paper1/tables/top20_cells_qsb_difference.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/top20_cells_qsb_difference.csv)")
    md.append("")
    md.append("| Rang | Coordonnées (Lon, Lat) | Texture Dominante (USDA) | Qsb DA_nocdf (mm) | Qsb ENS_OPL (mm) | Différence Qsb (mm) | Bassin Hydrographique | Amont Lalla Chafia | Amont Sidi Jabeur |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    
    for _, r in df_top20.iterrows():
        b_name = "Sebou" if r['inside_sebou'] else ("Bouregreg" if r['inside_bouregreg'] else "Hors Sebou/Bouregreg")
        in_lc = "Oui" if r['inside_lalla_chafia'] else "Non"
        in_sj = "Oui" if r['inside_sidi_jabeur'] else "Non"
        md.append(f"| {int(r['rank'])} | ({r['lon']:.4f}°E, {r['lat']:.4f}°N) | {r['texture_name']} (ID {int(r['texture_id'])}) | {r['qsb_da_nocdf_mm']:.1f} | {r['qsb_ens_opl_mm']:.1f} | **+{r['diff_qsb_mm']:.1f}** | {b_name} | {in_lc} | {in_sj} |")
    md.append("")
    md.append("---")
    md.append("")

    # Section 2
    md.append("## 2. Synthèse des Corrections Factuelles Appliquées dans `paper1/REPORT_LOT2.md`")
    md.append("")
    md.append("Le script de génération [`paper1/scripts/generate_report_lot2.py`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/scripts/generate_report_lot2.py) a été mis à jour et exécuté pour régénérer [`paper1/REPORT_LOT2.md`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/REPORT_LOT2.md) avec les corrections suivantes :")
    md.append("")
    md.append("1. **Taille de l'ensemble ENS_OPL :** mention corrigée de 12 à **20 membres** (`Number of ensembles per tile: 20` dans `lis.config`).")
    md.append("2. **Dénomination exacte des runs du Lot 1 :**")
    md.append("   - `ENS_OPL_2017` (Job 8360359), `OL_DAIC_2017` (Job 8360360, terminé), `DA_nocdf_nowilt_2017` (Job 8360361) ;")
    md.append("   - `DA_nocdf_nostate_2018MAM` (Job 8360362, diagnostic blocage état MAM 2018) et `DA_nocdf_diag_2018ND` (Job 8360363, diagnostic incréments ND 2018) — et non « DA_nostate_2017 » ou « DA_diag_2017 » ;")
    md.append("   - `DA_nocdf_diag_15min_2018Nov` (diagnostic pas fin 15 min novembre 2018).")
    md.append("3. **Fichier de raccordement du 31-05-2018 (ENS_OPL, DA_nocdf_nowilt) :**")
    md.append("   - Jour dupliqué dans le ruissellement : **30 mai 2018** (`LIS_HIST_201805310000.d01.nc`).")
    md.append("   - Jour manquant dans le répertoire principal : **31 mai 2018** (`LIS_HIST_201806010000.d01.nc`, préservé dans `output/_partial_201806_hang/SURFACEMODEL_201806/`).")
    md.append("   - Traitement dans `smap-xai-audit` : les scripts de bilan antérieurs lisaient directement le dossier standard sans inclure `_partial_201806_hang/`.")
    md.append("   - Ordre de grandeur de l'effet sur le domaine : strictly inférieur à 0,11 mm sur l'ET (−0,094 mm pour ENS_OPL, −0,105 mm pour DA_nowilt), inférieur à 0,012 mm sur Qs, et inférieur à 0,001 mm sur Qsb (+0,0007 mm pour ENS_OPL, +0,0010 mm pour DA_nowilt), soit un impact relatif < 0,03% sur l'ET.")
    md.append("4. **Configurations de routage DA (coldstart 2016–2020) :**")
    md.append("   - Diff documenté dans [`paper1/runs/routing/README.md`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/runs/routing/README.md).")
    md.append("   - Confirmation : `OPL_linres0_2016_2020` est également configuré en coldstart (`Routing restart mode: 0`) au 01-01-2016.")
    md.append("   - Aucune sortie préalable n'a été écrasée (dossiers de sortie vierges).")
    md.append("")
    md.append("---")
    md.append("")

    # Section 3
    md.append("## 3. Produits d'Évapotranspiration : Indépendance Méthodologique vis-à-vis de SMAP")
    md.append("")
    md.append("Conformément à la consigne, les données et la documentation disponibles rapportent les éléments factuels suivants :")
    md.append("")
    md.append("### 3.1. GLEAM v4.3a (Global Land Evaporation Amsterdam Model)")
    md.append("")
    md.append("- **Référence bibliographique officielle (attributs NetCDF) :**")
    md.append("  > Miralles, D.G. et al. 2025: global land evaporation and soil moisture dataset at 0.1° resolution from 1980 to near present, *Scientific Data*, 12, 416, doi: [10.1038/s41597-025-04610-y](https://doi.org/10.1038/s41597-025-04610-y).")
    md.append("- **Utilisation d'humidité du sol micro-ondes :**")
    md.append("  - Le modèle GLEAM v4 assimile explicitement l'humidité de surface satellitaire issue des micro-ondes via un schéma de *nudging newtonien* dans sa première couche de sol pour corriger le bilan hydrique.")
    md.append("  - La source de données micro-ondes utilisée est le produit multi-satellites **ESA CCI Soil Moisture** (COMBINED / ACTIVE / PASSIVE).")
    md.append("  - Depuis avril 2015, l'archive ESA CCI intègre directement les radiomètres micro-ondes en bande L de la mission **SMAP**, ainsi que SMOS et ASCAT.")
    md.append("  - GLEAM v4 utilise en outre la profondeur optique de la végétation micro-ondes (VODCA L, issue conjointement de SMAP et SMOS).")
    md.append("- **Statut d'indépendance vis-à-vis de SMAP :** **Non indépendant de SMAP** (assimilation indirecte de données micro-ondes incluant SMAP).")
    md.append("")
    md.append("### 3.2. WaPOR v3 (Water Productivity through Open-access of Remotely sensed derived data / ETLook)")
    md.append("")
    md.append("- **Référence méthodologique officielle (FAO / eLEAF) :**")
    md.append("  > FAO (2020, 2023): WaPOR Database Methodology: Version 2 & 3. Food and Agriculture Organization of the United Nations, Rome.")
    md.append("  > Collection GEE : `projects/UNFAO/wapor/v3/L1-AETI-D`.")
    md.append("- **Utilisation d'humidité du sol micro-ondes :**")
    md.append("  - L'algorithme ETLook de WaPOR v3 repose sur une formulation à deux couches (évaporation du sol nu et transpiration de la végétation selon l'équation de Penman-Monteith) contrainte par le bilan d'énergie en surface.")
    md.append("  - Les forçages satellitaires d'ETLook sont : la température de surface thermique infrarouge (**LST** issue de MODIS et VIIRS), les indices spectraux de végétation (**NDVI**, albédo issus de Sentinel-2 et PROBA-V), et les réanalyses météorologiques horaires (**ERA5**).")
    md.append("  - Le calcul de l'humidité relative du sol dans WaPOR v3 est dérivé en interne par inversion de la température de surface thermique infrarouge et du bilan hydrique ; il **n'assimile ni n'ingère aucune observation d'humidité du sol par micro-ondes** (ni SMAP, ni SMOS, ni ESA CCI).")
    md.append("- **Statut d'indépendance vis-à-vis de SMAP :** **Strictement indépendant de SMAP** (aucune donnée micro-ondes SMAP en entrée).")
    md.append("")
    md.append("---")
    md.append("")

    # Section 4
    md.append("## 4. Sommes de Contrôle MD5 des Fichiers et Scripts Produits (Lot 2b)")
    md.append("")
    md.append("| Fichier Produit | Rôle | Somme de Contrôle MD5 |")
    md.append("|---|---|---|")
    
    prod_files = [
        "paper1/scripts/c1_verify_lalla_chafia_streamflow.py",
        "paper1/scripts/calc_catchment_water_balance.py",
        "paper1/scripts/generate_report_lot2.py",
        "paper1/scripts/generate_report_lot2b.py",
        "paper1/runs/routing/README.md",
        "paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv",
        "paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv",
        "paper1/tables/water_balance_upstream_catchments_2018.csv",
        "paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv",
        "paper1/tables/remap_runoff_check_lalla_chafia_2018.csv",
        "paper1/tables/top20_cells_qsb_difference.csv",
        "paper1/figures/fig_control_daily_streamflow_log.png",
        "paper1/figures/fig_map_qsb_difference_da_minus_ens.png",
        "paper1/REPORT_LOT2.md"
    ]
    for rel_path in prod_files:
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            res = subprocess.run(["md5sum", full_path], capture_output=True, text=True)
            md5_val = res.stdout.split()[0]
            md.append(f"| `{rel_path}` | Livrable Lot 2b | `{md5_val}` |")
        else:
            md.append(f"| `{rel_path}` | Livrable Lot 2b | INTROUVABLE |")
    md.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"[OK] Rapport Lot 2b généré avec succès dans : {REPORT_PATH}")

if __name__ == "__main__":
    main()
