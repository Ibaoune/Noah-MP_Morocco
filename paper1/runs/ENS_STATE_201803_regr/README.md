# Run : ENS_STATE_201803_regr
- Type : Test de non-régression (2 jours, 2018-03-01 au 2018-03-03)
- Binaire : `src/lisf_ryu/lis/LIS` (LIS patché lis_pert_bias_corr_read_config.patch)
- Option Ryu : `Apply perturbation bias correction: 1`
- Job Slurm ID : 8360358
- Résultat : Non-régression validée (écart = 0.000000e+00 sur SMC et ET par rapport à la production).
