# Chaîne Complète de Post-Traitement et Production des Résultats HyMAP

Ce document formalise l'intégralité de la chaîne de traitement hydrologique, depuis l'extraction des ruissellements Noah-MP jusqu'à la génération des figures scientifiques publiables.

---

## 1. Vue d'Ensemble du Pipeline en 8 Étapes

```
[Étape 1] Sorties Noah-MP (Qs_tavg, Qsb_tavg) à 0.05° (121x181)
          matrix_2016_2020/[EXP]_noirr_2016_2020/output/SURFACEMODEL/
    │
    ▼  (scripts/remap_*.py)
[Étape 2] Ruissellements remappés sur grille HyMAP (180x120)
          runoff_remap_180x120/[EXP]_noirr_2016_2020/
    │
    ▼  (jobs/run_hymap2_*_spinup_*.sh)
[Étape 3] Spin-up HyMAP 2016 C1 -> C2 (Convergence BSFSTO < 1.0 %)
          output/[EXP]_spinup_c2/ROUTING/201701/LIS_RST_*.nc
    │
    ▼  (jobs/run_hymap2_*_2016_2020.sh)
[Étape 4] Production HyMAP 2016–2020 (1 827 fichiers LIS_HIST NetCDF par expérience)
          output/[EXP]_2016_2020/ROUTING/YYYYMM/LIS_HIST_*.nc
    │
    ▼  (Extraction Streamflow_tavg via row_hymap / col_hymap)
[Étape 5] Caches journaliers 12 stations
          output/[EXP]_2016_2020/t*_sim_daily_*.csv
    │
    ▼  (scripts/sebou_bouregreg_diagnostic.py + data/streamflow_clean/)
[Étape 6] Alignement temporel et appariement aux observations ABH
    │
    ▼  (Calcul KGE, NSE, r, PBIAS, extrêmes et bilans amont délimités)
[Étape 7] Tables canoniques
          plots/sebou_bouregreg/tables/
    │
    ▼  (Tracés ciblés Sebou & Bouregreg)
[Étape 8] Figures scientifiques canoniques
          plots/sebou_bouregreg/figures/streamflow/
```

---

## 2. Tableau Détaillé des Scripts et Flux de Données

| Étape | Script | Expériences | Entrées lues (Inputs vérifiés) | Produits générés (Outputs) | Emplacement actuel | Remarques méthodologiques |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1→2** | `scripts/remap_opl_2016_2020.py` | OPL | `matrix_2016_2020/OPL_noirr_2016_2020/output/SURFACEMODEL/` | 1 828 NetCDF journaliers (`Qs`, `Qsb`) | `runoff_remap_180x120/OPL_noirr_2016_2020/` | Utilise la grille cible de `ldt_hymap/lis_input_corrigee.d01.nc` |
| **1→2** | `scripts/remap_da_nocdf_2016_2020.py` | DA-NoCDF | `matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/SURFACEMODEL/` | 1 828 NetCDF journaliers | `runoff_remap_180x120/DA_nocdf_noirr_2016_2020/` | Idem |
| **1→2** | `scripts/remap_da_cdf_2016_2020.py` | DA-CDF | `matrix_2016_2020/DA_cdf_noirr_2016_2020/output/SURFACEMODEL/` | 1 828 NetCDF journaliers | `runoff_remap_180x120/DA_cdf_noirr_2016_2020/` | Idem |
| **Ctrl** | `scripts/check_remap_conservation_2018.py` | Toutes | Grilles source 121x181 et cible 180x120 | Contrôle volumique global domaine | Sortie terminal / logs | **Contrôle global domaine uniquement** (< 0.01 % d'écart total) ; ne constitue pas une preuve de conservation par sous-bassin. |
| **Ctrl** | `scripts/check_spinup_criterion_corrigee.py` | OPL | Restarts C1 & C2 au 01/01/2017 | Bilan stock BSFSTO | Sortie terminal | $\Delta S_{\text{BSF}} = 0.132\%$ |
| **Ctrl** | `scripts/check_spinup_criterion_da_nocdf.py` | DA-NoCDF | Restarts C1 & C2 au 01/01/2017 | Bilan stock BSFSTO | Sortie terminal | $\Delta S_{\text{BSF}} = 0.065\%$ |
| **5** | `scripts/complete_t7bis_analysis.py` | OPL | 1 827 LIS_HIST OPL | Cache débits OPL & tables historiques | `output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv` | Générateur du cache OPL |
| **5** | `scripts/complete_t8_analysis_and_plots.py` | OPL & DA-NoCDF | 1 827 LIS_HIST NoCDF + cache OPL | Cache NoCDF, tables T8, figures historiques | `output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`, `plots/_history/tache8_pour_hydro/` | Analyse historique T8 |
| **5** | `scripts/compare_3experiments_hydro.py` | 3 exp | 1 827 LIS_HIST DA-CDF + caches OPL & NoCDF | Cache DA-CDF, planches brutes 12 stations | `output/DA_cdf_2016_2020/t9_sim_daily_12stations_da_cdf.csv`, `plots/_history/comparison_3experiments_raw/` | Générateur du cache DA-CDF |
| **6→8** | `scripts/sebou_bouregreg_diagnostic.py` | 3 exp | 3 caches débits + observations ABH + LDT HyMAP | 3 tables validées + 3 figures ciblées Sebou–Bouregreg | `plots/sebou_bouregreg/tables/`, `plots/sebou_bouregreg/figures/streamflow/` | **Script canonique de production scientifique actuelle** |

---

## 3. Typologie des Données et Organisation

1. **Sorties brutes de modèle (`routing/output/`)** :
   * Contiennent exclusivement les arborescences NetCDF journalières (`ROUTING/YYYYMM/LIS_HIST_*.nc`), les restarts (`LIS_RST_*.nc`) et les journaux d'exécution (`lislog`).
   * Ces répertoires sont intangibles.
2. **Produits intermédiaires de post-traitement (Caches d'extraction)** :
   * Les débits extraits aux 12 stations sont conservés sous forme de fichiers CSV journaliers dans le répertoire de chaque simulation :
     - OPL : `output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv`
     - DA-NoCDF : `output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`
     - DA-CDF : `output/DA_cdf_2016_2020/t9_sim_daily_12stations_da_cdf.csv`
   * Ces caches permettent de relancer l'ensemble des diagnostics sans relire les 5 481 fichiers NetCDF.
3. **Résultats scientifiques actuels (`routing/plots/sebou_bouregreg/`)** :
   * Contient les tables validées (`tables/`) et les trois figures d'évaluation 3exp actuelles (`figures/streamflow/`).
4. **Diagnostics techniques (`routing/plots/technical/`)** :
   * Spin-up (`spinup/`), bilan des réservoirs OPL (`water_balance/`), paramètres et chronologie d'observation (`parameters/`).
5. **Archives patrimoniales (`routing/plots/_history/`)** :
   * Tâche 8 binaire OPL vs DA-NoCDF (`tache8_pour_hydro/`), planches brutes 3exp (`comparison_3experiments_raw/`), et anciennes figures unitaires (`exploratoire_t5_t7/`).

---

## 4. Reproduction Pas-à-Pas des Résultats Scientifiques

Pour reproduire ou recalculer les tables et figures canoniques Sebou–Bouregreg sans régénération lourde :

```bash
# Activer l'environnement Python
source activate postproc_env

# Exécuter le script canonique
python experiments/NorthMor/routing/scripts/sebou_bouregreg_diagnostic.py
```

Ce script charge les caches CSV existants, délimite les bassins versants amont connectés par le réseau de drainage HyMAP, calcule les métriques et écrit directement dans :
- `plots/sebou_bouregreg/tables/`
- `plots/sebou_bouregreg/figures/streamflow/`
