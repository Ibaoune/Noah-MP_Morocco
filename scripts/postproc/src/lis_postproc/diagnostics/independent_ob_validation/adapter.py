import os
import yaml
import logging

from . import soil_moisture
from . import evapotranspiration
from . import vegetation
from . import water_storage
from . import streamflow
from . import lsm_benchmark
from . import synthesis

logger = logging.getLogger(__name__)

def run(recipe_config, global_config):
    """
    Point d'entrée pour la validation indépendante.
    Lit la recette, construit les tâches de validation et appelle les validateurs.
    """
    if "independent_ob_validation" not in recipe_config.get("diagnostics", {}):
        return

    val_config = recipe_config["diagnostics"]["independent_ob_validation"]
    if not val_config.get("enabled", False):
        return

    logger.info("Démarrage de la validation indépendante multi-source")
    
    # Récupérer les expériences (héritées de la recette principale)
    reference = recipe_config["experiments"][0] if isinstance(recipe_config.get("experiments"), list) else recipe_config.get("baseline", None)
    experiments = recipe_config.get("experiments", [])
    
    # Création du répertoire de sortie
    outputs = recipe_config.get("outputs")
    if hasattr(outputs, "figure_dir"):
        out_dir = outputs.figure_dir
    elif isinstance(outputs, dict):
        out_dir = outputs.get("figure_dir", "outputs/matrix_2016/figures/smap_cdf_sensitivity")
    else:
        out_dir = "outputs/matrix_2016/figures/smap_cdf_sensitivity"
        
    val_out_dir = os.path.join(out_dir, "independent_ob_validation")
    os.makedirs(val_out_dir, exist_ok=True)

    # Lancement des validateurs si activés
    if val_config.get("soil_moisture", {}).get("enabled", False):
        soil_moisture.run_validation(val_config["soil_moisture"], experiments, val_out_dir)
        
    if val_config.get("evapotranspiration", {}).get("enabled", False):
        evapotranspiration.run_validation(val_config["evapotranspiration"], experiments, val_out_dir)
        
    if val_config.get("streamflow_and_runoff", {}).get("enabled", False):
        streamflow.run_validation(val_config["streamflow_and_runoff"], experiments, val_out_dir)
        
    if val_config.get("vegetation", {}).get("enabled", False):
        vegetation.run_validation(val_config["vegetation"], experiments, val_out_dir)
        
    if val_config.get("water_storage", {}).get("enabled", False):
        water_storage.run_validation(val_config["water_storage"], experiments, val_out_dir)
        
    if val_config.get("lsm_benchmark", {}).get("enabled", False):
        lsm_benchmark.run_validation(val_config["lsm_benchmark"], experiments, val_out_dir)

    if val_config.get("validation_synthesis", {}).get("enabled", False):
        synthesis.run_synthesis(val_config["validation_synthesis"], val_out_dir)

    logger.info("Validation indépendante terminée")
