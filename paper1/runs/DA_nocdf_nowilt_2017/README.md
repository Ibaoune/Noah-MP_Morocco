# Run DA_nocdf_nowilt_2017

- **Priorité** : P2
- **Job ID Slurm** : `8360361`
- **Binaire** : `./src/lisf_nowilt/lis/LIS`
- **Période** : 2017-01-01 au 2018-01-01
- **Répertoire d'exécution HPC** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017`
- **Fichier de configuration** : [`lis_DA_nocdf_nowilt_2017.config`](lis_DA_nocdf_nowilt_2017.config)
- **Script de lancement** : [`run_DA_nocdf_nowilt_2017.sh`](run_DA_nocdf_nowilt_2017.sh)

## 1. But de l'expérience
Assimilation SMAP sans CDF et sans seuil QC de flétrissement sur l'année sèche 2017 (20 membres EnKF).

## 2. Condition Initiale
Initialisé au 01-01-2017 à partir des restarts de DA_nocdf_noirr_2016_2020.
- **Surface restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc`
- **Perturbations restart** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201701010000.d01.bin`

## 3. Différences avec la production
Binaire lisf_nowilt désactivant le rejet d'observation (smobs - smcwlt < 0.02). Exécution continue 1 an.

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `8360361`
- **Logs** : `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/logs/slurm_DA_nowilt_17_8360361.log`
