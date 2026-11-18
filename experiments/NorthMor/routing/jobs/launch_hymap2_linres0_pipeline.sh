#!/bin/bash
# Script d'orchestration pour HyMAP-2 avec reservoir lineaire desactive (linres=0)
# Repond directement a la recommandation d'Augusto Getirana du 9 nov 2026.

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/jobs

echo "=========================================================="
echo "   ORCHESTRATION DU ROUTAGE HYMAP-2 (linres=0)"
echo "   Objectif : Correction des recessions estivales pour Augusto"
echo "=========================================================="
echo "Date de lancement : $(date)"

EXP=${1:-"all"}

launch_exp() {
    local name=$1
    local sp_script=$2
    local prod_script=$3

    echo ""
    echo ">>> [1/2] Soumission Spin-up 2016 pour ${name}..."
    JID_SP=$(sbatch --parsable "${sp_script}")
    echo "    Job Spin-up soumis : ID = ${JID_SP}"

    echo ">>> [2/2] Soumission Production 5 ans (2016-2020) pour ${name} (en attente du spinup ${JID_SP})..."
    JID_PROD=$(sbatch --parsable --dependency=afterok:${JID_SP} "${prod_script}")
    echo "    Job Production soumis : ID = ${JID_PROD} (dependance afterok:${JID_SP})"
}

case "$EXP" in
    opl)
        launch_exp "Open-Loop (OPL)" "run_hymap2_linres0_opl_spinup_2016.sh" "run_hymap2_linres0_opl_2016_2020.sh"
        ;;
    da_nocdf)
        launch_exp "SMAP DA sans CDF (DA_nocdf)" "run_hymap2_linres0_da_nocdf_spinup_2016.sh" "run_hymap2_linres0_da_nocdf_2016_2020.sh"
        ;;
    da_cdf)
        launch_exp "SMAP DA avec CDF (DA_cdf)" "run_hymap2_linres0_da_cdf_spinup_2016.sh" "run_hymap2_linres0_da_cdf_2016_2020.sh"
        ;;
    all)
        launch_exp "Open-Loop (OPL)" "run_hymap2_linres0_opl_spinup_2016.sh" "run_hymap2_linres0_opl_2016_2020.sh"
        launch_exp "SMAP DA sans CDF (DA_nocdf)" "run_hymap2_linres0_da_nocdf_spinup_2016.sh" "run_hymap2_linres0_da_nocdf_2016_2020.sh"
        launch_exp "SMAP DA avec CDF (DA_cdf)" "run_hymap2_linres0_da_cdf_spinup_2016.sh" "run_hymap2_linres0_da_cdf_2016_2020.sh"
        ;;
    *)
        echo "Usage: $0 [opl|da_nocdf|da_cdf|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================================="
echo "Soumissions transmises avec succes."
echo "Suivi : squeue -u \$USER"
echo "=========================================================="
