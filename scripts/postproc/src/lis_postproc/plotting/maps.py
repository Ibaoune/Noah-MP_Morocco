"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.plotting.maps
Description: Generic plotting utilities and visualization functions.
================================================================================
"""
"""plotting/maps.py — Generic mapping functions."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import logging

logger = logging.getLogger(__name__)

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False
    logger.warning("cartopy not available — map plots will be skipped")


def add_map_features(ax, map_cfg=None, gl_cfg=None):
    """
    Adds coastlines, borders and grid to a Cartopy axis.
    Compatible with the function of the same name in assimilation_diagnostics/utils.py.
    """
    if not HAS_CARTOPY:
        return None
    map_cfg = map_cfg or {}
    gl_cfg = gl_cfg or {}

    ax.coastlines(
        linewidth=map_cfg.get('coastline_linewidth', 0.6),
        color=map_cfg.get('coastline_color', '0.2')
    )
    ax.add_feature(
        cfeature.BORDERS,
        linewidth=map_cfg.get('border_linewidth', 0.35),
        linestyle=':',
        color=map_cfg.get('border_color', '0.35')
    )
    ax.set_facecolor(map_cfg.get('background_color', '0.92'))

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(), draw_labels=True,
        linewidth=gl_cfg.get('linewidth', 0.20),
        color=gl_cfg.get('color', '0.55'),
        alpha=gl_cfg.get('alpha', 0.25),
        linestyle=gl_cfg.get('linestyle', '--')
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': gl_cfg.get('label_fontsize', 9)}
    gl.ylabel_style = {'size': gl_cfg.get('label_fontsize', 9)}
    return gl


def plot_spatial_map(
    data, lat, lon,
    title="", subtitle="",
    cmap="viridis", vmin=None, vmax=None,
    colorbar_label="", bounds=None,
    figsize=(9, 7), dpi=300,
    map_cfg=None, gl_cfg=None,
    out_path=None,
):
    """
    Generates a generic spatial map with Cartopy.
    Compatible with the conventions of assimilation_diagnostics.
    """
    if not HAS_CARTOPY:
        logger.warning("Cannot plot map: cartopy not available")
        return None

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    add_map_features(ax, map_cfg=map_cfg, gl_cfg=gl_cfg)

    if bounds is not None:
        cmap_obj = plt.get_cmap(cmap, len(bounds) - 1).copy()
        norm = mcolors.BoundaryNorm(bounds, ncolors=cmap_obj.N, clip=True)
    else:
        cmap_obj = plt.get_cmap(cmap).copy()
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    cmap_obj.set_bad(color='lightgrey')
    pcm = ax.pcolormesh(lon, lat, data, cmap=cmap_obj, norm=norm,
                         transform=ccrs.PlateCarree())

    fig.suptitle(title, fontsize=13, fontweight='bold', y=0.965)
    ax.set_title(subtitle, fontsize=10, pad=8)

    fig.canvas.draw()
    pos = ax.get_position()
    cax = fig.add_axes([pos.x1 + 0.012, pos.y0, 0.018, pos.height])
    cbar = fig.colorbar(pcm, cax=cax, orientation='vertical', extend='both')
    cbar.set_label(colorbar_label, fontsize=11)
    cbar.ax.tick_params(labelsize=9)

    if out_path:
        fig.savefig(out_path, dpi=dpi, bbox_inches='tight')
        logger.info(f"Saved map: {out_path}")
    plt.close(fig)
    return out_path


def plot_difference_map(
    data_diff, lat, lon,
    exp_label_a="", exp_label_b="",
    title="", subtitle="",
    cmap="RdBu", bounds=None,
    colorbar_label="",
    figsize=(9, 7), dpi=300,
    map_cfg=None, gl_cfg=None,
    out_path=None,
):
    """Generates a difference map (B - A) with a divergent colormap centered on 0."""
    return plot_spatial_map(
        data=data_diff, lat=lat, lon=lon,
        title=title, subtitle=subtitle,
        cmap=cmap, bounds=bounds,
        colorbar_label=colorbar_label,
        figsize=figsize, dpi=dpi,
        map_cfg=map_cfg, gl_cfg=gl_cfg,
        out_path=out_path,
    )
