"""io/hymap.py — Stub pour la lecture des fichiers HyMAP."""
import logging
logger = logging.getLogger(__name__)


def get_hymap_files(hymap_dir, start_date, end_date):
    """Récupère les fichiers de sortie HyMAP pour une période donnée."""
    # TODO: Implémenter la lecture des fichiers HyMAP NetCDF
    # (à migrer depuis hymap_validation/ quand la logique est disponible)
    logger.warning("get_hymap_files: not yet implemented")
    return []


def load_hymap_streamflow(files, station_lon=None, station_lat=None):
    """Charge le débit fluvial HyMAP pour une station ou un domaine."""
    logger.warning("load_hymap_streamflow: not yet implemented")
    return None
