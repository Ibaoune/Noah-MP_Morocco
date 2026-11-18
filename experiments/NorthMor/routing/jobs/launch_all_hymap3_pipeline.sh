#!/bin/bash
# Script d'orchestration globale pour la chaine de routage HyMAP-3 (3 experiences : OPL, DA-NoCDF, DA-CDF)
# Soumet d'abord le spin-up 2016 (1 an), puis enchaine automatiquement sur la production 5 ans (2016-2020) via --dependency=afterok

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/jobs

echo "=========================================================="
echo "   ORCHESTRATION DU ROUTAGE HYMAP-3 (linres=0)"
echo "   Domaine Nord Maroc (0.05°) - 2016 à 2020"
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
        launch_exp "Open-Loop (OPL)" "run_hymap3_opl_spinup_2016.sh" "run_hymap3_opl_2016_2020.sh"
        ;;
    da_nocdf)
        launch_exp "SMAP DA sans CDF (DA_nocdf)" "run_hymap3_da_nocdf_spinup_2016.sh" "run_hymap3_da_nocdf_2016_2020.sh"
        ;;
    da_cdf)
        launch_exp "SMAP DA avec CDF (DA_cdf)" "run_hymap3_da_cdf_spinup_2016.sh" "run_hymap3_da_cdf_2016_2020.sh"
        ;;
    all)
        launch_exp "Open-Loop (OPL)" "run_hymap3_opl_spinup_2016.sh" "run_hymap3_opl_2016_2020.sh"
        launch_exp "SMAP DA sans CDF (DA_nocdf)" "run_hymap3_da_nocdf_spinup_2016.sh" "run_hymap3_da_nocdf_2016_2020.sh"
        launch_exp "SMAP DA avec CDF (DA_cdf)" "run_hymap3_da_cdf_spinup_2016.sh" "run_hymap3_da_cdf_2016_2020.sh"
        ;;
    *)
        echo "Usage: $0 [opl|da_nocdf|da_cdf|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================================="
echo "Toutes les soumissions demandees ont ete transmises a SLURM."
echo "Pour suivre l'avancement : squeue -u \$USER"
echo "=========================================================="
