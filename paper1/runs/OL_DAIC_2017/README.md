# Run OL_DAIC_2017

- **Priorité** : P1
- **Job ID Slurm** : `8360360`
- **Binaire** : `./src/lisf/lis/make/LIS`
- **Période** : 2017-01-01 au 2018-01-01
- **Répertoire d'exécution HPC** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017`
- **Fichier de configuration** : [`lis_OL_DAIC_2017.config`](lis_OL_DAIC_2017.config)
- **Script de lancement** : [`run_OL_DAIC_2017.sh`](run_OL_DAIC_2017.sh)

## 1. But de l'expérience
Simulation déterministe (1 membre) sur l'année sèche 2017 avec la même condition initiale que l'ensemble (membre le plus proche de l'eau colonne moyenne).

## 2. Condition Initiale
Restart 1 membre généré par paper1/scripts/create_restart_daic_2017.py. Écart stock humidité colonne = -0.0290 mm (< 0.5 mm).
- **Surface restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc`
- **Perturbations restart** : `none`

## 3. Différences avec la production
1 membre non perturbé, initialisé sur la trajectoire DA_nocdf plutôt que sur le spinup déterministe OPL.

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `8360360`
- **Logs** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/logs/slurm_OL_DAIC_17_8360360.log`
