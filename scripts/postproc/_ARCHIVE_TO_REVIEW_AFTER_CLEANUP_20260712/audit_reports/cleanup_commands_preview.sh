#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Phase B1 : Aperçu corrigé du nettoyage (Ne rien exécuter sans validation)
# =========================================================================

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc

echo "Suppression des dossiers de sortie temporaires et obsolètes..."
rm -rf outputs/matrix_2016/metrics
rm -rf outputs/matrix_2016/opl_vs_smap_da_scientific
rm -rf outputs/matrix_2016/pdf
rm -rf outputs/matrix_2016/smap_cdf_sensitivity_2016
rm -rf outputs/matrix_2016/tables
rm -rf outputs/matrix_2016/smap_da_extended_validation_2016

echo "Suppression des recettes parallèles..."
rm -f configs/recipes/opl_vs_smap_da_scientific_2016.yaml
rm -f configs/recipes/smap_da_extended_validation_2016.yaml

echo "Suppression des dossiers configs inutilisés..."
rm -rf configs/baselines/
rm -rf configs/product_catalogs/

echo "Suppression des composants Python de la pipeline parallèle..."
rm -f src/lis_postproc/core/capabilities.py
rm -f src/lis_postproc/core/diagnostic_registry.py
rm -f src/lis_postproc/core/provenance.py
rm -rf src/lis_postproc/diagnostics/quality_control/
rm -rf src/lis_postproc/diagnostics/water_balance/

echo "Suppression des scripts CLI obsolètes..."
rm -f scripts/run_scientific_postproc.py
rm -f scripts/postproc/scripts/run_scientific_postproc.py

echo "Suppression des tests associés..."
rm -f tests/core/test_capabilities.py
rm -f tests/core/test_diagnostic_registry.py
rm -f tests/core/test_provenance.py
rm -f tests/integration/test_run_scientific_postproc.py
rm -rf tests/quality_control/
rm -rf tests/water_balance/

echo "Suppression des outils d'audit..."
rm -rf tools/audit/

echo "Suppression des rapports Markdown/CSV d'audit..."
rm -f pipeline_scope_comparison.md
rm -f pipeline_diagnostic_overlap.csv
rm -f pipeline_output_overlap.csv
rm -f pipeline_module_overlap.csv
rm -f pipeline_consolidation_recommendation.md

echo "Création du nouveau dossier cible..."
mkdir -p outputs/matrix_2016/figures/smap_cdf_sensitivity/independent_ob_validation

echo "Nettoyage simulé terminé."
