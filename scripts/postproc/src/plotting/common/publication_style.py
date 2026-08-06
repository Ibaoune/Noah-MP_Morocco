# Author: M. EL Aabaribaoune (@um6p)

"""
Centralized publication style for all figures.
"""
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def apply_publication_style():
    """
    Applies the Q1 journal publication style to matplotlib.
    """
    logger.info("Applying publication style")
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 14,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        'image.cmap': 'viridis',
        'savefig.dpi': 300,
        'savefig.bbox': 'tight'
    })
