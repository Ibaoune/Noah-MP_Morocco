# Run DA_nocdf_nostate_2018MAM

- **Priorité** : P2
- **Job ID Slurm** : `8360362`
- **Binaire** : `./src/lisf/lis/make/LIS`
- **Période** : 2018-03-01 au 2018-06-01
- **Répertoire d'exécution HPC** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM`
- **Fichier de configuration** : [`lis_DA_nocdf_nostate_2018MAM.config`](lis_DA_nocdf_nostate_2018MAM.config)
- **Script de lancement** : [`run_DA_nocdf_nostate_2018MAM.sh`](run_DA_nocdf_nostate_2018MAM.sh)

## 1. But de l'expérience
Diagnostic de spread en assimilation SMAP sans perturbation additive d'état sur mars-mai 2018 (3 mois).

## 2. Condition Initiale
Initialisé au 01-03-2018 à partir des restarts de DA_nocdf_noirr_2016_2020.
- **Surface restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201803010000.d01.nc`
- **Perturbations restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201803010000.d01.bin`

## 3. Différences avec la production
State perturbation algorithm: none (au lieu de GMAO scheme). Diagnostics DA complets activés (innovations, increments, spread).

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `8360362`
- **Logs** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/logs/slurm_DA_nost_18MAM_8360362.log`
