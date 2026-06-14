#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)
#
# Plot localization map of the Sebou Basin over Morocco (with unified borders including the Southern Sahara).

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Paths
GEOJSON_PATH = "data/morocco_map.geojson"
OUT_PATH = "postproc/figures/sebou_basin_localization.png"
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# Study Area Bounds
SEBOU_LAT_MIN = 33.0
SEBOU_LAT_MAX = 35.0
SEBOU_LON_MIN = -7.0
SEBOU_LON_MAX = -4.0

# Major Cities Coordinates
CITIES = {
    "Rabat": (-6.8496, 34.0209, "bottom", "right"),
    "Fes": (-5.0003, 34.0331, "bottom", "left"),
    "Casablanca": (-7.5898, 33.5731, "top", "right"),
    "Marrakech": (-7.9811, 31.6295, "top", "right"),
    "Tangier": (-5.8085, 35.7595, "bottom", "left")
}

def plot_localization():
    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(f"Morocco GeoJSON map not found at {GEOJSON_PATH}")

    # Load GeoJSON
    with open(GEOJSON_PATH, 'r') as f:
        geojson_data = json.load(f)

    plt.figure(figsize=(10, 10), dpi=300)
    plt.style.use('seaborn-whitegrid')
    ax = plt.gca()

    # Draw Morocco unified boundaries
    poly = geojson_data['geometries'][0]
    coords = poly['coordinates']

    print("Drawing Morocco boundaries...")
    for ring in coords:
        ring = np.array(ring)
        if ring.ndim == 3:
            for r in ring:
                r = np.array(r)
                ax.fill(r[:, 0], r[:, 1], facecolor="#eae6df", edgecolor="#555555", linewidth=1.2, zorder=2)
        elif ring.ndim == 2:
            ax.fill(ring[:, 0], ring[:, 1], facecolor="#eae6df", edgecolor="#555555", linewidth=1.2, zorder=2)

    # Draw Sebou Basin Bounding Box (translucent red fill, thick red border)
    width = SEBOU_LON_MAX - SEBOU_LON_MIN
    height = SEBOU_LAT_MAX - SEBOU_LAT_MIN
    sebou_rect = Rectangle(
        (SEBOU_LON_MIN, SEBOU_LAT_MIN), width, height,
        linewidth=2.0, edgecolor="#d9534f", facecolor="#d9534f", alpha=0.35, zorder=3, label="Sebou Basin Study Area"
    )
    ax.add_patch(sebou_rect)
    
    # Plot outer red dashed line for emphasis
    rect_outline = Rectangle(
        (SEBOU_LON_MIN, SEBOU_LAT_MIN), width, height,
        linewidth=2.0, edgecolor="#d9534f", facecolor="none", linestyle="--", zorder=4
    )
    ax.add_patch(rect_outline)

    # Plot major cities
    print("Plotting city markers...")
    city_lon = [c[0] for c in CITIES.values()]
    city_lat = [c[1] for c in CITIES.values()]
    ax.scatter(city_lon, city_lat, color="black", edgecolor="white", s=60, marker="o", zorder=5)

    # Add text labels for cities
    for city, (lon, lat, va, ha) in CITIES.items():
        # Offset to prevent overlap with the marker
        offset_x = 0.15 if ha == "left" else -0.15
        offset_y = 0.15 if va == "bottom" else -0.15
        ax.text(
            lon + offset_x, lat + offset_y, city,
            fontsize=11, fontweight="bold", va=va, ha=ha, zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75, ec="none")
        )

    # Add geographical labels
    ax.text(-12.5, 30.5, "ATLANTIC\nOCEAN", fontsize=14, color="#3b7a9e", style="italic", fontweight="bold", ha="center", zorder=1)
    ax.text(-3.0, 36.2, "MEDITERRANEAN SEA", fontsize=12, color="#3b7a9e", style="italic", fontweight="bold", ha="center", zorder=1)
    
    # Label Sebou Basin inside the study area
    ax.text(
        (SEBOU_LON_MIN + SEBOU_LON_MAX) / 2.0, SEBOU_LAT_MAX + 0.35, "Sebou Basin\nStudy Area",
        fontsize=12, color="#c9302c", fontweight="bold", ha="center", va="center", zorder=6,
        bbox=dict(boxstyle="round,pad=0.3", fc="#fff5f5", ec="#d9534f", lw=1)
    )

    # Map extent and ticks (enclosing Morocco and the basin)
    ax.set_xlim(-18.0, -1.0)
    ax.set_ylim(20.0, 37.0)
    
    # Grid lines and labels
    ax.set_xlabel("Longitude (°E)", fontsize=12, fontweight="bold", labelpad=10)
    ax.set_ylabel("Latitude (°N)", fontsize=12, fontweight="bold", labelpad=10)
    ax.tick_params(labelsize=10)
    ax.grid(True, linestyle=":", alpha=0.6, zorder=1)

    # Add title and legend
    plt.title("Location of the Sebou Basin Study Area within Morocco", fontsize=15, fontweight="bold", pad=20)
    
    # Custom legend
    ax.legend(handles=[sebou_rect], loc="lower left", frameon=True, facecolor="white", edgecolor="none", fontsize=11)

    # Save Figure
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Localization map successfully generated: {OUT_PATH}")

if __name__ == "__main__":
    plot_localization()
