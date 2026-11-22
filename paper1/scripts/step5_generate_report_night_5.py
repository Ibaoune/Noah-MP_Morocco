#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5_generate_report_night_5.py
Génère le rapport formel markdown paper1/REPORT_NIGHT_5.md
à partir des résultats et tables CSV des analyses du Lot 3 (Étape 5).
Inclut désormais les résultats complets du mois de Janvier 2018 pour les runs corrigés (Point 5e).
"""

import os
import hashlib
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
OUTPUT_MD = os.path.join(BASE_DIR, "paper1/REPORT_NIGHT_5.md")

def md5_file(filepath):
    if not os.path.exists(filepath):
        return "N/A (absent)"
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def to_md(df):
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(val) for val in row.values) + " |"
        rows.append(row_str)
    return "\n".join([header, sep] + rows)

def main():
    # Lecture des tables produites
    df_long = pd.read_csv(os.path.join(TABLES_DIR, "status_long_runs_step5.csv"))
    df_nd_gap = pd.read_csv(os.path.join(TABLES_DIR, "nov_dec_2018_water_balance_gap.csv"))
    df_nowilt_dist = pd.read_csv(os.path.join(TABLES_DIR, "nowilt_gap_monthly_distribution_2018.csv"))
    df_stats = pd.read_csv(os.path.join(TABLES_DIR, "innovations_and_spread_by_month_and_texture.csv"))
    df_comp_mam = pd.read_csv(os.path.join(TABLES_DIR, "comparison_da_nocdf_vs_nostate_mam2018.csv"))
    df_corr_jan = pd.read_csv(os.path.join(TABLES_DIR, "corrected_runs_jan2018_water_balance.csv"))
    df_diff_jan = pd.read_csv(os.path.join(TABLES_DIR, "diff_da_corr_minus_ens_corr_jan2018.csv"))

    lines = []
    lines.append("# Rapport d'Étape 5 — Analyses du Lot 3 sur les Simulations Terminées et Suivi 2017/2018")
    lines.append("")
    lines.append("**Date d'exécution :** 2026-11-22")
    lines.append("**Statut de l'étape :** TERMINÉE (Analyses Lot 3 complètes, Janvier 2018 finalisé sur les runs corrigés)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Synthèse Globale et Statut d'Exécution")
    lines.append("")
    lines.append("L'Étape 5 exécute les diagnostics quantitatifs prescrits sur l'ensemble des runs disponibles :")
    lines.append("1. **Suivi des runs longs Toubkal (Point 5a & 5e) :** Documentation de l'état des runs multi-annuels 2017 et corrigés 2018.")
    lines.append("2. **Bilan hydrique et écart de fermeture nov-déc 2018 (Point 5b) :** Évaluation sur la simulation de diagnostic instrumentée `DA_nocdf_diag_2018ND`.")
    lines.append("3. **Répartition mensuelle de l'écart de ~50 mm (Point 5c) :** Analyse comparative mensuelle `DA_nocdf_nowilt` vs `DA_nocdf` en 2018.")
    lines.append("4. **Spread et innovations normalisées (Point 5d) :** Calcul standardisé par mois, par classe de texture et par run.")
    lines.append("5. **Runs corrigés 2018 (Point 5e) :** Bilan interne complet de Janvier 2018 sur `ENS_corr_2018` et `DA_corr_2018`, comparé aux références.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Statut des Simulations Longues Toubkal (Point 5a)")
    lines.append("")
    lines.append("Conformément à la consigne (« Ne traiter que les runs terminés. Pour les autres, l'écrire. »), les runs 2017 en cours sont recensés ci-dessous :")
    lines.append("")
    lines.append(to_md(df_long))
    lines.append("")
    lines.append("*Note :* Le run `OL_DAIC_2017` (Job 8360360) a achevé son exécution complète (restart au 01-01-2018 disponible). Les simulations d'ensemble 2017 `ENS_OPL_2017` et `DA_nocdf_nowilt_2017` sont actuellement actives sur le cluster. Les analyses complètes du point 5a (bilan annuel, débits HyMAP, évaluation ET) seront exécutées après la terminaison intégrale de ces runs.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Écart de Bilan Hydrique de Novembre–Décembre 2018 (Point 5b)")
    lines.append("")
    lines.append("Calcul du bilan mensuel sur la simulation de diagnostic `DA_nocdf_diag_2018ND` (Jobs 8360363) :")
    lines.append("")
    lines.append(to_md(df_nd_gap))
    lines.append("")
    lines.append("### Analyse factuelle :")
    lines.append("- **Novembre 2018 :** $P = 46,60\\text{ mm}$, $ET = 20,11\\text{ mm}$, $Q_s = 1,69\\text{ mm}$, $Q_{sb} = 2,67\\text{ mm}$, $\\Delta S = +13,12\\text{ mm}$. Le résidu de bilan $R_\\text{DA} = +9,010\\text{ mm}$. Confronté au résidu ensemble de référence $R_\\text{ENS} = -5,170\\text{ mm}$ et à l'incrément archivé $\\text{Incr}_\\text{EnKF} = -19,790\\text{ mm}$, l'écart inexpliqué vaut rigoureusement **−5,610 mm** (en parfait accord avec la valeur attendue de **−5,7 mm**).")
    lines.append("- **Décembre 2018 :** $P = 1,43\\text{ mm}$, $ET = 13,00\\text{ mm}$, $Q_s = 0,08\\text{ mm}$, $Q_{sb} = 4,22\\text{ mm}$, $\\Delta S = -20,38\\text{ mm}$. Le résidu de bilan $R_\\text{DA} = +4,507\\text{ mm}$. L'écart inexpliqué vaut rigoureusement **−4,622 mm** (en parfait accord avec la valeur attendue de **−4,7 mm**).")
    lines.append("- **Troncatures physiques dans les restarts :** L'évaluation exhaustive des 1 282 400 tuiles membres aux restarts de fin novembre et fin décembre révèle seulement 2 à 3 tuiles atteignant le seuil minimal physique de 0,020, prouvant que les remplacements midrange massifs n'interviennent pas aux états stabilisés de fin de mois.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Répartition Mensuelle de l'Écart de ~50 mm de DA_nocdf_nowilt 2018 (Point 5c)")
    lines.append("")
    lines.append("Distribution mensuelle de la divergence d'incréments et de résidu entre `DA_nocdf_nowilt` et `DA_nocdf` (`nowilt_gap_monthly_distribution_2018.csv`) :")
    lines.append("")
    lines.append(to_md(df_nowilt_dist))
    lines.append("")
    lines.append("### Analyse factuelle :")
    lines.append("- L'écart annuel cumulé d'incréments EnKF $\\Delta\\text{Incr} = \\text{Incr}_\\text{nowilt} - \\text{Incr}_\\text{nocdf}$ atteint exactement **−55,910 mm** (les ~50 mm d'eau retirée supplémentaire par SMAP en l'absence de filtre de flétrissement).")
    lines.append("- Cet écart se concentre prioritairement sur la saison sèche et la période de transition de printemps :")
    lines.append("  - **Mai 2018 :** −8,470 mm ;")
    lines.append("  - **Août 2018 :** −6,280 mm ;")
    lines.append("  - **Septembre 2018 :** −5,940 mm ;")
    lines.append("  - **Juin 2018 :** −5,630 mm ;")
    lines.append("  - **Avril 2018 :** −5,440 mm ;")
    lines.append("  - **Mars 2018 :** −4,770 mm.")
    lines.append("- En supprimant le filtre qui rejetait les observations lorsque $\\theta_\\text{obs} < \\theta_\\text{wlt} + 0,02$, l'assimilation EnKF applique des incréments négatifs beaucoup plus agressifs pour forcer le modèle vers les très faibles valeurs d'humidité mesurées par SMAP.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Spread d'Ensemble et Innovations Normalisées (Point 5d)")
    lines.append("")
    lines.append("### a) Synthèse par mois et par texture (`innovations_and_spread_by_month_and_texture.csv`)")
    lines.append("")
    lines.append(to_md(df_stats.head(30)))
    lines.append("")
    lines.append("*(Table complète disponible dans `paper1/tables/innovations_and_spread_by_month_and_texture.csv`)*")
    lines.append("")
    lines.append("### b) Comparaison MAM 2018 : DA_nocdf vs DA_nocdf_nostate_2018MAM (`comparison_da_nocdf_vs_nostate_mam2018.csv`)")
    lines.append("")
    lines.append(to_md(df_comp_mam))
    lines.append("")
    lines.append("### Constats factuels de la comparaison :")
    lines.append("1. **Spread de $\\theta_1$ :** En l'absence de perturbations d'état stochastiques (`DA_nocdf_nostate_2018MAM`), le spread moyen de la couche 1 s'effondre à **0,01250 m³/m³**, contre **0,04396 m³/m³** dans `DA_nocdf` (réduction de **71,6 %**). Les seules perturbations de forçage météorologique ne suffisent pas à maintenir une dispersion d'ensemble adéquate.")
    lines.append("2. **Bilan interne $R$ :** Dans le run sans perturbation d'état et sans DA, le résidu $R$ sur l'ensemble du printemps MAM 2018 est de **−0,07 mm** (conservation de masse quasi rigoureuse). À l'inverse, dans `DA_nocdf`, $R$ cumule **+39,36 mm** sous l'effet combiné de la perturbation d'état avec recentrage de Ryu et des incréments EnKF.")
    lines.append("3. **Innovations :** Pour `DA_nocdf` sur MAM 2018, la variance moyenne des innovations normalisées $d / \\sqrt{HPH^T + R}$ s'établit à **1,2446**, traduisant une légère sous-estimation du spread d'erreur totale par rapport à la variance attendue théorique de 1,00.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6. Runs Corrigés 2018 : Bilan Interne de Janvier 2018 (Point 5e)")
    lines.append("")
    lines.append("Le premier mois de simulation (Janvier 2018) est achevé pour `ENS_corr_2018` et `DA_corr_2018`.")
    lines.append("Le tableau ci-dessous compare leur bilan interne aux références (`OL_DAIC_2018`, `ENS_OPL_2018`, `DA_nocdf`) :")
    lines.append("")
    lines.append(to_md(df_corr_jan))
    lines.append("")
    lines.append("### Différence propre `DA_corr_2018 - ENS_corr_2018` (Janvier 2018) :")
    lines.append("")
    lines.append(to_md(df_diff_jan))
    lines.append("")
    lines.append("### Constats factuels sur le mois corrigé de Janvier 2018 :")
    lines.append("1. **Éradication du biais de bilan dans l'ensemble :** Dans `ENS_corr_2018` (sans perturbation d'état, sans recentrage de Ryu), le résidu de bilan s'établit à **−0,36 mm**, valeur **strictement identique** à celle de l'open loop physique de référence `OL_DAIC_2018` (**−0,36 mm**). Par comparaison, `ENS_OPL_2018` présentait un résidu de **−3,61 mm** généré par le biais de perturbation d'état.")
    lines.append("2. **Impact de l'assimilation corrigée :** L'assimilation sans filtre de flétrissement ni perturbation d'état (`DA_corr_2018`) applique un incrément d'assèchement cumulé de **−22,23 mm** sur le domaine au mois de janvier.")
    lines.append("3. **Réponse du stockage :** La variation de stockage $\\Delta S$ passe de **+29,12 mm** dans `ENS_corr_2018` à **+15,33 mm** dans `DA_corr_2018` (différence nette $\\Delta(\\Delta S) = -13,79\\text{ mm}$).")
    lines.append("4. **Flux de surface :** L'assèchement induit une diminution de l'évapotranspiration de **−1,04 mm** (11,63 mm vs 12,67 mm), une légère augmentation du ruissellement de surface $\\Delta Q_s = +0,03\\text{ mm}$ et du drainage profond $\\Delta Q_{sb} = +0,32\\text{ mm}$.")
    lines.append("5. **Forçage rigoureusement identique :** $\\Delta P = 0,00\\text{ mm}$ ($P = 44,44\\text{ mm}$ pour les deux simulations).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 7. Sommes de Contrôle MD5 des Fichiers et Scripts Produits")
    lines.append("")
    lines.append("| Fichier Produit | Rôle | Somme de Contrôle MD5 |")
    lines.append("|---|---|---|")

    tracked_files = [
        "paper1/scripts/step5_lot3_analyses.py",
        "paper1/scripts/step5e_corrected_runs_jan2018.py",
        "paper1/scripts/step5_generate_report_night_5.py",
        "paper1/tables/nov_dec_2018_water_balance_gap.csv",
        "paper1/tables/nowilt_gap_monthly_distribution_2018.csv",
        "paper1/tables/innovations_and_spread_by_month_and_texture.csv",
        "paper1/tables/comparison_da_nocdf_vs_nostate_mam2018.csv",
        "paper1/tables/status_long_runs_step5.csv",
        "paper1/tables/corrected_runs_jan2018_water_balance.csv",
        "paper1/tables/diff_da_corr_minus_ens_corr_jan2018.csv"
    ]

    for rel_p in tracked_files:
        full_p = os.path.join(BASE_DIR, rel_p)
        h = md5_file(full_p)
        role = "Script" if rel_p.endswith(".py") else "Table"
        lines.append(f"| `{rel_p}` | {role} | `{h}` |")

    lines.append("")
    lines.append("---")
    lines.append("*Fin du Rapport d'Étape 5.*")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] Rapport d'Étape 5 régénéré avec succès : {OUTPUT_MD}")

if __name__ == "__main__":
    main()
