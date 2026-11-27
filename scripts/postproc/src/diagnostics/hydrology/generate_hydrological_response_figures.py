#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération des figures de réponse hydrologique Noah-MP / SMAP DA (2016-2020).
Intègre la convention d'horodatage physique LIS (d_phys = d_fichier - 1 jour),
la réutilisation directe du cache validé, et l'indication explicite des saturations d'échelle.
"""

import os
import glob
import re
import time
from datetime import datetime, timedelta
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Chemins de base
BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
POSTPROC_DIR = os.path.join(BASE_DIR, "scripts/postproc")
OUTPUT_FIG_HYDRO = os.path.join(POSTPROC_DIR, "outputs/matrix_2016_2020/figures/smap_cdf_sensitivity_2016_2020/hydrology")
OUTPUT_FIG_ASSIM = os.path.join(POSTPROC_DIR, "outputs/matrix_2016_2020/figures/smap_cdf_sensitivity_2016_2020/assimilation")
CACHE_DIR = os.path.join(POSTPROC_DIR, "outputs/matrix_2016_2020/climatology_nc")
TABLES_DIR = os.path.join(POSTPROC_DIR, "outputs/matrix_2016_2020/tables/smap_cdf_sensitivity_2016_2020/water_balance")

os.makedirs(OUTPUT_FIG_HYDRO, exist_ok=True)
os.makedirs(OUTPUT_FIG_ASSIM, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

MASK_FILE = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

EXP_DIRS = {
    "OL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "DA_NoCDF": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
    "DA_CDF": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
}

CACHE_FILE = os.path.join(CACHE_DIR, "flux_climatologies_2016_2020.nc")


def load_domain():
    with nc.Dataset(MASK_FILE) as ds:
        mask = ds.variables["LANDMASK"][:].squeeze() == 1
        lat = ds.variables["lat"][:]
        lon = ds.variables["lon"][:]
    if lat.ndim == 1:
        lon_2d, lat_2d = np.meshgrid(lon, lat)
    else:
        lat_2d, lon_2d = lat, lon
    return mask, lat_2d, lon_2d


def load_flux_climatologies_cache(cache_file, mask):
    """Charge directement les climatologies depuis le cache NetCDF validé."""
    if not os.path.exists(cache_file):
        return None
    print(f"[CACHE] Chargement direct du cache validé : {cache_file}")
    data = {}
    with nc.Dataset(cache_file) as ds:
        for exp in ["OL", "DA_NoCDF", "DA_CDF"]:
            data[exp] = {"annual": {}, "DJF": {}, "JJA": {}}
            for v_name in ["ET", "Qs", "Qsb"]:
                arr = ds.variables[f"{exp}_annual_{v_name}"][:]
                if isinstance(arr, np.ma.MaskedArray):
                    arr = arr.filled(np.nan)
                data[exp]["annual"][v_name] = np.where(mask, arr, np.nan)
            for season in ["DJF", "JJA"]:
                for v_name in ["ET", "Qsb"]:
                    arr = ds.variables[f"{exp}_{season}_{v_name}"][:]
                    if isinstance(arr, np.ma.MaskedArray):
                        arr = arr.filled(np.nan)
                    data[exp][season][v_name] = np.where(mask, arr, np.nan)
    return data


def extract_flux_climatologies(mask, lat_2d, lon_2d):
    """
    Extrait les flux annuels et saisonniers pour les 3 expériences.
    Prend en compte la convention d'horodatage physique LIS :
    LIS_HIST_YYYYMMDD0000 intègre le flux du jour (YYYYMMDD - 1 jour).
    """
    print("[EXTRACTION] Calcul des climatologies sur 1 827 fichiers par expérience...")
    data = {}
    ny, nx = mask.shape
    regex_date = re.compile(r"LIS_HIST_(\d{4})(\d{2})(\d{2})\d{4}\.d01\.nc")

    for exp, exp_dir in EXP_DIRS.items():
        files = sorted(glob.glob(os.path.join(exp_dir, "output/**/LIS_HIST_*.d01.nc"), recursive=True))
        print(f"[{exp}] {len(files)} fichiers trouvés...")
        if len(files) != 1827:
            raise ValueError(f"Fichiers attendus: 1827, trouvés: {len(files)} dans {exp_dir}")

        et_sum = np.zeros((ny, nx), dtype=np.float64)
        qs_sum = np.zeros((ny, nx), dtype=np.float64)
        qsb_sum = np.zeros((ny, nx), dtype=np.float64)

        et_djf = np.zeros((ny, nx), dtype=np.float64)
        qsb_djf = np.zeros((ny, nx), dtype=np.float64)
        count_djf = 0

        et_jja = np.zeros((ny, nx), dtype=np.float64)
        qsb_jja = np.zeros((ny, nx), dtype=np.float64)
        count_jja = 0

        t0 = time.time()
        for f in files:
            m = regex_date.search(os.path.basename(f))
            if not m:
                continue
            # Date physique = Date de fin d'intégration - 1 jour
            d_file = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            d_phys = d_file - timedelta(days=1)
            phys_month = d_phys.month

            with nc.Dataset(f) as ds:
                et_val = ds.variables["Evap_tavg"][:].squeeze() * 86400.0   # kg m-2 s-1 -> mm/jour
                qs_val = ds.variables["Qs_tavg"][:].squeeze() * 86400.0
                qsb_val = ds.variables["Qsb_tavg"][:].squeeze() * 86400.0

            et_sum += et_val
            qs_sum += qs_val
            qsb_sum += qsb_val

            if phys_month in [12, 1, 2]:
                et_djf += et_val
                qsb_djf += qsb_val
                count_djf += 1
            elif phys_month in [6, 7, 8]:
                et_jja += et_val
                qsb_jja += qsb_val
                count_jja += 1

        print(f"[{exp}] Traité en {time.time()-t0:.1f} s. DJF jours={count_djf}, JJA jours={count_jja}")

        # Conversion annuelle : moyenne annuelle en mm/an (somme 5 ans / 5.0)
        data[exp] = {
            "annual": {
                "ET": np.where(mask, et_sum / 5.0, np.nan),
                "Qs": np.where(mask, qs_sum / 5.0, np.nan),
                "Qsb": np.where(mask, qsb_sum / 5.0, np.nan),
            },
            # Conversion saisonnière : cumul moyen par saison en mm/saison (somme totale des saisons / 5.0)
            "DJF": {
                "ET": np.where(mask, et_djf / 5.0, np.nan),
                "Qsb": np.where(mask, qsb_djf / 5.0, np.nan),
            },
            "JJA": {
                "ET": np.where(mask, et_jja / 5.0, np.nan),
                "Qsb": np.where(mask, qsb_jja / 5.0, np.nan),
            }
        }

    # Sauvegarde dans le cache NetCDF
    with nc.Dataset(CACHE_FILE, "w") as ds_out:
        ds_out.createDimension("lat", ny)
        ds_out.createDimension("lon", nx)

        var_lat = ds_out.createVariable("lat", "f4", ("lat", "lon"))
        var_lon = ds_out.createVariable("lon", "f4", ("lat", "lon"))
        var_lat[:] = lat_2d
        var_lon[:] = lon_2d

        for exp in ["OL", "DA_NoCDF", "DA_CDF"]:
            for v_name in ["ET", "Qs", "Qsb"]:
                v = ds_out.createVariable(f"{exp}_annual_{v_name}", "f4", ("lat", "lon"))
                v[:] = np.nan_to_num(data[exp]["annual"][v_name], nan=-9999.0)
                v.missing_value = -9999.0
            for season in ["DJF", "JJA"]:
                for v_name in ["ET", "Qsb"]:
                    v = ds_out.createVariable(f"{exp}_{season}_{v_name}", "f4", ("lat", "lon"))
                    v[:] = np.nan_to_num(data[exp][season][v_name], nan=-9999.0)
                    v.missing_value = -9999.0

    print(f"[CACHE] Sauvegardé avec succès dans {CACHE_FILE}")
    return data


def plot_spatial_flux_response(data, mask, lat_2d, lon_2d):
    """
    Figure 1 (Prioritaire) : Réponse spatiale des flux hydrologiques (ET, Qs, Qsb)
    Grille 3 lignes x 2 colonnes avec échelles communes et indication explicite des saturations.
    """
    print("[PLOTTING] Création de la figure spatiale comparative 3x2...")
    bbox = [-13.2, -1.0, 27.6, 36.0]
    fig = plt.figure(figsize=(13.5, 14.5), dpi=300)
    
    variables = [
        ("Évapotranspiration totale (ET)", "ET", "mm/an", (-100, 100), "RdYlBu",
         "Saturé à ±100 mm/an [Max DA-NoCDF: +480, Max DA-CDF: +324]"),
        ("Ruissellement de surface (Qs)", "Qs", "mm/an", (-20, 20), "PuOr",
         "Saturé à ±20 mm/an [Max DA-NoCDF: +61, Max DA-CDF: +45]"),
        ("Écoulement de base / Drainage (Qsb)", "Qsb", "mm/an", (-50, 50), "BrBG",
         "Saturé à ±50 mm/an [P95: +63 à +72 mm/an | Max: +681 mm/an]"),
    ]
    
    exp_cols = [
        ("DA-NoCDF − OL", "DA_NoCDF"),
        ("DA-CDF v2 − OL", "DA_CDF")
    ]
    
    for row_idx, (var_title, var_key, unit, (vmin, vmax), cmap_name, sat_label) in enumerate(variables):
        for col_idx, (col_title, exp_key) in enumerate(exp_cols):
            ax = fig.add_subplot(3, 2, row_idx * 2 + col_idx + 1, projection=ccrs.PlateCarree())
            ax.set_extent(bbox, crs=ccrs.PlateCarree())
            
            ax.add_feature(cfeature.COASTLINE, linewidth=0.7, edgecolor='#333333')
            ax.add_feature(cfeature.BORDERS, linewidth=0.7, linestyle=':', edgecolor='#555555')
            
            diff = data[exp_key]["annual"][var_key] - data["OL"]["annual"][var_key]
            mean_val = np.nanmean(diff[mask])
            p50 = np.nanpercentile(diff[mask], 50)
            
            norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
            im = ax.pcolormesh(
                lon_2d, lat_2d, diff,
                cmap=cmap_name, norm=norm,
                transform=ccrs.PlateCarree(), shading='auto'
            )
            
            sign_str = "+" if mean_val > 0 else ""
            ax.set_title(
                f"{var_title}\n{col_title} (Moyenne : {sign_str}{mean_val:.2f} {unit} | Médiane : {p50:+.2f})",
                fontsize=10.5, fontweight='bold', pad=7
            )
            
            gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlabel_style = {'size': 8}
            gl.ylabel_style = {'size': 8}
            if col_idx == 1:
                gl.left_labels = False
            if row_idx < 2:
                gl.bottom_labels = False
                
        # Colorbar par ligne avec indication explicite de la saturation
        cbar_ax = fig.add_axes([0.915, 0.70 - row_idx * 0.285, 0.02, 0.20])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='vertical', extend='both')
        cbar.set_label(f"Différence ({unit})", fontsize=9.5, fontweight='bold')
        cbar.ax.tick_params(labelsize=8)
        
        # Annotation textuelle discrète de l'étendue réelle
        fig.text(0.915, 0.685 - row_idx * 0.285, sat_label, fontsize=7.5, style='italic', color='#444444')

    plt.subplots_adjust(left=0.05, right=0.89, top=0.94, bottom=0.04, hspace=0.30, wspace=0.08)
    fig.suptitle(
        "Réponse spatiale moyenne annuelle des flux hydrologiques Noah-MP à l'assimilation SMAP (2016–2020)",
        fontsize=12.5, fontweight='bold', y=0.98
    )
    
    out_png = os.path.join(OUTPUT_FIG_HYDRO, "fig_spatial_flux_response_2016_2020.png")
    out_pdf = os.path.join(OUTPUT_FIG_HYDRO, "fig_spatial_flux_response_2016_2020.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[SUCCESS] Figure spatiale sauvegardée : {out_png}")


def plot_seasonal_flux_response(data, mask, lat_2d, lon_2d):
    """
    Figure 2 : Variabilité saisonnière (DJF vs JJA) pour ET et Qsb.
    Grille 2 lignes x 4 colonnes avec définition temporelle physique exacte.
    """
    print("[PLOTTING] Création de la figure saisonnière DJF/JJA...")
    bbox = [-13.2, -1.0, 27.6, 36.0]
    fig = plt.figure(figsize=(16, 8.5), dpi=300)
    
    seasons = [
        ("DJF", "DA_NoCDF", "DA-NoCDF − OL (Hiver DJF)", (-35, 35)),
        ("DJF", "DA_CDF", "DA-CDF v2 − OL (Hiver DJF)", (-35, 35)),
        ("JJA", "DA_NoCDF", "DA-NoCDF − OL (Été JJA)", (-35, 35)),
        ("JJA", "DA_CDF", "DA-CDF v2 − OL (Été JJA)", (-35, 35)),
    ]
    
    row_vars = [
        ("Évapotranspiration (ET)", "ET", "mm/saison", (-40, 40), "RdYlBu", "Saturé à ±40 mm/saison"),
        ("Écoulement de base (Qsb)", "Qsb", "mm/saison", (-20, 20), "BrBG", "Saturé à ±20 mm/saison [Max DJF: +328 mm/saison]")
    ]
    
    for row_idx, (v_title, v_key, unit, (vmin, vmax), cmap_name, sat_info) in enumerate(row_vars):
        for col_idx, (seas, exp_key, subtitle, _) in enumerate(seasons):
            ax = fig.add_subplot(2, 4, row_idx * 4 + col_idx + 1, projection=ccrs.PlateCarree())
            ax.set_extent(bbox, crs=ccrs.PlateCarree())
            ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='#333333')
            ax.add_feature(cfeature.BORDERS, linewidth=0.6, linestyle=':', edgecolor='#555555')
            
            diff = data[exp_key][seas][v_key] - data["OL"][seas][v_key]
            mean_val = np.nanmean(diff[mask])
            p50 = np.nanpercentile(diff[mask], 50)
            
            norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
            im = ax.pcolormesh(
                lon_2d, lat_2d, diff,
                cmap=cmap_name, norm=norm,
                transform=ccrs.PlateCarree(), shading='auto'
            )
            
            sign_str = "+" if mean_val > 0 else ""
            ax.set_title(f"{subtitle}\n(Moy: {sign_str}{mean_val:.2f} | Méd: {p50:+.2f} {unit})", fontsize=8.5, fontweight='bold', pad=5)
            
            gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlabel_style = {'size': 7}
            gl.ylabel_style = {'size': 7}
            if col_idx > 0:
                gl.left_labels = False
            if row_idx == 0:
                gl.bottom_labels = False
                
        cbar_ax = fig.add_axes([0.92, 0.55 - row_idx * 0.44, 0.015, 0.35])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='vertical', extend='both')
        cbar.set_label(f"Différence {v_title} ({unit})", fontsize=9, fontweight='bold')
        cbar.ax.tick_params(labelsize=8)
        fig.text(0.92, 0.52 - row_idx * 0.44, sat_info, fontsize=7, style='italic', color='#444444')

    plt.subplots_adjust(left=0.04, right=0.91, top=0.92, bottom=0.06, hspace=0.25, wspace=0.10)
    fig.suptitle(
        "Variabilité saisonnière (DJF vs JJA) des réponses hydrologiques ET et Qsb à l'assimilation SMAP (2016–2020)\n"
        "[Dates physiques exactes : DJF = 1er déc. au 28/29 fév. (452 j) | JJA = 1er juin au 31 août (460 j)]",
        fontsize=11.5, fontweight='bold', y=0.98
    )
    
    out_png = os.path.join(OUTPUT_FIG_HYDRO, "fig_seasonal_flux_response_djf_jja_2016_2020.png")
    out_pdf = os.path.join(OUTPUT_FIG_HYDRO, "fig_seasonal_flux_response_djf_jja_2016_2020.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[SUCCESS] Figure saisonnière sauvegardée : {out_png}")


def plot_vertical_increments():
    """
    Figure 3 : Structure verticale et décomposition des incréments EnKF théoriques (L1 à L4).
    Panneau A : Profil vertical cumulé avec épaisseurs physiques réelles (0-10, 10-40, 40-100, 100-200 cm).
    Panneau B : Série temporelle mensuelle des incréments nets par couche issue de table_c.
    """
    print("[PLOTTING] Création de la figure verticale des incréments...")
    
    csv_a = os.path.join(TABLES_DIR, "table_a_enkf_increments_2016_2020.csv")
    csv_c = os.path.join(TABLES_DIR, "table_c_monthly_increments_2016_2020.csv")
    
    df_a = pd.read_csv(csv_a).set_index("experience")
    df_c = pd.read_csv(csv_c)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    layers = ["Couche 1 (0–10 cm)\n[Δz = 100 mm]", 
              "Couche 2 (10–40 cm)\n[Δz = 300 mm]", 
              "Couche 3 (40–100 cm)\n[Δz = 600 mm]", 
              "Couche 4 (100–200 cm)\n[Δz = 1000 mm]"]
    y_pos = np.arange(len(layers))
    bar_width = 0.35
    
    # Données Table A
    pos_nocdf = [df_a.loc["DA-NoCDF", f"Pos_L{i}_mm"] for i in range(1, 5)]
    neg_nocdf = [df_a.loc["DA-NoCDF", f"Neg_L{i}_mm"] for i in range(1, 5)]
    net_nocdf = [df_a.loc["DA-NoCDF", f"Wnet_L{i}_mm"] for i in range(1, 5)]
    
    pos_cdf = [df_a.loc["DA-CDF v2", f"Pos_L{i}_mm"] for i in range(1, 5)]
    neg_cdf = [df_a.loc["DA-CDF v2", f"Neg_L{i}_mm"] for i in range(1, 5)]
    net_cdf = [df_a.loc["DA-CDF v2", f"Wnet_L{i}_mm"] for i in range(1, 5)]
    
    # Panneau A
    ax1.barh(y_pos - bar_width/2, pos_nocdf, bar_width, label="DA-NoCDF : Apports bruts (+)", color="#F4A582", alpha=0.7)
    ax1.barh(y_pos - bar_width/2, neg_nocdf, bar_width, color="#92C5DE", alpha=0.7)
    ax1.plot(net_nocdf, y_pos - bar_width/2, "s", color="#D6604D", markersize=8, label="DA-NoCDF : Net Wnet", zorder=5)
    
    ax1.barh(y_pos + bar_width/2, pos_cdf, bar_width, label="DA-CDF v2 : Apports bruts (+)", color="#B2182B", alpha=0.85)
    ax1.barh(y_pos + bar_width/2, neg_cdf, bar_width, color="#2166AC", alpha=0.85)
    ax1.plot(net_cdf, y_pos + bar_width/2, "D", color="#67001F", markersize=8, label="DA-CDF v2 : Net Wnet", zorder=5)
    
    ax1.axvline(0, color="black", linestyle="--", linewidth=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(layers, fontsize=9, fontweight='bold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Incréments cumulés 2016–2020 (mm équivalent eau)", fontsize=9.5, fontweight='bold')
    ax1.set_title("A. Profil vertical des incréments EnKF théoriques cumulés\n(Apports bruts, retraits bruts et soldes nets)", fontsize=10.5, fontweight='bold')
    ax1.legend(loc="lower right", fontsize=8, frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)
    
    # Panneau B : Série temporelle mensuelle
    df_c["date"] = pd.to_datetime(df_c["mois"])
    colors_layer = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3"]
    
    for i in range(1, 5):
        ax2.plot(df_c["date"], df_c[f"CDF_net_L{i}_mm"], label=f"CDF v2 L{i}", color=colors_layer[i-1], linewidth=1.5)
        ax2.plot(df_c["date"], df_c[f"NoCDF_net_L{i}_mm"], linestyle="--", color=colors_layer[i-1], alpha=0.6, linewidth=1.1)
        
    ax2.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax2.set_xlabel("Date", fontsize=9.5, fontweight='bold')
    ax2.set_ylabel("Incrément mensuel net Wnet (mm/mois)", fontsize=9.5, fontweight='bold')
    ax2.set_title("B. Dynamique mensuelle des incréments nets par couche\n(Trait plein : DA-CDF v2 | Tireté : DA-NoCDF)", fontsize=10.5, fontweight='bold')
    ax2.legend(loc="lower left", fontsize=8, ncol=2, frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)
    
    fig.text(
        0.5, 0.015,
        "Statut algorithmique : Ces valeurs représentent les incréments EnKF théoriques archivés dans les sorties LIS avant tout contrôle physique de Noah-MP\n"
        "(bornes MIN/MAX, quorum d'ensemble) et ne constituent pas des transferts de masse d'eau directement appliqués aux stocks du modèle.",
        ha="center", fontsize=8, style="italic", color="#333333"
    )
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
    out_png = os.path.join(OUTPUT_FIG_ASSIM, "fig_vertical_enkf_increments_2016_2020.png")
    out_pdf = os.path.join(OUTPUT_FIG_ASSIM, "fig_vertical_enkf_increments_2016_2020.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[SUCCESS] Figure verticale d'incréments sauvegardée : {out_png}")


def main(force_extract=False):
    print("=== DÉMARRAGE DE LA FINALISATION ÉTAPE 11 BIS ===")
    mask, lat_2d, lon_2d = load_domain()
    
    data = None
    if not force_extract and os.path.exists(CACHE_FILE):
        data = load_flux_climatologies_cache(CACHE_FILE, mask)
        
    if data is None:
        data = extract_flux_climatologies(mask, lat_2d, lon_2d)
    
    plot_spatial_flux_response(data, mask, lat_2d, lon_2d)
    plot_seasonal_flux_response(data, mask, lat_2d, lon_2d)
    plot_vertical_increments()
    print("=== FIN DE LA PRODUCTION DES FIGURES ÉTAPE 11 BIS ===")

if __name__ == "__main__":
    main()
