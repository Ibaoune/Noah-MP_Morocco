import os
import logging
from .common import write_skip_report

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "streamflow_and_runoff")
    os.makedirs(out_dir, exist_ok=True)
    
    for product in config.get("products", []):
        logger.warning("Streamflow routing not available. Skipping validation.")
        write_skip_report(out_dir, "streamflow_and_runoff", product, "SKIPPED_MISSING_ROUTED_STREAMFLOW")
