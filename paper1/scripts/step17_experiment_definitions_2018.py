#!/usr/bin/env python3
# step17_experiment_definitions_2018.py
# Génération de paper1/tables/experiment_definitions_2018.csv
import os
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

records = [{'experiment': 'OL_DAIC', 'forcing_perturbation': 'none', 'state_perturbation': 'none', 'recentering_bias_corr': '0 (disabled, lu lis.config/code)', 'wilting_criterion': 'Standard (smobs < smcwlt + 0.02)', 'cdf_matching': 'none', 'binary_used': './src/lisf/lis/make/LIS', 'initial_state': 'sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc (moyenne DA_nocdf 2018-01-01)'}, {'experiment': 'ENS_OPL', 'forcing_perturbation': 'GMAO scheme (1hr)', 'state_perturbation': 'GMAO scheme (3hr, noahmp_sm_pertattribs.txt)', 'recentering_bias_corr': '0 (disabled, lu lis.config/code)', 'wilting_criterion': 'Standard (smobs < smcwlt + 0.02)', 'cdf_matching': 'none', 'binary_used': './src/lisf/lis/make/LIS', 'initial_state': 'DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres)'}, {'experiment': 'ENS_corr', 'forcing_perturbation': 'GMAO scheme (1hr)', 'state_perturbation': 'none', 'recentering_bias_corr': '0 (disabled, lu lislog_ENS_corr_2018.0000)', 'wilting_criterion': 'Physique corrigé (lisf_corr: pas de troncature)', 'cdf_matching': 'none', 'binary_used': './src/lisf_corr/lis/LIS', 'initial_state': 'DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres)'}, {'experiment': 'DA_nocdf', 'forcing_perturbation': 'GMAO scheme (1hr)', 'state_perturbation': 'GMAO scheme (3hr, noahmp_sm_pertattribs.txt)', 'recentering_bias_corr': '0 (disabled, lu lis.config/code)', 'wilting_criterion': 'Standard (smobs < smcwlt + 0.02)', 'cdf_matching': 'none', 'binary_used': './src/lisf/lis/LIS', 'initial_state': 'DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres)'}, {'experiment': 'DA_nocdf_nowilt', 'forcing_perturbation': 'GMAO scheme (1hr)', 'state_perturbation': 'GMAO scheme (3hr, noahmp_sm_pertattribs.txt)', 'recentering_bias_corr': '0 (disabled, lu lis.config/code)', 'wilting_criterion': 'Inactif (désactivé: patch lisf_nowilt_qc_wilting)', 'cdf_matching': 'none', 'binary_used': './src/lisf_nowilt/lis/LIS', 'initial_state': 'DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres)'}, {'experiment': 'DA_corr', 'forcing_perturbation': 'GMAO scheme (1hr)', 'state_perturbation': 'none', 'recentering_bias_corr': '0 (disabled, lu lislog_DA_corr_2018.0000)', 'wilting_criterion': 'Physique corrigé (lisf_corr: mise à jour physique continue)', 'cdf_matching': 'none', 'binary_used': './src/lisf_corr/lis/LIS', 'initial_state': 'DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres)'}]

df = pd.DataFrame(records)
out_csv = os.path.join(TABLES_DIR, "experiment_definitions_2018.csv")
df.to_csv(out_csv, index=False)
print(f"[OK] Sauvegardé {out_csv}")
