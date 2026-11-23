#!/usr/bin/env python3
# step18_contrasts_definition.py
# Génération de paper1/tables/contrasts_definition.csv
import os
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

contrasts = [{'contrast_code': 'ENS_OPL - OL_DAIC', 'run_x': 'ENS_OPL', 'run_y': 'OL_DAIC', 'objective_manuscript': 'Effet ensemble et perturbations standard', 'differences_between_runs': 'Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO) vs non perturbés ; état perturbé (GMAO) vs none ; binaire standard make/LIS'}, {'contrast_code': 'ENS_corr - OL_DAIC', 'run_x': 'ENS_corr', 'run_y': 'OL_DAIC', 'objective_manuscript': 'Effet ensemble corrigé (sans perturbation d état)', 'differences_between_runs': 'Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO) vs non perturbés ; état non perturbé dans les deux runs ; binaire lisf_corr vs make/LIS'}, {'contrast_code': 'DA_nocdf - ENS_OPL', 'run_x': 'DA_nocdf', 'run_y': 'ENS_OPL', 'objective_manuscript': 'Effet net de l assimilation SMAP native (production)', 'differences_between_runs': 'Assimilation EnKF SMAP active vs pas d assimilation ; mêmes perturbations de forçage et d état (GMAO) ; même binaire standard'}, {'contrast_code': 'DA_nocdf_nowilt - DA_nocdf', 'run_x': 'DA_nocdf_nowilt', 'run_y': 'DA_nocdf', 'objective_manuscript': 'Effet spécifique du filtre de flétrissement (censure)', 'differences_between_runs': 'Critère de flétrissement désactivé (patch lisf_nowilt) vs actif (standard) ; binaire lisf_nowilt vs lisf ; toutes les autres options et forçages identiques'}, {'contrast_code': 'DA_corr - ENS_corr', 'run_x': 'DA_corr', 'run_y': 'ENS_corr', 'objective_manuscript': 'Effet net de l assimilation SMAP sous formulation physique corrigée', 'differences_between_runs': 'Assimilation EnKF SMAP active sous lisf_corr vs open-loop ENS_corr ; aucune perturbation d état dans les deux runs ; binaire lisf_corr'}, {'contrast_code': 'DA_cdf - DA_nocdf', 'run_x': 'DA_cdf', 'run_y': 'DA_nocdf', 'objective_manuscript': 'Effet de la mise à l échelle climatologique par CDF matching', 'differences_between_runs': 'Stratégie de mise à l échelle: CDF matching (100 bins) vs none (retrievals natifs) ; binaire standard make/LIS'}]

df = pd.DataFrame(contrasts)
out_csv = os.path.join(TABLES_DIR, "contrasts_definition.csv")
df.to_csv(out_csv, index=False)
print(f"[OK] Sauvegardé {out_csv}")
