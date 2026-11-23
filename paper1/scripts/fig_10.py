#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_10.py
---------
Figure 10 : Système de Production vs Système Corrigé (2018).
Panels :
  (a) Résidu mensuel du bilan hydrique R en 2018 : ENS_OPL vs ENS_corr, et DA_nocdf vs DA_corr.
  (b) Effet des observations sur l'évapotranspiration (ΔET) par mois :
      Système de production (DA_nocdf - ENS_OPL) vs Système corrigé (DA_corr - ENS_corr).
  (c) Impact sur la performance ET contre WaPOR v3 (Δ|biais| et fraction de mailles améliorées)
      pour l'effet des observations (production vs corrigé) à travers les strates géographiques et texturales.

Outputs :
  paper1/figures/fig_10.png (200 dpi)
  paper1/figures/fig_10_data.csv
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

OUT_FIG = os.path.join(FIGURES_DIR, "fig_10.png")
OUT_CSV = os.path.join(FIGURES_DIR, "fig_10_data.csv")

WB_MONTHLY_CSV = os.path.join(TABLES_DIR, "water_balance_corrected_2018_monthly.csv")
CLEAN_DIFF_CSV = os.path.join(TABLES_DIR, "clean_differences_2018.csv")
DIR_CHANGE_CSV = os.path.join(TABLES_DIR, "et_direction_of_change_corrected_2018.csv")

def main():
    print("=== GÉNÉRATION FIG. 10 : PRODUCTION VS CORRIGÉ (2018) ===")
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_wb = pd.read_csv(WB_MONTHLY_CSV)
    df_diff = pd.read_csv(CLEAN_DIFF_CSV)
    df_chg = pd.read_csv(DIR_CHANGE_CSV)

    # Panel (a) Data
    target_exps = ['ENS_OPL', 'ENS_corr', 'DA_nocdf', 'DA_corr']
    df_a = df_wb[df_wb['experiment'].isin(target_exps)].copy()
    
    # Panel (b) Data
    target_pairs_b = ['DA_nocdf - ENS_OPL', 'DA_corr - ENS_corr']
    months_12 = [f"2018-{m:02d}" for m in range(1, 13)]
    df_b = df_diff[(df_diff['pair'].isin(target_pairs_b)) & (df_diff['period'].isin(months_12))].copy()
    
    # Panel (c) Data
    df_c = df_chg[(df_chg['reference'] == 'WaPOR_v3') & 
                  (df_chg['season'] == 'Annual') & 
                  (df_chg['pair'].isin(target_pairs_b))].copy()

    # Save plotted data CSV
    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_RESIDU_MENSUEL_2018\n")
        df_a[['experiment', 'month', 'WaterBalance_Residual_mm', 'Incr_Total_mm']].to_csv(f, index=False)
        f.write("\n# PANEL_B_DELTA_ET_OBS_EFFECT_MONTHLY\n")
        df_b[['pair', 'period', 'delta_ET_mm', 'delta_P_mm', 'delta_Residual_mm']].to_csv(f, index=False)
        f.write("\n# PANEL_C_WAPOR_IMPACT_STRATA\n")
        df_c[['pair', 'stratum_type', 'stratum', 'delta_abs_bias_mm', 'frac_closer_pct', 'direction']].to_csv(f, index=False)
    print(f"[OK] Données tracées exportées dans : {OUT_CSV}")

    # ── 2. Create Figure Layout ────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.0, 1.1], width_ratios=[1.0, 1.0],
                           hspace=0.28, wspace=0.22, left=0.06, right=0.96, top=0.92, bottom=0.08)

    # ── Panel (a): Monthly Water Balance Residual R ────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    
    months = np.arange(1, 13)
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    colors_a = {
        'ENS_OPL': '#D55E00',       # Rouge production
        'ENS_corr': '#009E73',      # Vert corrigé
        'DA_nocdf': '#CC79A7',      # Rose production DA
        'DA_corr': '#0072B2'        # Bleu corrigé DA
    }
    labels_a = {
        'ENS_OPL': 'ENS_OPL (Production : Ryu=1, Midrange actif)',
        'ENS_corr': 'ENS_corr (Corrigé : Ryu=0, Midrange supprimé)',
        'DA_nocdf': 'DA_nocdf (Production : EnKF standard)',
        'DA_corr': 'DA_corr (Corrigé : Filtre flétrissement + EnKF corrigé)'
    }
    styles_a = {
        'ENS_OPL': ('--', 's'),
        'ENS_corr': ('-', 'o'),
        'DA_nocdf': ('--', '^'),
        'DA_corr': ('-', 'D')
    }

    for exp in target_exps:
        sub = df_a[df_a['experiment'] == exp].sort_values('month')
        ls, mkr = styles_a[exp]
        ax_a.plot(months, sub['WaterBalance_Residual_mm'].to_numpy(),
                  color=colors_a[exp], ls=ls, marker=mkr, lw=2.0, ms=6,
                  label=labels_a[exp])

    ax_a.axhline(0, color='gray', lw=1.0, ls=':')
    ax_a.set_xticks(months)
    ax_a.set_xticklabels(month_names, fontsize=10)
    ax_a.set_ylabel("Résidu du bilan $R$ (mm/mois)", fontsize=11, fontweight='bold')
    ax_a.set_title("(a) Résidu mensuel du bilan interne ($R = P - ET - Q - \\Delta S$) en 2018",
                   fontsize=12, fontweight='bold', pad=8)
    ax_a.grid(True, linestyle=':', alpha=0.5)
    ax_a.legend(loc='upper right', fontsize=8.5, framealpha=0.92)

    # ── Panel (b): ΔET Observation Effect Monthly ──────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])

    sub_b_prod = df_b[df_b['pair'] == 'DA_nocdf - ENS_OPL'].copy()
    sub_b_corr = df_b[df_b['pair'] == 'DA_corr - ENS_corr'].copy()
    
    sub_b_prod['m_num'] = sub_b_prod['period'].apply(lambda x: int(x.split('-')[1]))
    sub_b_corr['m_num'] = sub_b_corr['period'].apply(lambda x: int(x.split('-')[1]))
    
    sub_b_prod = sub_b_prod.sort_values('m_num')
    sub_b_corr = sub_b_corr.sort_values('m_num')

    w = 0.38
    x_prod = months - w/2
    x_corr = months + w/2

    ax_b.bar(x_prod, sub_b_prod['delta_ET_mm'], width=w, color='#E69F00', alpha=0.85,
             label='Effet observations production (DA_nocdf − ENS_OPL)')
    ax_b.bar(x_corr, sub_b_corr['delta_ET_mm'], width=w, color='#56B4E9', alpha=0.85,
             label='Effet observations corrigé (DA_corr − ENS_corr)')

    ax_b.axhline(0, color='black', lw=0.8, ls='-')
    ax_b.set_xticks(months)
    ax_b.set_xticklabels(month_names, fontsize=10)
    ax_b.set_ylabel("$\\Delta ET$ dû aux observations (mm/mois)", fontsize=11, fontweight='bold')
    ax_b.set_title("(b) Impact net de l'assimilation sur l'évapotranspiration ($\\Delta ET$ mensuel)",
                   fontsize=12, fontweight='bold', pad=8)
    ax_b.grid(True, linestyle=':', alpha=0.5)
    ax_b.legend(loc='lower right', fontsize=8.5, framealpha=0.92)

    # ── Panel (c): Δ|bias| against WaPOR v3 across Strata ──────────────────────
    ax_c = fig.add_subplot(gs[1, :])

    strata_order = [
        ("Geographic", "Domain", "Domaine"),
        ("Geographic", "Sebou", "Sebou"),
        ("Geographic", "Bouregreg", "Bouregreg"),
        ("Texture", "Texture_3_Sandy Loam", "Sandy Loam"),
        ("Texture", "Texture_6_Loam", "Loam"),
        ("Texture", "Texture_7_Sandy Clay Loam", "Sandy Clay Loam"),
        ("Texture", "Texture_9_Clay Loam", "Clay Loam"),
        ("Texture", "Texture_12_Clay", "Clay")
    ]

    labels_c = [s[2] for s in strata_order]
    x_c = np.arange(len(strata_order))

    delta_bias_prod = []
    delta_bias_corr = []
    frac_closer_prod = []
    frac_closer_corr = []

    for st_type, st_key, _ in strata_order:
        r_prod = df_c[(df_c['pair'] == 'DA_nocdf - ENS_OPL') & (df_c['stratum'] == st_key)]
        r_corr = df_c[(df_c['pair'] == 'DA_corr - ENS_corr') & (df_c['stratum'] == st_key)]
        
        delta_bias_prod.append(r_prod['delta_abs_bias_mm'].values[0] if len(r_prod) > 0 else np.nan)
        delta_bias_corr.append(r_corr['delta_abs_bias_mm'].values[0] if len(r_corr) > 0 else np.nan)
        frac_closer_prod.append(r_prod['frac_closer_pct'].values[0] if len(r_prod) > 0 else np.nan)
        frac_closer_corr.append(r_corr['frac_closer_pct'].values[0] if len(r_corr) > 0 else np.nan)

    width_c = 0.35
    rects1 = ax_c.bar(x_c - width_c/2, delta_bias_prod, width=width_c, color='#E69F00', alpha=0.85,
                      label='$\\Delta|biais|$ Production (DA_nocdf − ENS_OPL)')
    rects2 = ax_c.bar(x_c + width_c/2, delta_bias_corr, width=width_c, color='#0072B2', alpha=0.85,
                      label='$\\Delta|biais|$ Corrigé (DA_corr − ENS_corr)')

    ax_c.axhline(0, color='black', lw=1.0, ls='-')
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(labels_c, fontsize=11, fontweight='medium')
    ax_c.set_ylabel("$\\Delta|Biais|$ contre WaPOR v3 (mm/an)\n[Valeur négative = Rapprochement / Amélioration]",
                    fontsize=11, fontweight='bold')
    ax_c.set_title("(c) Validation indépendante contre WaPOR v3 : Réduction du biais absolu annuel par strate",
                   fontsize=12, fontweight='bold', pad=8)
    ax_c.grid(True, linestyle=':', alpha=0.5)

    # Annotate fraction of closer cells on top/bottom of bars
    for i in range(len(strata_order)):
        val_p = delta_bias_prod[i]
        fc_p = frac_closer_prod[i]
        offset_p = -8 if val_p < 0 else 3
        ax_c.annotate(f"{fc_p:.1f}%\napproch.", xy=(x_c[i] - width_c/2, val_p + offset_p),
                     ha='center', va='bottom' if val_p < 0 else 'top', fontsize=7.8, color='#8A4500', fontweight='bold')

        val_c = delta_bias_corr[i]
        fc_c = frac_closer_corr[i]
        offset_c = -8 if val_c < 0 else 3
        ax_c.annotate(f"{fc_c:.1f}%\napproch.", xy=(x_c[i] + width_c/2, val_c + offset_c),
                     ha='center', va='bottom' if val_c < 0 else 'top', fontsize=7.8, color='#004C78', fontweight='bold')

    ax_c.legend(loc='lower left', fontsize=9.5, framealpha=0.92)

    plt.suptitle("Figure 10 : Comparaison Globale du Système de Production et du Système Corrigé (2018)",
                 fontsize=15, fontweight='bold', y=0.97)

    plt.savefig(OUT_FIG, dpi=200)
    plt.close()
    print(f"[OK] Figure 10 sauvegardée dans : {OUT_FIG}")

if __name__ == '__main__':
    main()
