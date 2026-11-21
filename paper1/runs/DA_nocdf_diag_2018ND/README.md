# Run DA_nocdf_diag_2018ND

- **Priorité** : P1
- **Job ID Slurm** : `8360363`
- **Binaire** : `./src/lisf/lis/make/LIS`
- **Période** : 2018-11-01 au 2019-01-01
- **Répertoire d'exécution HPC** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND`
- **Fichier de configuration** : [`lis_DA_nocdf_diag_2018ND.config`](lis_DA_nocdf_diag_2018ND.config)
- **Script de lancement** : [`run_DA_nocdf_diag_2018ND.sh`](run_DA_nocdf_diag_2018ND.sh)

## 1. But de l'expérience
Run de diagnostic de fermeture du bilan hydrique sur novembre-décembre 2018 avec archivage complet des incréments et diagnostics.

## 2. Condition Initiale
Initialisé au 01-11-2018 à partir des restarts de DA_nocdf_noirr_2016_2020.
- **Surface restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201811010000.d01.nc`
- **Perturbations restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201811010000.d01.bin`

## 3. Différences avec la production
Exécution continue sur 2 mois (novembre-décembre 2018) dans un seul run au lieu de chunks mensuels indépendants.

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `8360363`
- **Logs** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/logs/slurm_DA_diag_18ND_8360363.log`
