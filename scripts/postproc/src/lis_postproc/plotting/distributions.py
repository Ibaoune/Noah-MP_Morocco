"""plotting/distributions.py — Histogrammes et boxplots génériques."""
import numpy as np
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)


def plot_histogram(
    data, bins=80,
    color="#8EC7DA", edgecolor="0.25", alpha=0.90,
    xlabel="", ylabel="Frequency (%)",
    title="", subtitle="",
    show_mean=True, show_median=True,
    use_percentage=True,
    figsize=(8, 6), dpi=300,
    out_path=None,
):
    """Histogramme générique avec lignes de référence."""
    fig, ax = plt.subplots(figsize=figsize)

    valid = data[np.isfinite(data)]
    if len(valid) == 0:
        logger.warning("No valid data for histogram")
        plt.close(fig)
        return None

    if use_percentage and len(valid) > 0:
        weights = np.ones_like(valid) * 100.0 / len(valid)
        ax.hist(valid, bins=bins, weights=weights,
                color=color, edgecolor=edgecolor, alpha=alpha)
    else:
        ax.hist(valid, bins=bins, color=color, edgecolor=edgecolor, alpha=alpha)

    if show_mean:
        ax.axvline(np.mean(valid), color='#B2182B', linestyle='--',
                   linewidth=1.2, label=f"Mean = {np.mean(valid):.3f}")
    if show_median:
        ax.axvline(np.median(valid), color='#2166AC', linestyle=':',
                   linewidth=1.4, label=f"Median = {np.median(valid):.3f}")

    ax.axvline(0, color='0.15', linestyle='-', linewidth=1.0, label='Zero')
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=8, frameon=False)

    if title:
        fig.suptitle(title, fontsize=13, fontweight='bold', y=0.965)
    if subtitle:
        ax.set_title(subtitle, fontsize=10, pad=8)

    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return out_path
