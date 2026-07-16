# Author: M. El Aabaribaoune (@um6p)
import os
import logging
from .common import write_skip_report

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "lsm_benchmark")
    os.makedirs(out_dir, exist_ok=True)
    
    for product in config.get("products", []):
        write_skip_report(out_dir, "lsm_benchmark", product, "MISSING_LOCAL_DATA")
