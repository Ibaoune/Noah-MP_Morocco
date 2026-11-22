#!/usr/bin/env python3
import csv, os

csv_path = "paper1/tables/jobs_status_night.csv"
md_path = "paper1/REPORT_NIGHT_0.md"

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

lines = []
lines.append("# Rapport Étape 0 — État des Jobs et Sécurisation des Exécutions")
lines.append("")
lines.append("## 1. Tableau d'État des Jobs")
lines.append("")
lines.append("| Job ID | Nom | État | Date Simulée Actuelle | Vitesse (dernière heure, j/h) | Fin Estimée | Limite `--time` | Risque Dépassement |")
lines.append("|---|---|---|---|---|---|---|---|")

for r in rows:
    lines.append(f"| {r['job_id']} | {r['job_name']} | {r['state']} | {r['current_simulated_date']} | {r['speed_last_hour_days_per_hour']} | {r['estimated_end']} | {r['time_limit']} | {r['risk_of_exceeding_limit']} |")

lines.append("")
lines.append("## 2. Analyse et Mesures Prises")
lines.append("")
lines.append("- **Jobs terminés avec succès (COMPLETED) :**")
lines.append("  - `8360360` (`OL_DAIC_2017`) : Simulation annuelle déterministe achevée en 02:12:02 (378 fichiers de sortie, restart finale `LIS_RST_NOAHMP401_201801010000.d01.nc`).")
lines.append("  - `8360363` (`DA_nocdf_diag_2018ND`) : Diagnostic de fermeture achevé en 03:02:39 (restart finale `LIS_RST_NOAHMP401_201901010000.d01.nc`).")
lines.append("  - `8360364` (`ENS_STATE_201803_noRyu`) : Mois de mars 2018 achevé en 01:30:23.")
lines.append("  - `8360365` (`ENS_FORC_201803_noRyu`) : Mois de mars 2018 achevé en 01:30:34.")
lines.append("  - `8360509` (`DA_nocdf_diag_15min_2018Nov`) : Run 15-min sur 5 jours achevé en 00:15:18.")
lines.append("  - `8360645` & `8360646` : Routages 5 ans `DA_nocdf` et `DA_cdf` linres0 achevés en ~29 min.")
lines.append("  - `8360678`, `8360679`, `8360680` : Routages 2018 linres0 (`OL_DAIC`, `ENS_OPL`, `DA_nocdf_nowilt`) achevés en ~6 min.")
lines.append("")
lines.append("- **Jobs en cours d'exécution (RUNNING) :**")
lines.append("  - `8360362` (`DA_nocdf_nostate_2018MAM`) : Période 2018-03-01 à 2018-06-01. Date simulée actuelle au 2018-05-08. Vitesse mesurée : 20.57 jours simulés/heure. Fin estimée vers 03:12:33 (temps restant ~1.2 h). Limite `--time=06:00:00` suffisante, aucun risque de dépassement.")
lines.append("  - `8360359` (`ENS_OPL_2017`) : Période 2017-01-01 à 2018-01-01 (20 membres). Date simulée actuelle au 2017-03-10. Vitesse mesurée : 20.52 jours simulés/heure. Fin estimée vers 16:31:08 le 2026-11-22. La limite de 16:00:00 expire vers 14:42:31. Risque avéré de dépassement (environ 2 mois manquants).")
lines.append("  - `8360361` (`DA_nocdf_nowilt_2017`) : Période 2017-01-01 à 2018-01-01 (20 membres). Date simulée actuelle au 2017-03-09. Vitesse mesurée : 20.22 jours simulés/heure. Fin estimée vers 16:46:37 le 2026-11-22. Risque avéré de dépassement.")
lines.append("  - `8360343` (`RegCM_Morocco`) : Processus externe de production de forçage, préservé intact.")
lines.append("")
lines.append("## 3. Sécurisation et Chaînage des Reprises")
lines.append("")
lines.append("Conformément aux instructions et à la règle de non-interruption des jobs en production, un système de reprise automatique a été mis en place et soumis sous Slurm :")
lines.append("1. **Script de reprise dynamique :** `paper1/scripts/resume_long_run.py` identifie automatiquement le dernier fichier restart mensuel (`LIS_RST_NOAHMP401_*.d01.nc` et `LIS_DAPERT_*.d01.bin`) présent dans le dossier de sortie, met à jour la configuration d'exécution (`lis_resume.config`) avec les dates et chemins exacts, et relance le binaire correspondant.")
lines.append("2. **Jobs Slurm chaînés avec dépendance :**")
lines.append("   - Job `8360931` (`ENS_17_res`) soumis avec `--dependency=afterany:8360359` pour reprendre `ENS_OPL_2017` dès l'arrêt du job initial.")
lines.append("   - Job `8360932` (`DA17_res`) soumis avec `--dependency=afterany:8360361` pour reprendre `DA_nocdf_nowilt_2017` dès l'arrêt du job initial.")
lines.append("   - Dossiers de sortie, configurations de base et binaires strictement identiques.")

with open(md_path, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Generated {md_path}")
