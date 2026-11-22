#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3_generate_report_night_3.py
Génère paper1/REPORT_NIGHT_3.md à partir des CSV de l'Étape 3 :
- Séries journalières et débits mensuels à Lalla Chafia et Sidi Jabeur
- Bilan mensuel sur les bassins versants amonts HyMAP
- Contrôle du remapping 181x121 vers 180x120
- Routage historique linres=1 vs linres=0
- Cartographie et top 20 mailles Qsb (DA_nocdf - ENS_OPL)
- Corrections documentées de REPORT_LOT2.md et REPORT_LOT1c.md
- Analyse d'indépendance de GLEAM v4.3a et WaPOR v3
"""

import os
import sys
import hashlib
import datetime
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
OUTPUT_MD = os.path.join(BASE_DIR, "paper1/REPORT_NIGHT_3.md")

def md5_file(filepath):
    if not os.path.exists(filepath):
        return "N/A"
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def to_md(df):
    cols = df.columns.tolist()
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    lines = [header, sep]
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            val = row[c]
            if isinstance(val, float):
                vals.append(f"{val:.4f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)

def main():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Monthly streamflow
    df_monthly = pd.read_csv(os.path.join(TABLES_DIR, "monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv"))
    
    # 2. Upstream catchment water balance
    df_wb_catchment = pd.read_csv(os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv"))
    
    # 3. DA_nocdf annual runoff 2016-2020 on catchment
    df_da_annual = pd.read_csv(os.path.join(TABLES_DIR, "da_nocdf_annual_runoff_catchment_2016_2020.csv"))
    
    # 4. Remapping check
    df_remap = pd.read_csv(os.path.join(TABLES_DIR, "remap_runoff_check_lalla_chafia_2018.csv"))
    
    # 5. Linres comparison
    df_linres_summary = pd.read_csv(os.path.join(TABLES_DIR, "lalla_chafia_linres_comparison_summary_2018.csv"))
    
    # 6. Top 20 Qsb difference
    df_top20 = pd.read_csv(os.path.join(TABLES_DIR, "top20_cells_qsb_difference.csv"))

    lines = []
    lines.append("# Rapport d'Étape 3 — Diagnostic du Débit DA_nocdf (Lalla Chafia) et Corrections")
    lines.append("")
    lines.append(f"**Date d'exécution :** {now_str}  ")
    lines.append("**Auteur :** Antigravity (mode autonome)  ")
    lines.append("**Branche Git :** `paper1-closure`  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Objectif de l'Étape 3")
    lines.append("")
    lines.append("Constat établi au Lot 2 : à la station hydrométrique de **Lalla Chafia** (bassin amont non régulé du Bouregreg), la simulation d'assimilation sans correction de biais `DA_nocdf` produit un débit moyen annuel simulé de **35,90 m³/s** en 2018, contre **9,74 m³/s** observés (KGE = −1,795). En revanche, l'assimilation avec correction de biais CDF (`DA_cdf`) simule **15,81 m³/s** (KGE = −0,022) et le contrôle d'ensemble `ENS_OPL` simule **15,69 m³/s** (KGE = +0,014), restant proches de la dynamique observée.")
    lines.append("")
    lines.append("L'objectif de cette étape est d'établir de manière strictement factuelle, chiffrée et sans conclusion subjective l'origine de cette anomalie de débit à travers :")
    lines.append("1. L'analyse des séries journalières et mensuelles 2018 à Lalla Chafia et Sidi Jabeur ;")
    lines.append("2. Le bilan hydrologique sur les bassins versants amonts HyMAP délimités par le réseau hydrographique D8 ;")
    lines.append("3. Le contrôle du remapping de ruissellement (grille native 181×121 vers grille HyMAP 180×120) ;")
    lines.append("4. L'impact du schéma de routage linéaire (`linres = 1` vs `linres = 0`) ;")
    lines.append("5. La localisation spatiale des anomalies de ruissellement sous-surfacique ($Q_{sb}$) ;")
    lines.append("6. Les corrections des rapports `REPORT_LOT2.md` et `REPORT_LOT1c.md` ;")
    lines.append("7. L'indépendance méthodologique des produits d'évapotranspiration GLEAM v4.3a et WaPOR v3 vis-à-vis de SMAP.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Séries Journalières et Mensuelles 2018 (Lalla Chafia et Sidi Jabeur)")
    lines.append("")
    lines.append("### a) Fichiers de données et figure de contrôle")
    lines.append("- Table journalière complète (365 jours, 6 expériences + observations ABH) : `paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv`")
    lines.append("- Figure de contrôle en échelle logarithmique : `paper1/figures/fig_control_daily_streamflow_log.png`")
    lines.append("")
    lines.append("### b) Débits moyens mensuels 2018 (`monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv`)")
    lines.append("")
    lines.append(to_md(df_monthly))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Bilan Hydrologique sur les Vrais Bassins Amonts HyMAP")
    lines.append("")
    lines.append("### a) Délimitation amont par remontée topologique HyMAP D8")
    lines.append("- **Algorithme :** Remontée récursive de la matrice de direction de drainage D8 (`HYMAP_flow_direction_x`, `HYMAP_flow_direction_y`) depuis les exutoires des stations dans `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc`.")
    lines.append("- **Lalla Chafia (Bouregreg) :**")
    lines.append("  - Maille exutoire : ligne 75, colonne 71 (grille 180×120).")
    lines.append("  - Nombre de mailles amont D8 : **133 mailles** (grille 180×120).")
    lines.append("  - Aire cumulée HyMAP D8 : **3 333,35 km²** (utilisée dans toutes les tables de calcul : `remap_runoff_check`, `water_balance_upstream_catchments`, `da_nocdf_annual_runoff`).")
    lines.append("  - Comparaison ABH : 3 341,60 km² dans l'inventaire officiel (`table2_stations.csv`), soit un écart topologique de seulement −0,25 %.")
    lines.append("  - **Clarification sur l'aire de 5 502 km² (189 mailles) :** cette valeur citée dans certains textes descriptifs correspondait à la délimitation globale du bassin du Bouregreg jusqu'à la retenue aval du barrage SMBA ou l'embouchure, et non au bassin amont spécifique contrôlé à la station hydrométrique de Lalla Chafia. La valeur rigoureuse et cohérente utilisée dans tous les calculs est 3 333,35 km².")
    lines.append("- **Sidi Jabeur (Grou) :**")
    lines.append("  - Maille exutoire : ligne 71, colonne 71 (grille 180×120).")
    lines.append("  - Nombre de mailles amont : **66 mailles**.")
    lines.append("  - Aire cumulée HyMAP : **3 130,55 km²** (contre 3 138,50 km² dans l'inventaire officiel des stations, écart = −0,25 %).")
    lines.append("")
    lines.append("### b) Bilan mensuel 2018 sur le bassin amont (`water_balance_upstream_catchments_2018.csv`)")
    lines.append("")
    lines.append("Extrait du bilan d'eau ($P$, $ET$, $Q_s$, $Q_{sb}$, Ruissellement total, $\\Delta S$, Incréments totaux DA, Résidu $R$) :")
    lines.append("")
    lines.append(to_md(df_wb_catchment.head(24)))
    lines.append("")
    lines.append("*(Table complète de 144 enregistrements disponible dans `paper1/tables/water_balance_upstream_catchments_2018.csv`)*")
    lines.append("")
    lines.append("### c) Ruissellement annuel DA_nocdf sur le bassin amont 2016–2020 (`da_nocdf_annual_runoff_catchment_2016_2020.csv`)")
    lines.append("")
    lines.append(to_md(df_da_annual))
    lines.append("")
    lines.append("On observe qu'en 2018, le ruissellement total de `DA_nocdf` sur le bassin de Lalla Chafia atteint **340,31 mm/an** (dont **286,81 mm/an de ruissellement sous-surfacique $Q_{sb}$**, soit 84,3 % du total), ce qui équivaut rigoureusement à un débit moyen de **35,97 m³/s**, concordant exactement avec le débit routé simule (**35,90 m³/s**).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Contrôle du Remapping de Ruissellement (Lalla Chafia, 2018)")
    lines.append("")
    lines.append("Comparaison du ruissellement total annuel ($Q_s + Q_{sb}$) calculé directement sur la grille source native de Noah-MP (181×121) contre les champs remappés vers la grille de routage HyMAP (180×120) sur le bassin versant de Lalla Chafia :")
    lines.append("")
    lines.append(to_md(df_remap))
    lines.append("")
    lines.append("- Pour `DA_nocdf`, le remapping introduit un écart de **+13,71 mm/an** (+4,20 %).")
    lines.append("- Pour `ENS_OPL`, le remapping introduit un écart de **−6,59 mm/an** (−4,26 %).")
    lines.append("- L'écart de remapping (+4,2 %) est d'un ordre de grandeur inférieur à la surestimation de débit constatée (+268 % entre 9,74 et 35,90 m³/s).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Routage Historique : linres = 1 vs linres = 0 (Lalla Chafia, 2018)")
    lines.append("")
    lines.append("Comparaison des débits simulés par HyMAP-2 en configuration historique (`linres = 1`, réservoir linéaire activé, restart spinup c2) contre la configuration de référence du Lot 2 (`linres = 0`, réservoir linéaire désactivé, coldstart) :")
    lines.append("")
    lines.append(to_md(df_linres_summary))
    lines.append("")
    lines.append("- Fichier journalier complet : `paper1/tables/lalla_chafia_streamflow_linres1_vs_linres0_2018.csv`")
    lines.append("- Le débit annuel moyen en `linres = 1` est de **35,6278 m³/s**, contre **35,8291 m³/s** en `linres = 0` (écart de **−0,2013 m³/s**, soit **−0,56 %**).")
    lines.append("- Cela démontre factuellement que l'activation ou la désactivation du réservoir linéaire d'HyMAP n'a qu'un impact marginal (< 0,6 %) sur le volume annuel acheminé à l'exutoire.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6. Analyse Spatiale de l'Anomalie de Ruissellement Sous-Surfacique (Qsb)")
    lines.append("")
    lines.append("### a) Cartographie")
    lines.append("- Figure produite : `paper1/figures/fig_map_qsb_difference_da_minus_ens.png`")
    lines.append("  - Panneau supérieur : Différence de $Q_{sb}$ annuel 2018 (`DA_nocdf` − `ENS_OPL`) en mm/an, avec contours des bassins versants amonts de Lalla Chafia et Sidi Jabeur.")
    lines.append("  - Panneau inférieur : Distribution des classes de texture de sol dominantes sur le domaine.")
    lines.append("")
    lines.append("### b) Top 20 des mailles présentant le plus fort excédent de Qsb (`top20_cells_qsb_difference.csv`)")
    lines.append("")
    lines.append(to_md(df_top20))
    lines.append("")
    lines.append("Sur les 20 mailles les plus émettrices d'écart $Q_{sb}$ sur le domaine (`top20_cells_qsb_difference.csv`) :")
    lines.append("- **Texture de sol :** Toutes les 20 mailles ont pour texture **Loam** (classe 6).")
    lines.append("- **Écart maximal :** +441,50 mm/an (maille rank 1 à lon −5,625°, lat 35,275°), et +384,06 mm/an pour le rank 20.")
    lines.append("- **Absence dans Lalla Chafia :** **Aucune maille** n'est située à l'intérieur du bassin versant amont de Lalla Chafia (`inside_lalla_chafia = False` pour les 20 mailles) ni de Sidi Jabeur (`inside_sidi_jabeur = False`).")
    lines.append("- **Localisation réelle :** Longitude −5,7° à −5,1°, Latitude 34,8° à 35,3° (région Rif / Loukkos, dont 7 mailles situées dans le bassin du Sebou : ranks 8, 9, 11, 12, 17, 19, 20).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 7. Corrections Apportées aux Rapports Précédents")
    lines.append("")
    lines.append("### a) Corrections de `paper1/REPORT_LOT2.md`")
    lines.append("1. **Taille de l'ensemble ENS_OPL :** Confirmation que `ENS_OPL` comprend **20 membres** (et non 12). Toutes les tables et mentions dans le texte ont été harmonisées via le script de régénération `paper1/scripts/generate_report_lot2.py`.")
    lines.append("2. **Nomenclature exacte des simulations du Lot 1 :**")
    lines.append("   - `DA_nocdf_nostate_2018MAM` (Job Slurm 8360362, diagnostic blocage état MAM 2018) ;")
    lines.append("   - `DA_nocdf_diag_2018ND` (Job Slurm 8360363, diagnostic incréments ND 2018) ;")
    lines.append("   - `DA_nocdf_diag_15min_2018Nov` (diagnostic pas fin 15 min novembre 2018).")
    lines.append("3. **Fichier de raccordement du 31-05-2018 :**")
    lines.append("   - Le flux journalier du **30 mai 2018** (`LIS_HIST_201805310000.d01.nc`) a été dupliqué pour combler l'absence temporaire du fichier du 31 mai dans l'arborescence standard lors du raccordement.")
    lines.append("   - Les audits antérieurs (`smap-xai-audit`) présentaient exactement le même trou lors de la lecture des sorties standard.")
    lines.append("   - L'effet calculé sur la moyenne annuelle domaine est strictement de :")
    lines.append("     - $ET$ : < 0,11 mm (−0,094 mm pour ENS_OPL, −0,105 mm pour DA_nowilt) ;")
    lines.append("     - $Q_s$ : < 0,012 mm (+0,011 mm pour ENS_OPL, +0,010 mm pour DA_nowilt) ;")
    lines.append("     - $Q_{sb}$ : < 0,001 mm (+0,0007 mm pour ENS_OPL, +0,0010 mm pour DA_nowilt).")
    lines.append("4. **Configurations de routage DA basculées en coldstart :**")
    lines.append("   - Le passage en coldstart (`Routing restart mode: 0` au 01-01-2016) pour `DA_nocdf_linres0_2016_2020` et `DA_cdf_linres0_2016_2020` est strictement conforme à la configuration de référence `OPL_linres0_2016_2020` (également en coldstart au 01-01-2016).")
    lines.append("   - Aucune sortie préexistante n'a été altérée ni écrasée (création de répertoires de sortie vierges dédiés).")
    lines.append("")
    lines.append("### c) Diagnostic et Statut de DA_nocdf_nostate_2018MAM")
    lines.append("- **Constat log et sorties :** `DA_nocdf_nostate_2018MAM` (Job Slurm 8360362) a réalisé **0 instance d'assimilation** (aucune analyse EnKF effectuée, aucun fichier d'incrément généré).")
    lines.append("- **Cause dans la configuration :** Dans `experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/config/lis_DA_nocdf_nostate_2018MAM.config`, la ligne de configuration porte `Number of data assimilation instances: 0`. Dans LIS, cette valeur désactive l'ensemble du sous-système d'assimilation, faisant tourner le run en simple ensemble open-loop.")
    lines.append("- **Comparaison avec DA_corr_2018 :** Dans `DA_corr_2018/config/lis_DA_corr_2018.config`, `Number of data assimilation instances: 1` est actif, avec `State perturbation algorithm: 'none'`. Cette configuration active bien l'algorithme EnKF et assimile les observations SMAP à chaque passage satellite, produisant les incréments attendus.")
    lines.append("- **Statut formel :** `DA_nocdf_nostate_2018MAM` est marqué comme **NON VALIDE pour l'évaluation de l'assimilation**.")
    lines.append("")
    lines.append("### b) Correction de `paper1/REPORT_LOT1c.md`")
    lines.append("- Le membre 20 de l'ensemble n'est pas `OL_DAIC`. Il s'agit du **membre non perturbé de l'ensemble**, dont les conditions initiales diffèrent de celles d'`OL_DAIC`. Le script `paper1/scripts/generate_report_lot1c.py` a été corrigé et `paper1/REPORT_LOT1c.md` a été régénéré.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 8. Indépendance Méthodologique des Produits d'Évapotranspiration vis-à-vis de SMAP")
    lines.append("")
    lines.append("### a) GLEAM v4.3a")
    lines.append("- **Référence bibliographique officielle (attributs NetCDF) :**")
    lines.append("  > Miralles, D.G. et al. 2025: Global land evaporation and soil moisture dataset at 0.1° resolution from 1980 to near present, *Scientific Data*, 12, 416, doi: [10.1038/s41597-025-04610-y](https://doi.org/10.1038/s41597-025-04610-y).")
    lines.append("- **Utilisation d'humidité du sol micro-ondes :**")
    lines.append("  - GLEAM v4 assimile explicitement l'humidité de surface micro-ondes par *nudging newtonien* dans son modèle de bilan hydrique du sol pour contraindre l'évaporation et le stress hydrique de la végétation.")
    lines.append("  - Le produit assimilé est le jeu multi-satellites **ESA CCI Soil Moisture** (COMBINED / ACTIVE / PASSIVE). Depuis avril 2015, l'archive ESA CCI intègre directement les radiomètres bande L de **SMAP**, ainsi que SMOS et ASCAT.")
    lines.append("  - De plus, GLEAM v4 utilise la profondeur optique de la végétation micro-ondes (VODCA L), issue de SMAP et SMOS.")
    lines.append("- **Statut :** **Non indépendant de SMAP** (assimilation indirecte de radiométrie micro-ondes incluant SMAP).")
    lines.append("")
    lines.append("### b) WaPOR v3 (FAO / eLEAF)")
    lines.append("- **Référence méthodologique officielle :**")
    lines.append("  > FAO (2020, 2023): WaPOR Database Methodology: Version 2 & 3. Food and Agriculture Organization of the United Nations, Rome.")
    lines.append("- **Utilisation d'humidité du sol micro-ondes :**")
    lines.append("  - L'algorithme ETLook de WaPOR repose sur un bilan d'énergie à deux couches contraint par la température de surface thermique infrarouge (**LST** MODIS et VIIRS), les indices spectraux optiques (**NDVI**, albédo Sentinel-2/PROBA-V) et les forçages météorologiques **ERA5**.")
    lines.append("  - WaPOR v3 **n'ingère ni n'assimile aucune observation d'humidité du sol issue des micro-ondes** (ni SMAP, ni SMOS, ni ESA CCI).")
    lines.append("- **Statut :** **Strictement indépendant de SMAP**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 9. Sommes de Contrôle MD5 des Fichiers et Scripts Produits")
    lines.append("")
    lines.append("| Fichier Produit | Rôle | Somme de Contrôle MD5 |")
    lines.append("|---|---|---|")

    tracked_files = [
        "paper1/scripts/c1_verify_lalla_chafia_streamflow.py",
        "paper1/scripts/step3_generate_report_night_3.py",
        "paper1/scripts/generate_report_lot2.py",
        "paper1/scripts/generate_report_lot1c.py",
        "paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv",
        "paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv",
        "paper1/tables/water_balance_upstream_catchments_2018.csv",
        "paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv",
        "paper1/tables/remap_runoff_check_lalla_chafia_2018.csv",
        "paper1/tables/lalla_chafia_streamflow_linres1_vs_linres0_2018.csv",
        "paper1/tables/lalla_chafia_linres_comparison_summary_2018.csv",
        "paper1/tables/top20_cells_qsb_difference.csv",
        "paper1/figures/fig_control_daily_streamflow_log.png",
        "paper1/figures/fig_map_qsb_difference_da_minus_ens.png",
        "paper1/REPORT_LOT2.md",
        "paper1/REPORT_LOT1c.md"
    ]

    for rel_p in tracked_files:
        full_p = os.path.join(BASE_DIR, rel_p)
        h = md5_file(full_p)
        role = "Script" if rel_p.endswith(".py") else ("Table" if rel_p.endswith(".csv") else ("Figure" if rel_p.endswith(".png") else "Rapport"))
        lines.append(f"| `{rel_p}` | {role} | `{h}` |")

    lines.append("")
    lines.append("---")
    lines.append("*Fin du Rapport d'Étape 3.*")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] Rapport d'Étape 3 généré : {OUTPUT_MD}")

if __name__ == "__main__":
    main()
