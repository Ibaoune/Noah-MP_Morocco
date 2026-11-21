# Statut des Runs de Robustesse et de Diagnostic — Papier 1

| run_name | priority | job_id | status | period | binary | walltime | purpose |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_OPL_2017 | P1 | 8360359 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf/lis/make/LIS | 16:00:00 | Ensemble Open-Loop de 20 membres sur l'année sèche 2017 (P=177.03 mm) pour isoler l'effet d'ensemble sans assimilation. |
| OL_DAIC_2017 | P1 | 8360360 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf/lis/make/LIS | 03:30:00 | Simulation déterministe (1 membre) sur l'année sèche 2017 avec la même condition initiale que l'ensemble (membre le plus proche de l'eau colonne moyenne). |
| DA_nocdf_nowilt_2017 | P2 | 8360361 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf_nowilt/lis/LIS | 16:00:00 | Assimilation SMAP sans CDF et sans seuil QC de flétrissement sur l'année sèche 2017 (20 membres EnKF). |
| DA_nocdf_nostate_2018MAM | P2 | 8360362 | SUBMITTED | 2018-03 to 2018-06 | ./src/lisf/lis/make/LIS | 06:00:00 | Diagnostic de spread en assimilation SMAP sans perturbation additive d'état sur mars-mai 2018 (3 mois). |
| DA_nocdf_diag_2018ND | P1 | 8360363 | SUBMITTED | 2018-11 to 2019-01 | ./src/lisf/lis/make/LIS | 04:30:00 | Run de diagnostic de fermeture du bilan hydrique sur novembre-décembre 2018 avec archivage complet des incréments et diagnostics. |

*Note : Ce tableau est généré directement à partir de `paper1/tables/runs_status.csv` par `paper1/scripts/setup_runs.py`.*
