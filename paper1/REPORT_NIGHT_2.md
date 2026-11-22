# Rapport d'Étape 2 — Mécanisme E6 : Build instrumenté et runs de mars 2018

**Date d'exécution :** 2026-11-22 03:57:58  
**Auteur :** Antigravity (mode autonome)  
**Branche Git :** `paper1-closure`  

---

## 1. Objectif de l'Étape 2

Quantifier rigoureusement et sans altérer la dynamique du modèle (**aucun calcul modifié**) le flux d'eau (en mm de colonne, équivalent eau liquide) ajouté ou retiré par chacune des étapes du mécanisme de perturbation d'état et de contrôle d'ensemble dans LIS :
1. `applyLSMPert` (`src/lisf_diag/lis/core/LIS_lsmMod.F90`) :
   - Eau ajoutée par la perturbation stochastique brute ($W_\text{pert}$).
   - Eau retirée ou ajoutée par le recentrage de Ryu ($W_\text{ryu}$).
2. `NoahMP401_qcsoilm` (`src/lisf_diag/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qcsoilm.F90`) :
   - Nombre de membres écrêtés en bas ($\theta_1 < 0.01$) et en haut ($\theta_1 > 0.55$).
   - Eau ajoutée ou retirée par l'écrêtage ($W_\text{qc}$).
3. `noahmp401_setsoilm` (`src/lisf_diag/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90`) :
   - Nombre de membres invalides ($N_\text{invalid}$).
   - Nombre de remplacements par le midrange ($N_\text{midrange}$) et eau ajoutée/retirée ($W_\text{mid}$).
   - Nombre d'itérations de recentrage ($N_\text{iter}$) et eau ajoutée/retirée par le recentrage itératif ($W_\text{rec}$).

---

## 2. Implémentation du Build `src/lisf_diag`

- **Arborescence source :** Copie conforme de `src/lisf_ryu/` dans `src/lisf_diag/`.
- **Module dédié :** `src/lisf_diag/lis/core/LIS_mech_diagMod.F90`
  - Gestion indépendante des unités de fichiers (`mech_unit`) via `LIS_getNextUnitNumber()`.
  - Écriture séparée par processus MPI (`mech_diag.<rank>.txt` dans le dossier `output/` de chaque run) pour éliminer tout verrouillage ou contention d'E/S.
  - Calcul direct en mm de colonne par couche ($\Delta z_1 = 0.1\text{ m}$, $\Delta z_2 = 0.3\text{ m}$, $\Delta z_3 = 0.6\text{ m}$, $\Delta z_4 = 1.0\text{ m}$) et en moyenne d'ensemble ($N_\text{ens} = 20$).
- **Points d'instrumentation :**
  - `LIS_lsmMod.F90:1085-1245` : capture de `stvar_up` (état pré-perturbation), `stvar_pert` (après perturbation brute), et `stvar` (après recentrage de Ryu éventuel).
  - `noahmp401_qcsoilm.F90:55-75` : capture de `soilm1` avant et après écrêtage `[smmin1, smmax1]`.
  - `noahmp401_setsoilm.F90:120-580` : capture des candidats `soilm(1..4)` et de l'état `smc(1..4)` après midrange et après recentrage itératif.
- **Binaire produit :**
  - Chemin : `src/lisf_diag/lis/LIS`
  - Taille : 16 675 184 octets
  - MD5 : `f64b09e8b489ee9bca313e99b1922737`

---

## 3. Test de Non-Régression (Règle Permanente 2)

- **Configuration de test :** `tests/ENS_STATE_201803_regr_diag/config/lis_ENS_STATE_201803_regr_diag.config`
- **Période :** 2 jours simulés (01–03/03/2018), 20 membres, `Apply perturbation bias correction: 1`.
- **Référence :** `tests/ENS_STATE_201803_regr` produit par `src/lisf_ryu/lis/LIS`.
- **Résultats de comparaison :**

| date | variable | max_abs_diff | mean_abs_diff | diff_zero |
| --- | --- | --- | --- | --- |
| 201803020000 | SoilMoist_tavg | 0.0 | 0.0 | True |
| 201803020000 | Evap_tavg | 0.0 | 0.0 | True |
| 201803020000 | Qs_tavg | 0.0 | 0.0 | True |
| 201803020000 | Qsb_tavg | 0.0 | 0.0 | True |
| 201803030000 | SoilMoist_tavg | 0.0 | 0.0 | True |
| 201803030000 | Evap_tavg | 0.0 | 0.0 | True |
| 201803030000 | Qs_tavg | 0.0 | 0.0 | True |
| 201803030000 | Qsb_tavg | 0.0 | 0.0 | True |

**Conclusion non-régression :** Écart strictement nul (`0.000000e+00`) sur toutes les variables (SMC, ET, Qs, Qsb) pour les deux jours simulés. Le binaire `lisf_diag` est 100% conforme.

---

## 4. Lancement des 4 Runs de Mars 2018

Les 4 configurations ont été préparées dans de nouveaux dossiers sous `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/` :

| Run | Job ID | Slurm Name | Option Ryu (`pert_bias_corr`) | Perturbations actives |
|:---|:---:|:---:|:---:|:---|
| `ENS_STATE_201803` | 8361362 | `DG_ST_18` | 1 | État (SM L1 std=0.004) |
| `ENS_STATE_201803_noRyu` | 8361363 | `DG_STnR_18` | 0 | État (SM L1 std=0.004) |
| `ENS_FORC_201803` | 8361364 | `DG_FC_18` | 1 | Forçage (SW std=0.3, Rain std=0.5) |
| `ENS_FORC_201803_noRyu` | 8361365 | `DG_FCnR_18` | 0 | Forçage (SW std=0.3, Rain std=0.5) |

Les 4 jobs tournent en parallèle sur Toubkal (32 coeurs chacun).

---

## 5. Bilan du Mécanisme (`paper1/tables/march2018_mechanism_budget.csv`)

Le script d'analyse `paper1/scripts/step2_compute_mechanism_budget.py` extrait et cumule les flux sur les 635 mailles du domaine :

| run | status | R_mm | minus_R_mm | w_pert_mm | w_ryu_mm | w_qc_mm | w_mid_mm | w_rec_mm | w_sum_mm | gap_minusR_minus_sum_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803 | COMPLETED | -8.26 | 8.26 | -0.0212 | -0.363 | 0.0033 | 0.1898 | -0.3144 | -0.5055 | 8.7655 |
| ENS_STATE_201803_noRyu | COMPLETED | -22.94 | 22.94 | -0.0048 | 0.0 | 0.0 | 0.4229 | -0.0001 | 0.418 | 22.522 |
| ENS_FORC_201803 | COMPLETED | -1.98 | 1.98 | 0.0 | 0.4745 | 0.002 | -0.7135 | -0.4392 | -0.6763 | 2.6563 |
| ENS_FORC_201803_noRyu | COMPLETED | 0.93 | -0.93 | 0.0 | 0.0 | 0.0 | -0.8898 | 0.0 | -0.8898 | -0.0402 |

### Tables détaillées produites :
- `paper1/tables/march2018_mechanism_budget.csv` : Bilan domaine complet par run.
- `paper1/tables/march2018_mechanism_by_theta1_class.csv` : Décomposition par classe de $\theta_1$ du membre 20 au 01-03 (< 0.05, 0.05–0.10, 0.10–0.20, > 0.20).
- `paper1/tables/march2018_mechanism_by_texture.csv` : Décomposition par type de texture de sol dominante USDA.
