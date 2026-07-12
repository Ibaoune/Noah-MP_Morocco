import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def check_data_availability(product_name, category):
    """
    Vérifie si les données brutes sont disponibles pour un produit.
    """
    # Chemin relatif depuis src/lis_postproc/diagnostics/independent_validation/common.py jusqu'à la racine du projet
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
    base_path = project_root / "data" / "validation" / category / product_name
    
    if not base_path.exists():
        return False
    # Vérifie s'il y a des fichiers .nc
    has_nc = any(base_path.rglob("*.nc"))
    return has_nc

def write_skip_report(out_dir, category, product, reason):
    """
    Génère un rapport indiquant qu'un produit a été ignoré.
    """
    os.makedirs(out_dir, exist_ok=True)
    report_file = os.path.join(out_dir, f"SKIPPED_{product}.txt")
    with open(report_file, 'w') as f:
        f.write(f"Validation for {product} in {category} was skipped.\n")
        f.write(f"Reason: {reason}\n")
    logger.warning(f"SKIPPED {product}: {reason}")
