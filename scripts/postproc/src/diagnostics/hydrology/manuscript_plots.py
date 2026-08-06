# Author: M. EL Aabaribaoune (@um6p)

"""
manuscript_plots.py
-------------------
Publication-quality hydrological diagnostic figures for the SMAP
assimilation manuscript. Reads pre-computed seasonal climatologies from
the NetCDF cache produced by seasonal_impact_maps.py.

Figures produced (PNG + PDF):
  1. fig_sm_seasonal_{ref}_vs_{da}_{yr}.png  — Surface Soil Moisture
  2. fig_runoff_seasonal_{ref}_vs_{da}_{yr}.png — Total Runoff (2×3)
  3. fig_precip_runoff_{ref}_vs_{da}_{yr}.png  — Precip + Δ Components (2×4)

Runs for DA_NoCDF and DA_CDF automatically.
"""

import copy, logging, os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ── Domain ────────────────────────────────────────────────────────────────────
BBOX = [-13.5, -1.0, 27.5, 36.0]   # [lon_min, lat_min, lon_max, lat_max]
PERIOD = "2016–2020"
PRECIP_SOURCE = "MERRA-2"           # actual forcing used in LIS run

# ── Discrete colour scales ────────────────────────────────────────────────────
# Absolute soil moisture (m³ m⁻³)
SM_BOUNDS   = [0.05, 0.08, 0.11, 0.14, 0.17, 0.20, 0.23, 0.26, 0.30]
SM_CMAP     = "YlGnBu"

# Absolute total runoff (mm day⁻¹)
Q_BOUNDS    = [0.0, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50]
Q_CMAP      = "Blues"

# Precipitation (mm day⁻¹)
P_BOUNDS    = [0.0, 0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 2.50, 3.00]
P_CMAP      = "Blues"

# Difference (diverging, centred at 0)
DIFF_SM_BOUNDS  = [-0.10, -0.07, -0.05, -0.03, -0.01, 0.01, 0.03, 0.05, 0.07, 0.10]
DIFF_Q_BOUNDS   = [-0.50, -0.30, -0.15, -0.05, -0.01, 0.01, 0.05, 0.15, 0.30, 0.50]
DIFF_CMAP       = "RdBu_r"

# ── Fonts ─────────────────────────────────────────────────────────────────────
TITLE_FS   = 9
GTITLE_FS  = 11
CBAR_FS    = 9
ANNOT_FS   = 7
DPI        = 300

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_discrete(bounds, cmap_name, under='#f5f5f5'):
    """Return (cmap, norm) for a BoundaryNorm discrete colour scale."""
    cmap = copy.copy(plt.get_cmap(cmap_name))
    cmap.set_bad(color='white')
    cmap.set_under(under)
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')
    return cmap, norm


def _make_discrete_div(bounds, cmap_name):
    """Return (cmap, norm) for a symmetric BoundaryNorm diverging scale."""
    cmap = copy.copy(plt.get_cmap(cmap_name))
    cmap.set_bad(color='white')
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')
    return cmap, norm


def _load(nc_dir, var, exp, season, yr0, yr1):
    """Load a 2-D climatology from the cache."""
    p = nc_dir / f"{var}_{exp}_{season}_{yr0}_{yr1}.nc"
    if not p.exists():
        return None, None, None
    with xr.open_dataset(p) as ds:
        data = ds[var].values.squeeze()
        lon  = ds.lon.values
        lat  = ds.lat.values
    return data, lon, lat


def _map_ax(fig, row, col, nrows, ncols, facecolor='white'):
    """Create a Cartopy axes and apply common map styling."""
    ax = fig.add_subplot(nrows, ncols, row * ncols + col + 1,
                         projection=ccrs.PlateCarree())
    ax.set_facecolor(facecolor)
    ax.set_extent(BBOX, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, facecolor='white', zorder=0)
    ax.add_feature(cfeature.LAND,  facecolor='#f5f5f5', zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#333333', zorder=2)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.4, linestyle=':', edgecolor='#666666', zorder=2)
    return ax


def _annot(ax, data, extra_lines=None):
    """Add compact min / mean / max annotation (bottom-left corner)."""
    v = data[~np.isnan(data)]
    if v.size == 0:
        return
    lines = [f"min={v.min():.3f}  mean={v.mean():.3f}  max={v.max():.3f}"]
    if extra_lines:
        lines += extra_lines
    ax.text(0.01, 0.02, '\n'.join(lines), transform=ax.transAxes,
            fontsize=ANNOT_FS, va='bottom', ha='left',
            bbox=dict(facecolor='white', alpha=0.75, edgecolor='none',
                      boxstyle='round,pad=0.15'))


def _shared_cbar(fig, im, ax_list, label, ticks=None, pad=0.07, fraction=0.035):
    cb = fig.colorbar(im, ax=ax_list, orientation='horizontal',
                      fraction=fraction, pad=pad, extend='both')
    if ticks is not None:
        cb.set_ticks(ticks)
    cb.set_label(label, fontsize=CBAR_FS, labelpad=3)
    cb.ax.tick_params(labelsize=ANNOT_FS)
    return cb


def _save(fig, path_stem, dpi=DPI):
    for ext in ('png', 'pdf'):
        fig.savefig(f"{path_stem}.{ext}", dpi=dpi, bbox_inches='tight',
                    facecolor='white')
    log.info(f"Saved {path_stem}.png / .pdf")
    plt.close(fig)


def _da_label(da_exp):
    return da_exp.replace('_', '-')


# ── Figure A: Surface Soil Moisture ──────────────────────────────────────────

def plot_sm(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1):
    da_label = _da_label(da_exp)
    log.info(f"[SM] {ref_exp} vs {da_label}")
    cm_abs,  nm_abs  = _make_discrete(SM_BOUNDS, SM_CMAP)
    cm_diff, nm_diff = _make_discrete_div(DIFF_SM_BOUNDS, DIFF_CMAP)

    fig = plt.figure(figsize=(13, 8))
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f"Seasonal Climatology of Surface Soil Moisture and Assimilation-Induced Anomalies\n"
        f"{da_label} vs OL — DJF / JJA  |  {PERIOD}",
        fontsize=GTITLE_FS, fontweight='bold', y=1.01)

    seasons = ['DJF', 'JJA']
    ax_abs, ax_diff = [], []
    im_abs = im_diff = None

    for row, season in enumerate(seasons):
        ol, lon, lat = _load(nc_dir, 'surface_soil_moisture', ref_exp,  season, yr0, yr1)
        da, _,   _   = _load(nc_dir, 'surface_soil_moisture', da_exp,   season, yr0, yr1)
        if ol is None or da is None:
            continue
        diff = da - ol

        # (a/d) OL
        ax = _map_ax(fig, row, 0, 2, 3)
        im = ax.pcolormesh(lon, lat, ol, transform=ccrs.PlateCarree(),
                           cmap=cm_abs, norm=nm_abs, shading='auto', zorder=1)
        ax.set_title(f"({'abcdef'[row*3]}) OL surface soil moisture — {season}",
                     fontsize=TITLE_FS, fontweight='bold')
        _annot(ax, ol)
        im_abs = im; ax_abs.append(ax)

        # (b/e) DA
        ax2 = _map_ax(fig, row, 1, 2, 3)
        ax2.pcolormesh(lon, lat, da, transform=ccrs.PlateCarree(),
                       cmap=cm_abs, norm=nm_abs, shading='auto', zorder=1)
        ax2.set_title(f"({'abcdef'[row*3+1]}) {da_label} surface soil moisture — {season}",
                      fontsize=TITLE_FS, fontweight='bold')
        _annot(ax2, da)
        ax_abs.append(ax2)

        # (c/f) Diff
        ax3 = _map_ax(fig, row, 2, 2, 3)
        im3 = ax3.pcolormesh(lon, lat, diff, transform=ccrs.PlateCarree(),
                             cmap=cm_diff, norm=nm_diff, shading='auto', zorder=1)
        ax3.set_title(f"({'abcdef'[row*3+2]}) Δ surface soil moisture ({da_label} − OL) — {season}",
                      fontsize=TITLE_FS, fontweight='bold')
        vd = diff[~np.isnan(diff)]
        extra = []
        if vd.size:
            extra = [f"Median={np.median(vd):.3f}  Dry={100*np.mean(vd<0):.0f}%  Wet={100*np.mean(vd>0):.0f}%"]
        _annot(ax3, diff, extra)
        im_diff = im3; ax_diff.append(ax3)

    if im_abs:
        _shared_cbar(fig, im_abs, ax_abs,
                     "Surface soil moisture (m³ m⁻³)",
                     ticks=SM_BOUNDS[::2])
    if im_diff:
        _shared_cbar(fig, im_diff, ax_diff,
                     f"Δ surface soil moisture ({da_label} − OL)  (m³ m⁻³)",
                     ticks=DIFF_SM_BOUNDS[::2])

    _save(fig, out_dir / f"fig_sm_seasonal_{ref_exp}_vs_{da_exp}_{yr0}_{yr1}")


# ── Figure B: Total Runoff ────────────────────────────────────────────────────

def plot_runoff(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1):
    da_label = _da_label(da_exp)
    log.info(f"[Runoff] {ref_exp} vs {da_label}")
    cm_abs,  nm_abs  = _make_discrete(Q_BOUNDS, Q_CMAP)
    cm_diff, nm_diff = _make_discrete_div(DIFF_Q_BOUNDS, DIFF_CMAP)

    fig = plt.figure(figsize=(13, 8))
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f"Seasonal Mean Total Runoff and Data-Assimilation-Induced Anomalies\n"
        f"{da_label} vs OL — DJF / JJA  |  {PERIOD}",
        fontsize=GTITLE_FS, fontweight='bold', y=1.01)

    seasons = ['DJF', 'JJA']
    ax_abs, ax_diff = [], []
    im_abs = im_diff = None

    for row, season in enumerate(seasons):
        ol, lon, lat = _load(nc_dir, 'total_runoff', ref_exp, season, yr0, yr1)
        da, _,   _   = _load(nc_dir, 'total_runoff', da_exp,  season, yr0, yr1)
        if ol is None or da is None:
            continue
        diff = da - ol

        ax1 = _map_ax(fig, row, 0, 2, 3)
        im  = ax1.pcolormesh(lon, lat, ol, transform=ccrs.PlateCarree(),
                             cmap=cm_abs, norm=nm_abs, shading='auto', zorder=1)
        ax1.set_title(f"({'abcdef'[row*3]}) OL — {season}",
                      fontsize=TITLE_FS, fontweight='bold')
        _annot(ax1, ol)
        im_abs = im; ax_abs.append(ax1)

        ax2 = _map_ax(fig, row, 1, 2, 3)
        ax2.pcolormesh(lon, lat, da, transform=ccrs.PlateCarree(),
                       cmap=cm_abs, norm=nm_abs, shading='auto', zorder=1)
        ax2.set_title(f"({'abcdef'[row*3+1]}) {da_label} — {season}",
                      fontsize=TITLE_FS, fontweight='bold')
        _annot(ax2, da)
        ax_abs.append(ax2)

        ax3 = _map_ax(fig, row, 2, 2, 3)
        im3 = ax3.pcolormesh(lon, lat, diff, transform=ccrs.PlateCarree(),
                             cmap=cm_diff, norm=nm_diff, shading='auto', zorder=1)
        ax3.set_title(f"({'abcdef'[row*3+2]}) {da_label} − OL — {season}",
                      fontsize=TITLE_FS, fontweight='bold')
        _annot(ax3, diff)
        im_diff = im3; ax_diff.append(ax3)

    if im_abs:
        _shared_cbar(fig, im_abs, ax_abs,
                     "Total runoff (mm day⁻¹)", ticks=Q_BOUNDS)
    if im_diff:
        _shared_cbar(fig, im_diff, ax_diff,
                     f"Δ runoff ({da_label} − OL)  (mm day⁻¹)",
                     ticks=DIFF_Q_BOUNDS[::2])

    _save(fig, out_dir / f"fig_runoff_seasonal_{ref_exp}_vs_{da_exp}_{yr0}_{yr1}")


# ── Figure C: Precipitation + Runoff Components ───────────────────────────────

def plot_precip_runoff(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1):
    da_label = _da_label(da_exp)
    log.info(f"[Precip/Runoff] {ref_exp} vs {da_label}")
    cm_p,    nm_p    = _make_discrete(P_BOUNDS,  P_CMAP)
    cm_diff, nm_diff = _make_discrete_div(DIFF_Q_BOUNDS, DIFF_CMAP)

    seasons = ['DJF', 'JJA']
    comp_vars   = ['total_runoff', 'surface_runoff', 'baseflow']
    comp_labels = ['Δ Total runoff', 'Δ Surface runoff', 'Δ Baseflow']

    fig = plt.figure(figsize=(18, 8))
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f"Seasonal Mean Precipitation Forcing and Assimilation-Induced Changes in Runoff Partitioning\n"
        f"{da_label} vs OL — DJF / JJA  |  {PERIOD}",
        fontsize=GTITLE_FS, fontweight='bold', y=1.01)

    ax_p, ax_d = [], []
    im_p = im_d = None
    letters = list('abcdefgh')
    idx = 0

    for row, season in enumerate(seasons):
        # Precipitation
        pr, lon, lat = _load(nc_dir, 'precipitation', ref_exp, season, yr0, yr1)
        if pr is not None:
            ax = _map_ax(fig, row, 0, 2, 4)
            im = ax.pcolormesh(lon, lat, pr, transform=ccrs.PlateCarree(),
                               cmap=cm_p, norm=nm_p, shading='auto', zorder=1)
            ax.set_title(f"({letters[idx]}) Mean precipitation forcing ({PRECIP_SOURCE}) — {season}",
                         fontsize=TITLE_FS, fontweight='bold')
            _annot(ax, pr)
            im_p = im; ax_p.append(ax)
        idx += 1

        # Runoff components
        for ci, (cv, cl) in enumerate(zip(comp_vars, comp_labels)):
            ol, _, _ = _load(nc_dir, cv, ref_exp, season, yr0, yr1)
            da, _, _ = _load(nc_dir, cv, da_exp,  season, yr0, yr1)
            if ol is None or da is None:
                idx += 1; continue
            diff = da - ol
            ax = _map_ax(fig, row, ci + 1, 2, 4)
            im = ax.pcolormesh(lon, lat, diff, transform=ccrs.PlateCarree(),
                               cmap=cm_diff, norm=nm_diff, shading='auto', zorder=1)
            ax.set_title(f"({letters[idx]}) {cl} ({da_label} − OL) — {season}",
                         fontsize=TITLE_FS, fontweight='bold')
            _annot(ax, diff)
            im_d = im; ax_d.append(ax)
            idx += 1

    if im_p:
        _shared_cbar(fig, im_p, ax_p,
                     f"Precipitation (mm day⁻¹)  [{PRECIP_SOURCE}]",
                     ticks=P_BOUNDS, pad=0.09, fraction=0.04)
    if im_d:
        _shared_cbar(fig, im_d, ax_d,
                     f"Δ runoff ({da_label} − OL)  (mm day⁻¹)",
                     ticks=DIFF_Q_BOUNDS[::2], pad=0.09, fraction=0.025)

    _save(fig, out_dir / f"fig_precip_runoff_{ref_exp}_vs_{da_exp}_{yr0}_{yr1}")


# ── QC Summary ────────────────────────────────────────────────────────────────

def print_qc(nc_dir, ref_exp, da_exps, yr0, yr1):
    log.info("\n" + "="*60)
    log.info("QC SUMMARY")
    log.info("="*60)
    log.info(f"Discrete class boundaries:")
    log.info(f"  SM absolute   : {SM_BOUNDS}")
    log.info(f"  SM difference : {DIFF_SM_BOUNDS}")
    log.info(f"  Runoff abs    : {Q_BOUNDS}")
    log.info(f"  Runoff diff   : {DIFF_Q_BOUNDS}")
    log.info(f"  Precipitation : {P_BOUNDS}")
    log.info(f"Precipitation source: {PRECIP_SOURCE}")
    log.info(f"Irrigation panels: EXCLUDED — GMIA shows 0 valid pixels >30% in this domain")

    for da_exp in da_exps:
        da_label = _da_label(da_exp)
        log.info(f"\n--- {da_label} ---")
        for season in ['DJF', 'JJA']:
            for var, label, unit in [
                ('surface_soil_moisture', 'SM', 'm³/m³'),
                ('total_runoff',          'Q',  'mm/day'),
                ('precipitation',         'P',  'mm/day'),
            ]:
                data, _, _ = _load(nc_dir, var, ref_exp if var == 'precipitation' else da_exp,
                                   season, yr0, yr1)
                if data is None:
                    continue
                v = data[~np.isnan(data)]
                log.info(f"  {label} {season}: min={v.min():.3f}  mean={v.mean():.3f}  max={v.max():.3f}  [{unit}]")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import yaml
    postproc = Path("/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc")
    cfg_path = postproc / "configs/manuscripts/hydrology_seasonal_impact.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
        
    base_out_dir = postproc / cfg['paths'].get('output_dir', 'outputs')
    manuscript_id = cfg.get('manuscript_id', 'hydrology_seasonal_impact')
    
    nc_dir  = base_out_dir / "climatology_nc" / manuscript_id
    out_dir = base_out_dir / "figures" / manuscript_id
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_exp  = "OPL"
    da_exps  = ["DA_NoCDF", "DA_CDF"]
    yr0, yr1 = 2016, 2020

    print_qc(nc_dir, ref_exp, da_exps, yr0, yr1)

    for da_exp in da_exps:
        plot_sm(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1)
        plot_runoff(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1)
        plot_precip_runoff(nc_dir, out_dir, ref_exp, da_exp, yr0, yr1)

    log.info(f"\nAll figures saved to {out_dir}")


if __name__ == "__main__":
    main()
