import os
import logging
from .dataset_registry import DatasetRegistry

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "streamflow")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    config_dir = os.path.join(project_root, "scripts/postproc/configs/observations")
    registry = DatasetRegistry(config_dir)
    ready_datasets = registry.get_ready_datasets()
    
    sf_datasets = {k: v for k, v in ready_datasets.items() if v["validation_category"] == "streamflow"}
    
    if not sf_datasets:
        logger.warning("No READY Streamflow datasets found.")
        # Mark as skipped missing local data
        with open(os.path.join(out_dir, "SKIPPED_MISSING_LOCAL.txt"), "w") as f:
            f.write("No streamflow data ready.\n")
        return
        
    for name, cfg in sf_datasets.items():
        logger.info(f"Streamflow module loaded for {cfg['display_name']} but logic is skipped because data is incomplete.")
