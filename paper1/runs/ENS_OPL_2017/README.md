# Run ENS_OPL_2017

- **Priorité** : P1
- **Job ID Slurm** : `8360359`
- **Binaire** : `./src/lisf/lis/make/LIS`
- **Période** : 2017-01-01 au 2018-01-01
- **Répertoire d'exécution HPC** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017`
- **Fichier de configuration** : [`lis_ENS_OPL_2017.config`](lis_ENS_OPL_2017.config)
- **Script de lancement** : [`run_ENS_OPL_2017.sh`](run_ENS_OPL_2017.sh)

## 1. But de l'expérience
Ensemble Open-Loop de 20 membres sur l'année sèche 2017 (P=177.03 mm) pour isoler l'effet d'ensemble sans assimilation.

## 2. Condition Initiale
Initialisé au 01-01-2017 à partir des restarts surface et perturbation d'ensemble de DA_nocdf_noirr_2016_2020.
- **Surface restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc`
- **Perturbations restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201701010000.d01.bin`

## 3. Différences avec la production
Pas d'assimilation (instances DA = 0). Perturbations forçages et état actives (schéma GMAO 20 membres).

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `8360359`
- **Logs** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017/logs/slurm_ENS_OPL_17_8360359.log`
