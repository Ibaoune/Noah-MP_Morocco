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
