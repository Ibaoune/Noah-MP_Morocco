"""
diagnostics/domain/adapter.py
=============================
Adaptateur pour le module src/domain/
Permet d'intégrer la génération des cartes du domaine dans le pipeline lis_postproc.
"""
import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_THIS_DIR = Path(__file__).parent
_POSTPROC_SRC = _THIS_DIR.parent.parent.parent
DOMAIN_DIR = _POSTPROC_SRC / "domain"

def _add_src_to_path():
    src_path = str(_POSTPROC_SRC)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

def run_domain_diagnostics(recipe, global_cfg, out_dir, dry_run=False):
    """
    Exécute le script principal du module domain.
    """
    generated_files = []
    
    if dry_run:
        print(f"\n  [DRY-RUN] Domain diagnostics:")
        print(f"    Output dir: {out_dir}")
        return generated_files

    _add_src_to_path()
    import sys
    logger.error(f"DEBUG: sys.modules['utils'] = {sys.modules.get('utils')}")
    try:
        from domain.main import run_domain
    except ImportError as e:
        logger.error(f"Cannot import domain module: {e}")
        return generated_files

    # Config attendue par le module domain
    data_dict = {
        'project_root': getattr(global_cfg, 'project_root', "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco")
    }
    
    logger.info(f"Running domain diagnostics → {out_dir}")
    try:
        files = run_domain(data_dict, out_dir)
        if files:
            generated_files.extend(files)
    except Exception as e:
        logger.error(f"Error in run_domain: {e}")

    return list(set(generated_files))
