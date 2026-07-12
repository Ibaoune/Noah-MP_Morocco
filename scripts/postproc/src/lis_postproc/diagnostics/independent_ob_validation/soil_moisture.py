import os
import logging
from .common import check_data_availability, write_skip_report

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "soil_moisture")
    os.makedirs(out_dir, exist_ok=True)
    
    for product in config.get("products", []):
        if product == "ascat_soil_moisture" or product == "in_situ_soil_moisture":
            write_skip_report(out_dir, "soil_moisture", product, "MISSING_LOCAL_DATA")
            continue
            
        if product == "esa_cci_soil_moisture":
            if check_data_availability("ESA_CCI", "soil_moisture"):
                logger.info(f"Exécution de la validation pour {product}")
                # Logique de validation ESA CCI (placeholder)
                with open(os.path.join(out_dir, f"{product}_validation_status.txt"), 'w') as f:
                    f.write("AVAILABLE and PROCESSED (Placeholder)\n")
            else:
                write_skip_report(out_dir, "soil_moisture", product, "MISSING_LOCAL_DATA")
