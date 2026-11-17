# -*- coding: utf-8 -*-
import os

readme_path = 'experiments/NorthMor/opl_hydrology_sensitivity/README.md'

section10 = """

---

## 10. Extension Multi-Stations ABH et Diagnostics Scientifiques (2018)

### 10.1 Cadre et Objectifs
Cette extension élargit l'évaluation des 4 formulations physiques OPL (`OL_R1_SIMGM`, `OL_R2_SIMTOP`, `OL_R3_SCHAAKE96`, `OL_R4_BATS`) à l'ensemble des stations hydrométriques ABH disponibles et exploitables dans le domaine `NorthMor`, tout en répondant point par point aux observations scientifiques formulées par Augusto Getirana.

### 10.2 Inventaire et Classification des Stations (2018)
Sur 20 stations hydrométriques recensées dans les archives historiques :
- **7 stations retenues pour l'évaluation principale (Qualité A/B) :**
  - Bassin du Bouregreg : `b_l_chafia` (Lalla Chafia, 3 333 km², 365 j obs), `b_s_jabeur` (Sidi Jabeur, 3 131 km², 365 j obs).
  - Bassin du Sebou (Moyen Sebou & Moyen Atlas) : `ain_timedrine` (Ain Timedrine, 3 438 km², 12 mois obs), `azzaba` (Azzaba, 3 798 km², 12 mois obs), `pont_de_mdez` (Pont de Mdez, 2 830 km², 12 mois obs), `ait_khabbach` (Ait Khabbach, 1 129 km², 12 mois obs), `dar_el_hamra` (Dar El Hamra, 1 035 km², 12 mois obs).
- **3 stations exploitables avec réserves (Qualité C) :**
  - `b_a_loudah` (Ain Loudah, 335 km²) et `b_s_cherif` (S.M. Cherif, 375 km²) : séries observées 2018 strictement dupliquées dans la base ABH d'origine (même débit au jour le jour) ; bassin amont de petite taille à forte pente.
  - `pont_ait_aissa` (Pont Ait Aissa, 252 km²) : écart de superficie D8 vs référence (+23.8%) et contrôle amont par le barrage Bab Louta.
- **10 stations exclues :**
  - 2 stations sans coordonnées géographiques valides (`b_a_ziar`, `b_r_fathia`).
  - 8 stations sans aucune observation en 2018 (`adamna`, `el_mers`, `m_jemaa`, `mechra_bel_ksiri`, `oued_amreuss`, `sidi_ammar`, `taza_amont`, `taza_aval`).

Fichier de référence : `postproc/tables/station_inventory_2018.csv` et `station_inventory_2018.md`.

### 10.3 Vérification de la Conservation et du Remapping
- **Cohérence spatiale des apports :** L'intégration des flux de ruissellement journaliers $Q_s$ et de drainage $Q_{sb}$ sur les masques de bassins versants amont D8 montre une stricte conservation de masse entre les sorties brutes Noah-MP ($0.05^\\circ$) et la grille HyMAP-2 ($180 \\times 120$) : ratio $V_{\\text{remap}} / V_{\\text{raw}} = 0.9954 \\text{ à } 0.9976$ (écart $< 0.4\\%$ attribuable au découpage de bordure des mailles).
- **Partitionnement $Q_s / Q_{sb}$ :**
  - En hiver/printemps, SIMTOP et BATS activent le ruissellement superficiel $Q_s$ de manière contrastée : BATS génère un ruissellement hortonien/dunien vigoureux ($Q_s$ annuel de 111 mm à Lalla Chafia, 46 mm à Sidi Jabeur), tandis que SIMGM reste quasi exclusivement dominé par $Q_{sb}$ ($Q_s < 2.5\\text{ mm/an}$).
  - En été (juin–septembre), $Q_s \\equiv 0\\text{ mm}$ pour tous les schémas ; la totalité du débit simulé provient du drainage de nappe/subsurface $Q_{sb}$.

### 10.4 Synthèse des Performances Multi-Stations
1. **Lalla Chafia (Bouregreg humide pérenne) :**
   - **SIMTOP est le modèle optimal** : $\\text{NSE}_{\\text{daily}} = 0.59$, $\\text{KGE}_{\\text{daily}} = 0.59$, $\\text{NSE}_{\\text{monthly}} = 0.90$, $\\text{KGE}_{\\text{monthly}} = 0.82$, $\\text{PBIAS} = +16.9\\%$.
   - BATS surestime les volumes de crue ($\\text{PBIAS} = +65.6\\%$, $\\text{NSE}_{\\text{daily}} = -0.19$).
2. **Sidi Jabeur (Oued Grou semi-aride intermittent) :**
   - **BATS est le modèle optimal** : $\\text{NSE}_{\\text{daily}} = 0.42$, $\\text{KGE}_{\\text{daily}} = 0.48$, $\\text{NSE}_{\\text{monthly}} = 0.79$, $\\text{KGE}_{\\text{monthly}} = 0.83$, $\\text{PBIAS} = -10.4\\%$.
   - SIMGM échoue par sous-estimation critique des crues ($\\text{PBIAS} = -64.0\\%$, $\\text{NSE}_{\\text{daily}} = 0.05$).
3. **Moyen Sebou & Moyen Atlas (`ain_timedrine`, `dar_el_hamra`, `pont_de_mdez`, `azzaba`) :**
   - SIMGM souffre d'un déficit volumique massif ($\\text{PBIAS} = -75\\% \\text{ à } -86\\%$, $\\text{NSE} < 0$).
   - SIMTOP réduit substantiellement ce biais ($\\text{PBIAS} \\approx -47\\% \\text{ à } -70\\%$ ; $\\text{KGE} > 0$).
   - BATS obtient les scores les plus élevés sur le Haut Sebou : $\\text{NSE}_{\\text{monthly}} = +0.33$ à Ain Timedrine, $+0.26$ à Dar El Hamra, $+0.01$ à Pont de Mdez, avec $r > 0.90$.
   - Exception à `ait_khabbach` (Guigou) : le fort pompage agricole dans la plaine du Guigou et l'infiltration karstique rendent le débit observé très faible (0.57 m³/s en moyenne), conduisant BATS à une surestimation volumique.

### 10.5 Réponses Point par Point aux Remarques d'Augusto Getirana
1. **Risque de mélange de simulations et chutes brutales du débit à zéro :**
   - *Vérification factuelle :* Les hydrogrammes journaliers continus des 4 simulations 2017–2018 ne présentent **aucune discontinuité technique ni aucune chute brutale à zéro** aux transitions mensuelles ou annuelles (vérifié sur Nov 2017 – Jan 2018 et Nov 2018 – Jan 2019, voir Figure F5).
   - *Origine de l'anomalie historique :* L'artefact observé sur les anciens tracés OPL provenait d'une concaténation de sorties de tests mensuels isolés avec décalage d'indexation journalière ($t+1$ jour). Ce problème est totalement éliminé par la chaîne de production automatisée.
2. **Rôle du drainage $Q_{sb}$ dans la surestimation des étiages :**
   - *Confirmation :* En été, $Q_s = 0$ et le débit simulé est intégralement constitué de $Q_{sb}$.
   - SIMGM et SIMTOP produisent un $Q_{sb}$ estival excessif (3 à 16 mm/saison), maintenant un débit artificiel de 2.6 à 6.9 m³/s.
   - Schaake96 draine plus vigoureusement au printemps, ce qui assèche la colonne de sol et réduit $Q_{sb}$ estival à $< 1\\text{ mm}$ dans le Sebou, divisant par 2 à 4 le débit estival simulé.
3. **Représentation des précipitations et forçage :**
   - Les précipitations GPM IMERG V07B captent fidèlement la chronologie des grandes perturbations atlantiques (crues de mars, avril et novembre 2018).
   - La comparaison avec MSWEP v2.8 et ERA5-Land confirme que la sous-estimation des crues sous SIMGM ne provient pas d'un manque de pluie, mais d'une absorption excessive dans la colonne de sol en l'absence de ruissellement rapide.
4. **Problème de l'intermittence des oueds :**
   - Aucun schéma physique 1D de surface ne peut reproduire les 47 à 60 jours de tarissement complet observés à Sidi Jabeur car HyMAP-2 ne modélise pas les pertes par infiltration dans le lit vif de l'oued (*transmission losses*) ni les prélèvements alluviaux.

### 10.6 Livrables Générés
- **Figures Multi-Stations (dans `postproc/multistation/figures/` et `postproc/figures/`) :**
  - `f1a_hydrographs_bouregreg_daily_2018.png` : Hydrogrammes journaliers du Bouregreg (4 panneaux).
  - `f1b_hydrographs_sebou_monthly_2018.png` : Hydrogrammes mensuels du Sebou (6 panneaux).
  - `f2_precip_and_flood_response_2018.png` : Précipitations et réponses en crue (événements de mars et nov. 2018).
  - `f3_daily_qs_qsb_hydrographs_2018.png` : Séries journalières $P, Q_s, Q_{sb}$ et débits routés vs observés.
  - `f4_lowflow_diagnostic_summer2018.png` : Diagnostic d'étiage estival (seuils $\\le 0.1$ et $\\le 0.5\\text{ m}^3\\text{/s}$, zéros, $Q_{50}$).
  - `f5_discontinuity_and_continuity_check.png` : Contrôle des raccords et continuité temporelle HyMAP-2.
  - `f6_multistation_synthesis_performance.png` : Synthèse globale comparative KGE, $\\Delta\\text{KGE}$, PBIAS et $r$.
- **Tables de synthèse :**
  - `postproc/tables/station_inventory_2018.csv` & `.md`
  - `postproc/tables/table_multistation_metrics_2018.csv` & `.md`
  - `postproc/tables/table_multistation_lowflows_2018.csv`
  - `postproc/tables/table_multistation_floods_2018.csv`
  - `postproc/tables/catchment_fluxes_multistation_summary_2018.csv` & `.md`
"""

with open(readme_path, 'a', encoding='utf-8') as f:
    f.write(section10)

print("Section 10 successfully added via clean python script.")
