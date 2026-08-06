# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: lis_postproc.plotting.styles
Description: Generic plotting utilities and visualization functions.
================================================================================
"""
"""
plotting/styles.py — Styles globaux et palettes de couleurs
=============================================================
Fonctions utilitaires pour initialiser les styles matplotlib
cohérents avec le guide de style de la publication Q1.
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


# ============================================================
# Palette de couleurs par expérience
# ============================================================
EXPERIMENT_COLORS = {
    'OPL_noirr_2016':           '#2166AC',
    'DA_smap_nocdf_noirr_2016': '#D6604D',
    'DA_smap_cdf_noirr_2016':   '#B2182B',
    'DA_lai_noirr_2016':        '#4DAC26',
    'DA_joint_smap_lai_noirr_2016': '#762A83',
}

EXPERIMENT_LINESTYLES = {
    'OPL_noirr_2016':           '-',
    'DA_smap_nocdf_noirr_2016': '--',
    'DA_smap_cdf_noirr_2016':   '-.',
    'DA_lai_noirr_2016':        ':',
    'DA_joint_smap_lai_noirr_2016': '-',
}


def setup_matplotlib_style(dpi: int = 300):
    """Configure matplotlib pour des figures de qualité publication."""
    plt.rcParams.update({
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 13,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': False,
    })


def get_experiment_style(exp_id: str, exp_catalog: dict = None) -> dict:
    """Retourne le style visuel (color, linestyle, marker) pour une expérience."""
    if exp_catalog and exp_id in exp_catalog:
        exp = exp_catalog[exp_id]
        return {
            'color': exp.get('color', '#2166AC'),
            'linestyle': exp.get('linestyle', '-'),
            'marker': exp.get('marker', 'o'),
            'label': exp.get('label', exp_id),
        }
    return {
        'color': EXPERIMENT_COLORS.get(exp_id, '#666666'),
        'linestyle': EXPERIMENT_LINESTYLES.get(exp_id, '-'),
        'marker': 'o',
        'label': exp_id,
    }


def get_robust_colorlimits(data, percentiles=(2, 98)):
    """Calcule des limites de colorbar robustes."""
    valid = data[np.isfinite(data)]
    if len(valid) == 0:
        return 0.0, 1.0
    return float(np.percentile(valid, percentiles[0])), \
           float(np.percentile(valid, percentiles[1]))


def get_symmetric_colorlimits(data, percentiles=(2, 98)):
    """Calcule des limites symétriques (pour les cartes de différences)."""
    vmin, vmax = get_robust_colorlimits(data, percentiles)
    abs_max = max(abs(vmin), abs(vmax))
    return -abs_max, abs_max
