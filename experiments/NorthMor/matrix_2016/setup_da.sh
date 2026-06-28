#!/bin/bash
# Script to generate DA experiments

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/final_2016_2020

DA_SOURCE="../step3_da_2015"

for exp in DA_nocdf_noirr DA_cdf_noirr DA_nocdf_irr DA_cdf_irr; do
    echo "Setting up $exp..."
    mkdir -p $exp
    cp -r $DA_SOURCE/templates $exp/
    cp -r $DA_SOURCE/config $exp/
    cp -r $DA_SOURCE/scripts $exp/
    cp $DA_SOURCE/job.sh $exp/
    mkdir -p $exp/restarts/surf
    mkdir -p $exp/restarts/pert
    mkdir -p $exp/logs
    mkdir -p $exp/output
    mkdir -p $exp/generated

    # Update experiment.ini
    sed -i "s/StartDate = .*/StartDate = 2016-01-01/g" $exp/config/experiment.ini
    sed -i "s/EndDate = .*/EndDate = 2017-01-01/g" $exp/config/experiment.ini
    sed -i "s/ExperimentName = .*/ExperimentName = $exp/g" $exp/config/experiment.ini
    
    # Update chain_da.py
    # Change base_dir
    sed -i "s|base_dir = .*|base_dir = \"/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/final_2016_2020/$exp\"|g" $exp/scripts/chain_da.py
    
    # Change cd base_dir/../../../ to base_dir/../../../../
    sed -i "s|cd {base_dir}/../../../|cd {base_dir}/../../../../|g" $exp/scripts/chain_da.py
    
    # Fix the initial restart pull logic for 2016-01-01
    cat << 'EOF' > patch.py
import sys
with open(sys.argv[1], 'r') as f:
    code = f.read()

old_logic = """    if current_date == global_start_date:
        pert_start_mode = "coldstart"
    else:
        pert_start_mode = "restart"

    os.makedirs("generated/configs", exist_ok=True)"""

new_logic = """    if current_date == global_start_date:
        pert_start_mode = "restart"
    else:
        pert_start_mode = "restart"

    os.makedirs("generated/configs", exist_ok=True)"""
code = code.replace(old_logic, new_logic)

old_restart_logic = """    if not os.path.exists(surf_restart_path):
        print(f"Error: Required surface restart file {surf_restart_path} not found!")
        sys.exit(1)
        
    if not os.path.exists(pert_restart_path):
        print(f"Error: Required perturbation restart file {pert_restart_path} not found!")
        sys.exit(1)

    with open(template_path, "r") as f:
        template_text = f.read()

    config_out = f"generated/configs/lis_{exp_name}_{label}.config"
    
    config_text = template_text
    config_text = config_text.replace("__START_MODE__", start_mode)
    config_text = config_text.replace("__PERT_START_MODE__", pert_start_mode)
    config_text = config_text.replace("__START_YEAR__", current_date.strftime("%Y"))
    config_text = config_text.replace("__START_MONTH__", current_date.strftime("%m"))
    config_text = config_text.replace("__START_DAY__", current_date.strftime("%d"))
    config_text = config_text.replace("__END_YEAR__", next_date.strftime("%Y"))
    config_text = config_text.replace("__END_MONTH__", next_date.strftime("%m"))
    config_text = config_text.replace("__END_DAY__", next_date.strftime("%d"))
    config_text = config_text.replace("__SURF_RESTART_FILE__", f"{base_dir}/{surf_restart_path}")
    config_text = config_text.replace("__PERT_RESTART_FILE__", f"{base_dir}/{pert_restart_path}")"""

new_restart_logic = """    if current_date == global_start_date:
        # Pull from step3_da_2015 directly
        step3_base = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/step3_da_2015"
        surf_restart_full = f"{step3_base}/{surf_restart_path}"
        pert_restart_full = f"{step3_base}/{pert_restart_path}"
    else:
        surf_restart_full = f"{base_dir}/{surf_restart_path}"
        pert_restart_full = f"{base_dir}/{pert_restart_path}"

    if not os.path.exists(surf_restart_full):
        print(f"Error: Required surface restart file {surf_restart_full} not found!")
        sys.exit(1)
        
    if not os.path.exists(pert_restart_full):
        print(f"Error: Required perturbation restart file {pert_restart_full} not found!")
        sys.exit(1)

    with open(template_path, "r") as f:
        template_text = f.read()

    config_out = f"generated/configs/lis_{exp_name}_{label}.config"
    
    config_text = template_text
    config_text = config_text.replace("__START_MODE__", start_mode)
    config_text = config_text.replace("__PERT_START_MODE__", pert_start_mode)
    config_text = config_text.replace("__START_YEAR__", current_date.strftime("%Y"))
    config_text = config_text.replace("__START_MONTH__", current_date.strftime("%m"))
    config_text = config_text.replace("__START_DAY__", current_date.strftime("%d"))
    config_text = config_text.replace("__END_YEAR__", next_date.strftime("%Y"))
    config_text = config_text.replace("__END_MONTH__", next_date.strftime("%m"))
    config_text = config_text.replace("__END_DAY__", next_date.strftime("%d"))
    config_text = config_text.replace("__SURF_RESTART_FILE__", surf_restart_full)
    config_text = config_text.replace("__PERT_RESTART_FILE__", pert_restart_full)"""

code = code.replace(old_restart_logic, new_restart_logic)
with open(sys.argv[1], 'w') as f:
    f.write(code)
EOF
    python3 patch.py $exp/scripts/chain_da.py
    
    # Update job.sh
    sed -i "s|python3 scripts/chain_da.py .*|python3 scripts/chain_da.py --current-date \$START_DATE --submit|g" $exp/job.sh

    # Modify lis_da.config.template
    if [[ "$exp" == *"_irr"* ]]; then
        # irrigation
        # Insert irrigation configuration
        cat << 'EOF' > patch_template.py
import sys
with open(sys.argv[1], 'r') as f:
    text = f.read()

old_lsm = "#-----------------------LAND SURFACE MODELS--------------------------"
irr_block = """#-----------------------IRRIGATION CONFIGURATION---------------------
Irrigation scheme:                          "Sprinkler"
Irrigation output interval:                 "1da"
Irrigation threshold:                       0.50
Irrigation max soil layer depth:            2
Sprinkler irrigation max root depth file:   ./data/land_params/noahmp401_parms/maxrootdepth32.txt
Irrigation GVF parameter 1:                 0.40
Irrigation GVF parameter 2:                 0.00

"""
if irr_block not in text:
    text = text.replace(old_lsm, irr_block + old_lsm)
text = text.replace("lis_input_NorthMor_5km.nc", "lis_input_NorthMor_5km_irr.nc")
with open(sys.argv[1], 'w') as f:
    f.write(text)
EOF
        python3 patch_template.py $exp/templates/lis_da.config.template
    else
        # no irrigation
        cat << 'EOF' > patch_template_noirr.py
import sys
with open(sys.argv[1], 'r') as f:
    text = f.read()

old_lsm = "#-----------------------LAND SURFACE MODELS--------------------------"
irr_block = """#-----------------------IRRIGATION CONFIGURATION---------------------
Irrigation scheme:                          "none"

"""
if irr_block not in text:
    text = text.replace(old_lsm, irr_block + old_lsm)
with open(sys.argv[1], 'w') as f:
    f.write(text)
EOF
        python3 patch_template_noirr.py $exp/templates/lis_da.config.template
    fi

    if [[ "$exp" == *"_nocdf"* ]]; then
        # no cdf
        sed -i 's|Data assimilation scaling strategy:.*|Data assimilation scaling strategy:                   "none"|g' $exp/templates/lis_da.config.template
    else
        # cdf
        sed -i 's|Data assimilation scaling strategy:.*|Data assimilation scaling strategy:                   "CDF matching"|g' $exp/templates/lis_da.config.template
    fi

done
echo "Setup complete."
