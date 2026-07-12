import os
import logging

logger = logging.getLogger(__name__)

def run_synthesis(config, base_out_dir):
    out_dir = os.path.join(base_out_dir, "validation_synthesis")
    os.makedirs(out_dir, exist_ok=True)
    
    logger.info("Génération de la synthèse de validation")
    with open(os.path.join(out_dir, "scientific_summary.md"), 'w') as f:
        f.write("# Validation Synthesis\n")
        f.write("Synthesis computation relies on individual module outputs.\n")
