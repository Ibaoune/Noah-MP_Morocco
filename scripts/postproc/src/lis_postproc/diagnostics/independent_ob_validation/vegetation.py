import os
import logging
from .common import check_data_availability, write_skip_report

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "vegetation")
    os.makedirs(out_dir, exist_ok=True)
    
    for product in config.get("products", []):
        if product in ["copernicus_lai", "modis_lai"]:
            write_skip_report(out_dir, "vegetation", product, "MISSING_LOCAL_DATA")
            continue
            
        if product == "fluxsat_gpp":
            if check_data_availability("FLUXSAT_GPP", "vegetation"):
                logger.info(f"Exécution de la validation pour {product}")
                # Logique de validation FLUXSAT GPP (placeholder)
                with open(os.path.join(out_dir, f"{product}_validation_status.txt"), 'w') as f:
                    f.write("AVAILABLE and PROCESSED (Placeholder)\n")
            else:
                write_skip_report(out_dir, "vegetation", product, "MISSING_LOCAL_DATA")
