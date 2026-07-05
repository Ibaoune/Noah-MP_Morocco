"""plotting/timeseries.py — Fonctions génériques de séries temporelles."""
import numpy as np
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)


def plot_multi_experiment_timeseries(
    dates, data_dict, variable,
    experiment_catalog=None,
    title="", ylabel="",
    figsize=(12, 4), dpi=300,
    out_path=None,
):
    """
    Trace les séries temporelles de plusieurs expériences sur le même graphique.

    Paramètres
    ----------
    dates          : liste de datetime
    data_dict      : {exp_id: np.array 1D}
    variable       : objet Variable (pour les unités et labels)
    experiment_catalog: dict brut des expériences (pour les styles)
    """
    from .styles import get_experiment_style

    fig, ax = plt.subplots(figsize=figsize)

    for exp_id, data in data_dict.items():
        style = get_experiment_style(exp_id, experiment_catalog)
        ax.plot(dates, data,
                color=style['color'],
                linestyle=style['linestyle'],
                label=style['label'],
                linewidth=1.2)

    unit = getattr(variable, 'unit', '') if variable else ''
    cb_label = getattr(variable, 'colorbar_label', ylabel) if variable else ylabel
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel(cb_label or f"Value ({unit})", fontsize=11)
    ax.legend(fontsize=9, frameon=False)
    ax.tick_params(labelsize=9)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=6)

    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=dpi, bbox_inches='tight')
        logger.info(f"Saved timeseries: {out_path}")
    plt.close(fig)
    return out_path
