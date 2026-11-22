# Rapport Étape 0 — État des Jobs et Sécurisation des Exécutions

## 1. Tableau d'État des Jobs

| Job ID | Nom | État | Date Simulée Actuelle | Vitesse (dernière heure, j/h) | Fin Estimée | Limite `--time` | Risque Dépassement |
|---|---|---|---|---|---|---|---|
| 8360343 | RegCM_Morocco | RUNNING | Production externe | N/A | Indeterminee | 1-12:00:00 | non |
| 8360359 | ENS_OPL_2017 | RUNNING | 2017-03-10 00:00 | 20.52 | 2026-11-22 16:31:08 | 16:00:00 | oui |
| 8360360 | OL_DAIC_2017 | COMPLETED | 2018-01-01 | 0.00 | 2026-11-22T00:54:33 | 03:30:00 | non |
| 8360361 | DA_nocdf_nowilt_2017 | RUNNING | 2017-03-09 00:00 | 20.22 | 2026-11-22 16:46:37 | 16:00:00 | oui |
| 8360362 | DA_nocdf_nostate_2018MAM | RUNNING | 2018-05-08 00:00 | 20.57 | 2026-11-22 03:12:33 | 06:00:00 | non |
| 8360363 | DA_nocdf_diag_2018ND | COMPLETED | 2019-01-01 | 0.00 | 2026-11-22T01:45:10 | 04:30:00 | non |
| 8360364 | ENS_STATE_201803_noRyu | COMPLETED | 2018-04-01 | 0.00 | 2026-11-22T00:18:54 | 04:00:00 | non |
| 8360365 | ENS_FORC_201803_noRyu | COMPLETED | 2018-04-01 | 0.00 | 2026-11-22T00:19:05 | 04:00:00 | non |
| 8360509 | DA_nocdf_diag_15min_2018Nov | COMPLETED | 2018-11-06 | 0.00 | 2026-11-21T23:49:50 | 02:00:00 | non |
| 8360645 | hm2_5y_lr0_da_nocdf | COMPLETED | 2021-01-01 | 0.00 | 2026-11-22T00:54:02 | 01:15:00 | non |
| 8360646 | hm2_5y_lr0_da_cdf | COMPLETED | 2021-01-01 | 0.00 | 2026-11-22T00:53:43 | 01:15:00 | non |
| 8360678 | hm2_ol_daic_2018_linres0 | COMPLETED | 2019-01-01 | 0.00 | 2026-11-22T00:43:36 | 00:30:00 | non |
| 8360679 | hm2_ens_opl_2018_linres0 | COMPLETED | 2019-01-01 | 0.00 | 2026-11-22T00:43:33 | 00:30:00 | non |
| 8360680 | hm2_da_nocdf_nowilt_2018_linres0 | COMPLETED | 2019-01-01 | 0.00 | 2026-11-22T00:43:34 | 00:30:00 | non |

## 2. Analyse et Mesures Prises

- **Jobs terminés avec succès (COMPLETED) :**
  - `8360360` (`OL_DAIC_2017`) : Simulation annuelle déterministe achevée en 02:12:02 (378 fichiers de sortie, restart finale `LIS_RST_NOAHMP401_201801010000.d01.nc`).
  - `8360363` (`DA_nocdf_diag_2018ND`) : Diagnostic de fermeture achevé en 03:02:39 (restart finale `LIS_RST_NOAHMP401_201901010000.d01.nc`).
  - `8360364` (`ENS_STATE_201803_noRyu`) : Mois de mars 2018 achevé en 01:30:23.
  - `8360365` (`ENS_FORC_201803_noRyu`) : Mois de mars 2018 achevé en 01:30:34.
  - `8360509` (`DA_nocdf_diag_15min_2018Nov`) : Run 15-min sur 5 jours achevé en 00:15:18.
  - `8360645` & `8360646` : Routages 5 ans `DA_nocdf` et `DA_cdf` linres0 achevés en ~29 min.
  - `8360678`, `8360679`, `8360680` : Routages 2018 linres0 (`OL_DAIC`, `ENS_OPL`, `DA_nocdf_nowilt`) achevés en ~6 min.

- **Jobs en cours d'exécution (RUNNING) :**
  - `8360362` (`DA_nocdf_nostate_2018MAM`) : Période 2018-03-01 à 2018-06-01. Date simulée actuelle au 2018-05-08. Vitesse mesurée : 20.57 jours simulés/heure. Fin estimée vers 03:12:33 (temps restant ~1.2 h). Limite `--time=06:00:00` suffisante, aucun risque de dépassement.
  - `8360359` (`ENS_OPL_2017`) : Période 2017-01-01 à 2018-01-01 (20 membres). Date simulée actuelle au 2017-03-10. Vitesse mesurée : 20.52 jours simulés/heure. Fin estimée vers 16:31:08 le 2026-11-22. La limite de 16:00:00 expire vers 14:42:31. Risque avéré de dépassement (environ 2 mois manquants).
  - `8360361` (`DA_nocdf_nowilt_2017`) : Période 2017-01-01 à 2018-01-01 (20 membres). Date simulée actuelle au 2017-03-09. Vitesse mesurée : 20.22 jours simulés/heure. Fin estimée vers 16:46:37 le 2026-11-22. Risque avéré de dépassement.
  - `8360343` (`RegCM_Morocco`) : Processus externe de production de forçage, préservé intact.

## 3. Sécurisation et Chaînage des Reprises

Conformément aux instructions et à la règle de non-interruption des jobs en production, un système de reprise automatique a été mis en place et soumis sous Slurm :
1. **Script de reprise dynamique :** `paper1/scripts/resume_long_run.py` identifie automatiquement le dernier fichier restart mensuel (`LIS_RST_NOAHMP401_*.d01.nc` et `LIS_DAPERT_*.d01.bin`) présent dans le dossier de sortie, met à jour la configuration d'exécution (`lis_resume.config`) avec les dates et chemins exacts, et relance le binaire correspondant.
2. **Jobs Slurm chaînés avec dépendance :**
   - Job `8360931` (`ENS_17_res`) soumis avec `--dependency=afterany:8360359` pour reprendre `ENS_OPL_2017` dès l'arrêt du job initial.
   - Job `8360932` (`DA17_res`) soumis avec `--dependency=afterany:8360361` pour reprendre `DA_nocdf_nowilt_2017` dès l'arrêt du job initial.
   - Dossiers de sortie, configurations de base et binaires strictement identiques.
