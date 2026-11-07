# Index Général des Figures et Résultats HyMAP — Noah-MP Maroc

Ce répertoire regroupe les figures, diagnostics et tables d'évaluation issus de la chaîne de routage hydrodynamique HyMAP couplée à Noah-MP pour la période quinquennale 2016–2020.

L'arborescence est strictement structurée en deux catégories maintenues.

---

## 1. Figures Scientifiques Actuelles (`sebou_bouregreg/figures/`)

Ces figures constituent les **résultats scientifiques validés actuels**, comparant les trois simulations (OPL, DA-NoCDF, DA-CDF) et les observations ABH sur les bassins cibles du Sebou et du Bouregreg :

| Fichier canonique | Description scientifique | Expériences comparées |
| :--- | :--- | :---: |
| [`sebou_bouregreg/figures/streamflow/fig_detaillee_2018_b_s_jabeur.png`](sebou_bouregreg/figures/streamflow/fig_detaillee_2018_b_s_jabeur.png) | Hydrogramme journalier détaillé à Sidi Jabeur (Grou, Bouregreg) : pic de crue linéaire + étiage estival log avec zéros observés stricts. | OPL / NoCDF / CDF / Obs (2018) |
| [`sebou_bouregreg/figures/streamflow/fig_detaillee_2018_b_l_chafia.png`](sebou_bouregreg/figures/streamflow/fig_detaillee_2018_b_l_chafia.png) | Hydrogramme journalier détaillé à Lalla Chafia (Bouregreg moyen) : pic de crue linéaire + étiage estival log. | OPL / NoCDF / CDF / Obs (2018) |
| [`sebou_bouregreg/figures/streamflow/fig_comparative_mensuelle_sebou.png`](sebou_bouregreg/figures/streamflow/fig_comparative_mensuelle_sebou.png) | Hydrogrammes mensuels synchronisés sur les 3 stations du Haut Sebou (Ain Timedrine, Dar El Hamra, Pont de Mdez) avec métriques intégrées. | OPL / NoCDF / CDF / Obs (2016–2020) |

*Toutes les tables associées sont documentées dans [`sebou_bouregreg/README.md`](sebou_bouregreg/README.md).*

---

## 2. Diagnostics Techniques et Contrôles (`technical/`)

Ces éléments assurent le contrôle de la qualité numérique et le diagnostic interne du modèle :

| Sous-dossier | Fichier | Description & Statut |
| :--- | :--- | :--- |
| [`technical/parameters/`](technical/parameters/) | [`streamflow_coverage_timeline.png`](technical/parameters/streamflow_coverage_timeline.png) | Frise chronologique de disponibilité des données de jaugeage ABH (stations journalières vs mensuelles). Reproductible via `scripts/plot_streamflow_coverage.py`. |
| [`technical/spinup/`](technical/spinup/) | [`README.md`](technical/spinup/README.md) | Synthèse numérique de la convergence du spin-up C1 -> C2 (< 1.0 %) pour OPL (0.132 %), DA-NoCDF (0.065 %) et DA-CDF (0.076 %). |

---

## 3. Figures Prévues, Non Encore Produites

Les figures suivantes complèteront l'analyse lors de la phase finale de rédaction :

1. **Figure F1 (`sebou_bouregreg/figures/domain/`)** : Carte du domaine recadrée sur le Sebou et le Bouregreg (11 stations), avec tracé des bassins amont délimités.
2. **Figure F2 (`sebou_bouregreg/figures/runoff/`)** : Diagramme en barres empilées décomposant ruissellement de surface ($Q_s$) et drainage souterrain ($Q_{sb}$) pour OPL, NoCDF et CDF avec découpage saisonnier méditerranéen (Octobre–Mars vs Avril–Septembre).
3. **Figure F3 tripartite (`sebou_bouregreg/figures/streamflow/`)** : Courbes des débits classés (FDC) comparant OPL, DA-NoCDF et DA-CDF aux stations du Bouregreg.
4. **Figure F4 (`sebou_bouregreg/figures/performance/`)** : Synthèse graphique comparative des métriques KGE, NSE, r, PBIAS par station.

---

## 4. Politique Git pour `routing/plots/`

* Le répertoire `experiments/NorthMor/routing/plots/` est ignoré par défaut dans le `.gitignore` (`.gitignore:37`).
* Les figures PNG volumineuses et les tables CSV d'évaluation restent non versionnées sur Git afin de préserver la légèreté du dépôt.
* Seuls les fichiers de documentation Markdown (`README.md`, `sebou_bouregreg/README.md`, `technical/spinup/README.md`) sont suivis dans Git.
