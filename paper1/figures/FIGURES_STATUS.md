# Statut et Inventaire des Figures du Papier 1 (Étape 6)

*Date de génération : 2026-11-22*
*Résolution graphique : 200 dpi*
*Charte graphique : palettes accessibles aux personnes daltoniennes (Okabe-Ito / Colorblind-friendly)*
*Couleurs fixes d'expériences : OL (#1f77b4), OL-DAIC (#56B4E9), ENS-OL (#009E73), DA-NoCDF (#D55E00), DA-CDF (#CC79A7), DA-NoCDF-noWQC (#E69F00), ENS-corr (#000000), DA-corr (#882255)*

---

## 1. Synthèse Globale des Figures

| Figure | Titre / Contenu | Script | Statut PNG | Statut CSV Données | Remarques / Données Manquantes |
|---|---|---|:---:|:---:|---|
| **Fig. 2** | Fraction des retrievals rejetés par le filtre de flétrissement (2016–2020) | `paper1/scripts/fig_02.py` | Complet (`358 Ko`) | Complet (`fig_02_data.csv`) | (a) MAM, (b) JJA, (c) Texture DA-NoCDF vs DA-CDF |
| **Fig. 3** | Effet de sélection du QC de flétrissement | `paper1/scripts/fig_03.py` | Complet (`329 Ko`) | Complet (`fig_03_data.csv`) | (a) écart accepted vs uncensored, (b) ΔJJA θ1 par classe de censure (IRRIGFRAC=0) |
| **Fig. 4** | Dry-downs de printemps (MAM) : SMAP uncensored vs Noah-MP OL | `paper1/scripts/fig_04.py` | Complet (`312 Ko`) | Complet (`fig_04_data.csv`) | (a) τ par texture, (b) P5 vs SMCWLT, (c) τ vs % argile (pentes +4.40 vs -18.38) |
| **Fig. 5** | Changements mensuels DA − OL 2016–2020 (DA-NoCDF, DA-CDF) | `paper1/scripts/fig_05.py` | Complet (`496 Ko`) | Complet (`fig_05_data.csv`) | (a) Δθ 4 couches, (b) ΔET, ΔQs, ΔQsb, (c) Incréments vs Δflux |
| **Fig. 6** | Effet du filtre de flétrissement en 2018 | `paper1/scripts/fig_06.py` | Complet (`290 Ko`) | Complet (`fig_06_data.csv`) | (a) Obs acceptées par mois, (b) ΔET annuel par texture, (c) Carte JJA Δθ1 |
| **Fig. 7** | Bilan d'eau interne et mécanismes E6 | `paper1/scripts/fig_07.py` | Complet (`664 Ko`) | Complet (`fig_07_data.csv`) | (a) Résidu mensuel 2018 & incréments, (b) ET mensuelle, (c) Tests mars 2018, (d) Décomposition code E6 (Step 2). **Panneau (e) 2018 vs 2017 omis : runs 2017 toujours en cours d'exécution sur le cluster.** |
| **Fig. 8** | Évaluation de l'ET contre GLEAM v4.3a et WaPOR v3 | `paper1/scripts/fig_08.py` | Complet (`454 Ko`) | Complet (`fig_08_data.csv`) | (a1-a3) Cycles mensuels Sebou, Bouregreg, Domaine, (b1) Δ\|biais\|, (b2) % mailles en amélioration |
| **Fig. 9** | Débits journaliers HyMAP-2 linres=0 (2018) | `paper1/scripts/fig_09.py` | Complet (`1.0 Mo`) | Complet (`fig_09_data.csv`) | (a) Lalla Chafia (échelle log), (b) Sidi Jabeur (échelle log), encadrés KGE/NIC et IC95 bootstrap |
| **Fig. S-a** | Diagnostic Lalla Chafia et invariance de routage linres | `paper1/scripts/fig_Sa.py` | Complet (`581 Ko`) | Complet (`fig_Sa_data.csv`) | (a) Carte ΔQsb DA-NoCDF − ENS_OPL avec top 20 mailles, (b) Comparaison linres=0 vs linres=1 |
| **Fig. S-b** | Diagnostic haute fréquence des incréments appliqués vs archivés | `paper1/scripts/fig_Sb.py` | Complet (`317 Ko`) | Complet (`fig_Sb_data.csv`) | (a) Scatter appliqué vs archivé 12 événements, (b) r et ratio par couche, (c) heures avec/sans perturbation |
| **Fig. S-c** | Innovations normalisées et spread de l'ensemble (2018) | `paper1/scripts/fig_Sc.py` | Complet (`394 Ko`) | Complet (`fig_Sc_data.csv`) | (a) Variance des innovations normalisées, (b) Biais normalisé, (c) Effondrement du spread sans perturbation d'état |

---

## 2. Inventaire Détaillé des Fichiers et Sommes de Contrôle

Tous les fichiers sont situés sous `paper1/figures/` :
- `fig_02.png` et `fig_02_data.csv`
- `fig_03.png` et `fig_03_data.csv`
- `fig_04.png` and `fig_04_data.csv`
- `fig_05.png` et `fig_05_data.csv`
- `fig_06.png` et `fig_06_data.csv`
- `fig_07.png` et `fig_07_data.csv`
- `fig_08.png` et `fig_08_data.csv`
- `fig_09.png` et `fig_09_data.csv`
- `fig_Sa.png` et `fig_Sa_data.csv`
- `fig_Sb.png` et `fig_Sb_data.csv`
- `fig_Sc.png` et `fig_Sc_data.csv`
