import os
import logging
from .common import check_data_availability, write_skip_report

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "evapotranspiration")
    os.makedirs(out_dir, exist_ok=True)
    
    for product in config.get("products", []):
        if product in ["mod16_evapotranspiration", "wapor_evapotranspiration"]:
            write_skip_report(out_dir, "evapotranspiration", product, "MISSING_LOCAL_DATA")
            continue
            
        if product == "gleam_evapotranspiration":
            if check_data_availability("GLEAM", "evapotranspiration"):
                logger.info(f"Exécution de la validation pour {product}")
                # Logique de validation GLEAM (placeholder)
                with open(os.path.join(out_dir, f"{product}_validation_status.txt"), 'w') as f:
                    f.write("AVAILABLE and PROCESSED (Placeholder)\n")
            else:
                write_skip_report(out_dir, "evapotranspiration", product, "MISSING_LOCAL_DATA")
