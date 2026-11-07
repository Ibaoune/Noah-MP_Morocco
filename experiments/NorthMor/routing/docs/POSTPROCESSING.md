# Chaîne de Post-Traitement et Production des Résultats HyMAP

Ce document formalise l'intégralité de la chaîne de traitement hydrologique HyMAP couplée à Noah-MP pour le Nord Maroc (2016–2020), depuis le remapping des flux jusqu'aux figures et tables scientifiques canoniques.

---

## 1. Vue d'Ensemble du Pipeline en 5 Étapes

```
[Étape 1] Ruissellements Noah-MP (Qs, Qsb) à 0.05° (121x181)
          matrix_2016_2020/[EXP]_noirr_2016_2020/output/SURFACEMODEL/
    │
    ▼  (scripts/remap_runoff_*.py)
[Étape 2] Ruissellements conservatifs remappés sur grille HyMAP (180x120)
          runoff_remap_180x120/[EXP]_noirr_2016_2020/SURFACEMODEL/
    │
    ▼  (jobs/run_hymap2_*_spinup_*.sh -> jobs/run_hymap2_*_2016_2020.sh)
[Étape 3] Simulations HyMAP 2016–2020 (1 827 fichiers LIS_HIST NetCDF par expérience)
          output/[EXP]_2016_2020/ROUTING/YYYYMM/LIS_HIST_*.nc
    │
    ▼  (scripts/extract_streamflow.py + stations/hymap_stations_pairing.csv)
[Étape 4] Caches journaliers 12 stations (1 827 jours, 2016-01-01 à 2020-12-31)
          output/[EXP]_2016_2020/t*_sim_daily_*.csv
    │
    ▼  (scripts/evaluate_sebou_bouregreg.py + data/streamflow_clean/)
[Étape 5] Métriques, Bilans d'Apports Amont et Figures Canoniques
          plots/sebou_bouregreg/tables/
          plots/sebou_bouregreg/figures/streamflow/
```

---

## 2. Tableau des Scripts Maintenus

| Étape | Script | Fonction opérationnelle | Entrées lues | Sorties produites |
| :---: | :--- | :--- | :--- | :--- |
| **1→2** | `scripts/remap_runoff_opl.py` | Remapping conservatif Qs/Qsb OPL (181x121 $\rightarrow$ 180x120) | Sorties Noah-MP OPL | 1 828 NetCDF dans `runoff_remap_180x120/OPL_.../` |
| **1→2** | `scripts/remap_runoff_da_nocdf.py` | Remapping conservatif Qs/Qsb DA-NoCDF | Sorties Noah-MP DA-NoCDF | 1 828 NetCDF dans `runoff_remap_180x120/DA_nocdf_.../` |
| **1→2** | `scripts/remap_runoff_da_cdf.py` | Remapping conservatif Qs/Qsb DA-CDF | Sorties Noah-MP DA-CDF | 1 828 NetCDF dans `runoff_remap_180x120/DA_cdf_.../` |
| **Ctrl** | `scripts/check_remap_conservation_2018.py` | Contrôle volumique global du remapping | Grilles Noah-MP et HyMAP | Bilan de masse domaine (< 0.01 % d'écart) |
| **Ctrl** | `scripts/check_spinup_criterion_corrigee.py` | Contrôle convergence spin-up OPL C1 $\rightarrow$ C2 | Restarts 201701 C1 & C2 | Bilan stock BSFSTO ($\Delta S = 0.132\%$) |
| **Ctrl** | `scripts/check_spinup_criterion_da_nocdf.py` | Contrôle convergence spin-up NoCDF C1 $\rightarrow$ C2 | Restarts 201701 C1 & C2 | Bilan stock BSFSTO ($\Delta S = 0.065\%$) |
| **4** | `scripts/extract_streamflow.py` | **Extracteur unifié des débits** aux stations | 1 827 NetCDF LIS_HIST par exp + table stations | Caches CSV journaliers dans `output/[EXP]/` |
| **5** | `scripts/evaluate_sebou_bouregreg.py` | **Évaluateur scientifique canonique** | 3 caches débits + observations ABH + LDT HyMAP | 3 tables validées + 3 figures ciblées Sebou–Bouregreg |
| **Ctrl** | `scripts/plot_streamflow_coverage.py` | Générateur frise de disponibilité ABH | `data/streamflow_data/` | `plots/technical/parameters/streamflow_coverage_timeline.png` |

---

## 3. Commandes de Reproduction

### A. Reproduction instantanée à partir des caches existants (Recommandé)
Les séries journalières extraites étant déjà vérifiées et en cache, l'évaluation complète se lance directement sans relire les NetCDF :

```bash
# Activer l'environnement Python
source activate postproc_env

# Exécuter l'évaluation canonique
python experiments/NorthMor/routing/scripts/evaluate_sebou_bouregreg.py
```
*Temps d'exécution : ~15 secondes.*
*Produit : 3 tables dans `plots/sebou_bouregreg/tables/` et 3 figures dans `plots/sebou_bouregreg/figures/streamflow/`.*

### B. Extraction des débits depuis les NetCDF LIS_HIST
Pour régénérer les caches à partir des sorties NetCDF complètes :

```bash
# Vérifier l'état des caches sans ré-extraction
python experiments/NorthMor/routing/scripts/extract_streamflow.py

# Forcer l'extraction d'une expérience spécifique (ex. OPL, nocdf ou cdf)
python experiments/NorthMor/routing/scripts/extract_streamflow.py --experiment opl --force

# Forcer la ré-extraction complète des 3 expériences (5 481 NetCDF)
python experiments/NorthMor/routing/scripts/extract_streamflow.py --experiment all --force
```

---

## 4. Emplacement des Livrables Scientifiques

- **Tables canoniques (`plots/sebou_bouregreg/tables/`)** :
  1. `tableau_synthese_11stations_sebou_bouregreg.csv` : Métriques complètes KGE, NSE, r, PBIAS sur les 11 stations.
  2. `tableau_diagnostic_5stations.csv` : Synthèse ciblée sur les 5 stations clés (Sidi Jabeur, Lalla Chafia, Ain Timedrine, Dar El Hamra, Pont de Mdez).
  3. `tableau_apports_noahmp_2018.csv` : Bilans volumiques amont délimités $Q_s$ et $Q_{sb}$ en $\text{hm}^3$ pour 2018.
- **Figures scientifiques (`plots/sebou_bouregreg/figures/streamflow/`)** :
  1. `fig_detaillee_2018_b_s_jabeur.png` : Hydrogramme journalier 2018 à Sidi Jabeur (Grou, Bouregreg) — crue linéaire + étiage log.
  2. `fig_detaillee_2018_b_l_chafia.png` : Hydrogramme journalier 2018 à Lalla Chafia (Bouregreg moyen) — crue linéaire + étiage log.
  3. `fig_comparative_mensuelle_sebou.png` : Hydrogrammes mensuels synchronisés 2016–2020 sur le Haut Sebou.
