# Sprint 2.2: Final Hydrological Response Cleanup

## A. Corrections textuelles effectuées
- **Formulation DJF (Runoff)** : La phrase indiquant que DA-NoCDF "depresses runoff generation" a été supprimée et remplacée par une explication plus précise : "During DJF, DA-NoCDF reduces SSM, RZSM and ET relative to OPL, while increasing pre-routing total runoff mainly through the baseflow-like component."
- **Formulation JJA** : La description de l'augmentation d'ET et de la faible réponse du runoff a été affinée avec la formulation requise.
- **Water Balance** : L'expression "confirming physical interpretability" a été retirée au profit de "supports a first-order interpretation... but does not demonstrate water-balance closure because storage changes are not explicitly included."
- **Atténuation CDF** : L'expression "neutralizing the hydrological fluxes back toward OPL" a été remplacée par "strongly attenuating runoff and baseflow responses relative to DA-NoCDF."
- **Valeur Diagnostique** : L'expression "obscures the physical diagnostic value" a été remplacée par "reduces the raw model–SMAP mismatch signal and therefore limits the diagnostic sensitivity of the hydrological response."

## B. Vérification de `n_grid_cells`
L'analyse de la matrice de données a confirmé la présence de **16030 cellules uniques** pour le masque terrestre (couples `north_south` / `east_west`).
- La colonne `n_pixels` a été rigoureusement renommée en `n_samples`.
- Les métadonnées explicites `n_unique_grid_cells = 16030`, `n_months = 60/15`, et `aggregation_method = spatial mean map` ont été ajoutées dans le fichier récapitulatif `q1_hydrological_response_summary.csv` pour éviter toute ambiguïté sur l'échantillonnage spatial.

## C. Nouvelles figures produites
Les figures "3x6" surchargées ont été divisées en graphiques 3x3 "paper-ready". La représentation a migré du `scatterplot` vers `imshow` (matrice 2D native reconstruite via `north_south`/`east_west`) pour éliminer les artefacts visuels (stries horizontales) et obtenir un fond blanc propre pour les océans. 
- *States + ET* : `q1_fig_hydrological_response_states_ET_annual_2016_2020.png` (ainsi que DJF et JJA).
- *Runoff Partitioning* : `q1_fig_hydrological_response_runoff_annual_2016_2020.png` (ainsi que DJF et JJA).

## D. Message scientifique final (Section 3.4/3.5)
1. **Dynamic Response (DA-NoCDF)**: DA-NoCDF yields a strong diagnostic response, modifying SSM and RZSM states that subsequently alter ET and pre-routing runoff distributions.
2. **Seasonal Contrasts**: During DJF, DA-NoCDF decreases SSM/RZSM/ET while redistributing water to baseflow; during JJA, it induces a slight surface wetting and markedly increases ET.
3. **Conservative Behavior (DA-CDF)**: CDF matching strongly attenuates the runoff and baseflow responses, reducing the raw SMAP mismatch signal and limiting hydrological diagnostic sensitivity.
4. **Baseflow Dominance**: Pre-routing runoff responses are heavily dominated by the slow baseflow component, acting as a deep buffer for increments.
5. **Interpretability**: A first-order flux-only balance verifies that DA-induced flux anomalies are consistent with unmodeled SMAP water increments, although exact mass closure remains impossible without explicit temporal storage tracking.

## E. Figures recommandées pour le Main Paper
- `q1_fig_hydrological_response_states_ET_annual_2016_2020.png`
- `q1_fig_hydrological_response_states_ET_DJF_2016_2020.png`
- `q1_fig_hydrological_response_states_ET_JJA_2016_2020.png`

## F. Figures à mettre en Supplementary
- `q1_fig_hydrological_response_runoff_annual_2016_2020.png`
- `q1_fig_hydrological_response_runoff_DJF_2016_2020.png`
- `q1_fig_hydrological_response_runoff_JJA_2016_2020.png`
- `q1_fig_first_order_water_balance.png`

## G. Limites restantes
L'absence d'un module de routage (HyMAP) impose de traiter ces résultats comme des diagnostics "pre-routing". Le baseflow ne peut pas être mathématiquement comparé aux débits fluviaux mesurés. Le bilan massique parfait reste incalculable sans `dS`.
