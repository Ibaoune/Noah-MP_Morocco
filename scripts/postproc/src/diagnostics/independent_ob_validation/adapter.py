# Author: M. El Aabaribaoune (@um6p)
import os
import logging
import pandas as pd
from .dataset_registry import DatasetRegistry
from . import soil_moisture
from . import evapotranspiration
from . import vegetation
from . import water_storage
from . import model_benchmark

logger = logging.getLogger(__name__)

MODULE_MAP = {
    "soil_moisture": soil_moisture.run_validation,
    "evapotranspiration": evapotranspiration.run_validation,
    "vegetation": vegetation.run_validation,
    "water_storage": water_storage.run_validation,
    "model_benchmark": model_benchmark.run_validation
}

def run(recipe_config, global_config):
    """
    Point d'entrée pour la validation indépendante multi-source.
    """
    if "independent_ob_validation" not in recipe_config.get("diagnostics", {}):
        return

    val_config = recipe_config["diagnostics"]["independent_ob_validation"]
    if not val_config.get("enabled", False):
        return

    logger.info("Démarrage de la validation indépendante multi-source")
    
    experiments = recipe_config.get("experiments", [])
    
    outputs = recipe_config.get("outputs")
    if hasattr(outputs, "figure_dir"):
        out_dir = outputs.figure_dir
    elif isinstance(outputs, dict):
        out_dir = outputs.get("figure_dir", "outputs/matrix_2016/figures/smap_cdf_sensitivity")
    else:
        out_dir = "outputs/matrix_2016/figures/smap_cdf_sensitivity"
        
    val_out_dir = os.path.join(out_dir, "independent_obs_validation")
    os.makedirs(val_out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    config_dir = os.path.join(project_root, "scripts/postproc/configs/observations")
    registry = DatasetRegistry(config_dir)
    
    audit_records = []
    
    for module_name, func in MODULE_MAP.items():
        module_cfg = val_config.get(module_name, {})
        enabled = module_cfg.get("enabled", False)
        
        # Check registry for datasets in this category
        for ds_id, ds_cfg in registry.datasets.items():
            if ds_cfg.get("validation_category") == module_name:
                
                # Check readiness
                is_ready = ds_cfg.get("readiness_status", "") == "READY"
                skip_reason = ""
                status = "SKIPPED"
                
                if not enabled:
                    skip_reason = "Module disabled in recipe config"
                elif not is_ready:
                    skip_reason = "Dataset not READY in observation config"
                else:
                    try:
                        # Attempt to run
                        logger.info(f"[RUN] {ds_cfg['display_name']} ({module_name})")
                        func(module_cfg, experiments, val_out_dir)
                        status = "DONE"
                        logger.info(f"[DONE] {ds_cfg['display_name']}")
                    except Exception as e:
                        status = "FAILED"
                        skip_reason = str(e)
                        logger.error(f"[FAILED] {ds_cfg['display_name']}: {e}")
                        
                audit_records.append({
                    "Module": module_name,
                    "Dataset": ds_id,
                    "Enabled": enabled,
                    "Imported": True,
                    "Registered": True,
                    "Called": status == "DONE" or status == "FAILED",
                    "Observation ready": is_ready,
                    "Output generated": status == "DONE",
                    "Status": status,
                    "Skip reason": skip_reason
                })

    # Save audit
    data_inv_dir = os.path.join(val_out_dir, "data_inventory")
    os.makedirs(data_inv_dir, exist_ok=True)
    df_audit = pd.DataFrame(audit_records)
    df_audit.to_csv(os.path.join(val_out_dir, "data_inventory", "validator_execution_audit.csv"), index=False)
    
    # Save missing
    missing = df_audit[df_audit["Status"] == "SKIPPED"]
    with open(os.path.join(val_out_dir, "data_inventory", "missing_validation_products.md"), "w") as f:
        f.write("# Missing Validation Products\n\n")
        for _, row in missing.iterrows():
            f.write(f"- **{row['Module']} / {row['Dataset']}**: {row['Skip reason']}\n")
            
    # Generate index of final products
    import glob
    final_files = glob.glob(os.path.join(val_out_dir, "**/*.*"), recursive=True)
    products = []
    for ff in final_files:
        if 'data_inventory' in ff: continue
        if not ff.endswith(".png") and not ff.endswith(".json") and not ff.endswith(".csv"): continue
        rel_path = os.path.relpath(ff, val_out_dir)
        products.append({
            "Path": rel_path,
            "Type": os.path.splitext(ff)[1]
        })
    pd.DataFrame(products).to_csv(os.path.join(val_out_dir, "data_inventory", "generated_independent_validation_products.csv"), index=False)

    logger.info("Validation indépendante terminée")
