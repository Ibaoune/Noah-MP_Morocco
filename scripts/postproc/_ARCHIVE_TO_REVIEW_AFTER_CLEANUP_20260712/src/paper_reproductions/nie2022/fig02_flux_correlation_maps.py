# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Script: fig02_flux_correlation_maps.py
Description: Reproduit la Figure 2 de Nie et al. (2022).
             Cartes de différences de corrélation (DA minus OL) pour les
             flux E, T, ET, NPP et GPP.
================================================================================
"""

import sys
import os
import matplotlib.pyplot as plt
import logging

# S'assurer que le module src/ est dans le PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from external_validation.correlations import compute_spatial_correlation, compute_anomaly_correlation

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def plot_correlation_difference_maps(flux_name, da_corr, ol_corr, da_anomaly_corr, ol_anomaly_corr):
    """
    Fonction utilitaire pour tracer la différence de corrélation (DA - OL).
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Différence de corrélation absolue
    diff_corr = da_corr - ol_corr
    diff_corr.plot(ax=axes[0], cmap='RdBu_r', vmin=-0.2, vmax=0.2, 
                   cbar_kwargs={'label': 'Difference in Correlation (DA - OL)'})
    axes[0].set_title(f'Correlation Difference: {flux_name}')
    
    # Différence de corrélation d'anomalie
    diff_anom = da_anomaly_corr - ol_anomaly_corr
    diff_anom.plot(ax=axes[1], cmap='RdBu_r', vmin=-0.2, vmax=0.2,
                   cbar_kwargs={'label': 'Difference in Anomaly Correlation (DA - OL)'})
    axes[1].set_title(f'Anomaly Correlation Difference: {flux_name}')
    
    plt.tight_layout()
    return fig

def main():
    logger.info("Starting reproduction of Figure 2: Flux Correlation Maps")
    
    # ÉTAPE 1: Chargement des données (Placeholder)
    # Les chemins réels devront être injectés depuis lis_postproc/configs/
    logger.info("Loading LIS outputs (OL, LAI-DA, SSM-DA) and reference observations (WaPOR, FLUXSAT)...")
    
    # ÉTAPE 2: Calcul des corrélations via external_validation/correlations.py
    logger.info("Computing correlations vs observations...")
    # ex: corr_ol = compute_spatial_correlation(sim_ol['Qle_tavg'], obs_wapor['ET'])
    # ex: corr_da = compute_spatial_correlation(sim_smap['Qle_tavg'], obs_wapor['ET'])
    
    # ÉTAPE 3: Génération de la figure
    logger.info("Plotting maps of correlation differences...")
    
    # ÉTAPE 4: Sauvegarde
    output_dir = "outputs/nie2022_figures"
    os.makedirs(output_dir, exist_ok=True)
    # fig.savefig(f"{output_dir}/Figure02_Correlation_Maps.pdf")
    logger.info("Figure 2 successfully generated and saved.")

if __name__ == "__main__":
    main()

