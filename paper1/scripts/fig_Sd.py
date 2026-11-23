#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_Sd.py
---------
Figure S-d : Diagnostic hydrologique et assimilation sur le bassin versant de Lalla Chafia (2018).
Panels :
  (a) Innovations mensuelles de l'humidité de surface SMAP (θ_obs - θ_prior) pour DA_nocdf, DA_cdf et DA_corr.
  (b) Incréments EnKF appliqués par couche de sol (1 à 4) et incrément total (mm/mois) pour les 3 systèmes DA.
  (c) Drainage profond mensuel Qsb (mm/mois) simulant la recharge et l'alimentation du débit de base
      pour les expériences d'assimilation et les références (OPL, OL_DAIC).

Outputs :
  paper1/figures/fig_Sd.png (200 dpi)
  paper1/figures/fig_Sd_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

OUT_FIG = os.path.join(FIGURES_DIR, "fig_Sd.png")
OUT_CSV = os.path.join(FIGURES_DIR, "fig_Sd_data.csv")

INNOV_CSV = os.path.join(TABLES_DIR, "lalla_chafia_innovations_and_increments.csv")
WB_CATCH_CSV = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")

def main():
    print("=== GÉNÉRATION FIG. S-d : BASSIN DE LALLA CHAFIA (2018) ===")
    
    df_innov = pd.read_csv(INNOV_CSV)
    df_wb = pd.read_csv(WB_CATCH_CSV)

    # 1. Filter Data for Lalla Chafia Monthly 2018
    target_da = ['DA_nocdf', 'DA_cdf', 'DA_corr']
    sub_innov = df_innov[(df_innov['target'] == 'Lalla Chafia') & 
                         (df_innov['period_type'] == 'monthly_2018') & 
                         (df_innov['experiment'].isin(target_da))].copy()
    
    sub_innov['month'] = sub_innov['period'].apply(lambda x: int(x.split('-')[1]))
    sub_innov = sub_innov.sort_values(['experiment', 'month'])

    sub_wb = df_wb[(df_wb['station'] == 'Lalla Chafia') & 
                   (df_wb['year_month'].str.startswith('2018-'))].copy()
    sub_wb['month'] = sub_wb['year_month'].apply(lambda x: int(x.split('-')[1]))
    sub_wb = sub_wb.sort_values(['experiment', 'month'])

    # Save Plotted Data
    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_B_INNOVATIONS_ET_INCREMENTS_LALLA_CHAFIA\n")
        sub_innov[['experiment', 'period', 'month', 'n_obs_assimilated', 'mean_innovation_m3m3',
                   'incr_layer1_mm', 'incr_layer2_mm', 'incr_layer3_mm', 'incr_layer4_mm', 'incr_total_mm']].to_csv(f, index=False)
        f.write("\n# PANEL_C_QSB_MENSUEL_LALLA_CHAFIA\n")
        sub_wb[['experiment', 'year_month', 'month', 'Qsb_mm', 'Qs_mm', 'TotalRunoff_mm', 'WaterBalance_Residual_mm']].to_csv(f, index=False)
    print(f"[OK] Données tracées exportées dans : {OUT_CSV}")

    # 2. Setup Figure Layout (3 Panels Vertical)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 14), sharex=True)
    fig.subplots_adjust(hspace=0.25, left=0.08, right=0.95, top=0.93, bottom=0.07)

    months = np.arange(1, 13)
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    colors_exp = {
        'DA_nocdf': '#D55E00',       # Rouge production
        'DA_cdf': '#CC79A7',         # Rose DA CDF
        'DA_corr': '#0072B2',        # Bleu DA corrigé
        'OPL': '#999999',            # Gris baseline
        'OL_DAIC': '#56B4E9'         # Bleu ciel OL
    }

    # ── Panel (a): Innovations Mensuelles ──────────────────────────────────────
    styles_a = {'DA_nocdf': ('--', 's'), 'DA_cdf': ('-.', '^'), 'DA_corr': ('-', 'o')}
    labels_a = {
        'DA_nocdf': 'DA_nocdf (Production : EnKF sans CDF, sans seuil flétrissement)',
        'DA_cdf': 'DA_cdf (Production : EnKF avec CDF matching)',
        'DA_corr': 'DA_corr (Corrigé : Filtre flétrissement + EnKF corrigé)'
    }

    for exp in target_da:
        s = sub_innov[sub_innov['experiment'] == exp].sort_values('month')
        ls, mkr = styles_a[exp]
        ax1.plot(months, s['mean_innovation_m3m3'].to_numpy(),
                 color=colors_exp[exp], ls=ls, marker=mkr, lw=2.0, ms=6,
                 label=labels_a[exp])

    ax1.axhline(0, color='black', lw=0.8, ls=':')
    ax1.set_ylabel("Innovation moyenne ($m^3/m^3$)\n[Obs − Prior]", fontsize=11, fontweight='bold')
    ax1.set_title("(a) Innovations mensuelles SMAP sur le bassin amont de Lalla Chafia en 2018",
                  fontsize=12, fontweight='bold', pad=8)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=9, framealpha=0.92)

    # ── Panel (b): Incréments EnKF par Couche (Stacked Bars / Multi-bars) ──────
    # Affichage en 3 groupes de barres par mois
    w = 0.25
    x_nocdf = months - w
    x_cdf = months
    x_corr = months + w

    # Plot total increments as bars, with points for layer distribution
    ax2.bar(x_nocdf, sub_innov[sub_innov['experiment'] == 'DA_nocdf']['incr_total_mm'],
            width=w, color=colors_exp['DA_nocdf'], alpha=0.8, label='DA_nocdf : Incrément Total')
    ax2.bar(x_cdf, sub_innov[sub_innov['experiment'] == 'DA_cdf']['incr_total_mm'],
            width=w, color=colors_exp['DA_cdf'], alpha=0.8, label='DA_cdf : Incrément Total')
    ax2.bar(x_corr, sub_innov[sub_innov['experiment'] == 'DA_corr']['incr_total_mm'],
            width=w, color=colors_exp['DA_corr'], alpha=0.8, label='DA_corr : Incrément Total')

    # Add markers for Layer 4 increment (deep layer injection)
    ax2.plot(x_nocdf, sub_innov[sub_innov['experiment'] == 'DA_nocdf']['incr_layer4_mm'].to_numpy(),
             color='#7A2E00', marker='v', ls='', ms=5, label='DA_nocdf : Couche 4 (1-2 m)')
    ax2.plot(x_cdf, sub_innov[sub_innov['experiment'] == 'DA_cdf']['incr_layer4_mm'].to_numpy(),
             color='#6B1846', marker='v', ls='', ms=5, label='DA_cdf : Couche 4 (1-2 m)')
    ax2.plot(x_corr, sub_innov[sub_innov['experiment'] == 'DA_corr']['incr_layer4_mm'].to_numpy(),
             color='#003366', marker='v', ls='', ms=5, label='DA_corr : Couche 4 (1-2 m)')

    ax2.axhline(0, color='black', lw=0.8, ls='-')
    ax2.set_ylabel("Incrément d'assimilation (mm/mois)", fontsize=11, fontweight='bold')
    ax2.set_title("(b) Incréments nets injectés dans le profil de sol (Total et Couche profonde 4)",
                  fontsize=12, fontweight='bold', pad=8)
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=8.5, ncol=2, framealpha=0.92)

    # ── Panel (c): Drainage Profond Mensuel Qsb ────────────────────────────────
    target_qsb = ['OPL', 'OL_DAIC', 'DA_nocdf', 'DA_cdf', 'DA_corr']
    labels_c = {
        'OPL': 'OPL (Baseline sans DA)',
        'OL_DAIC': 'OL_DAIC (Open Loop DAIC)',
        'DA_nocdf': 'DA_nocdf (Production : Surgénérescence de drainage)',
        'DA_cdf': 'DA_cdf (Production : Régulé par CDF matching)',
        'DA_corr': 'DA_corr (Corrigé : Équilibre restauré)'
    }
    styles_c = {
        'OPL': (':', 'x', 1.5),
        'OL_DAIC': ('-', '+', 1.5),
        'DA_nocdf': ('--', 's', 2.2),
        'DA_cdf': ('-.', '^', 1.8),
        'DA_corr': ('-', 'D', 2.2)
    }

    for exp in target_qsb:
        s = sub_wb[sub_wb['experiment'] == exp].sort_values('month')
        if len(s) == 12:
            ls, mkr, lw = styles_c[exp]
            ax3.plot(months, s['Qsb_mm'].to_numpy(),
                     color=colors_exp[exp], ls=ls, marker=mkr, lw=lw, ms=6,
                     label=labels_c[exp])

    ax3.set_xticks(months)
    ax3.set_xticklabels(month_names, fontsize=11, fontweight='medium')
    ax3.set_ylabel("Drainage profond $Q_{sb}$ (mm/mois)", fontsize=11, fontweight='bold')
    ax3.set_title("(c) Drainage profond mensuel $Q_{sb}$ sur Lalla Chafia (Alimentation du débit de base)",
                  fontsize=12, fontweight='bold', pad=8)
    ax3.grid(True, linestyle=':', alpha=0.5)
    ax3.legend(loc='upper right', fontsize=9.0, framealpha=0.92)

    plt.suptitle("Figure S-d : Diagnostic Détaillé sur le Bassin Amont de Lalla Chafia (2018)",
                 fontsize=15, fontweight='bold', y=0.97)

    plt.savefig(OUT_FIG, dpi=200)
    plt.close()
    print(f"[OK] Figure S-d sauvegardée dans : {OUT_FIG}")

if __name__ == '__main__':
    main()
