# Matrice d'Expériences 2016 (Core SMAP Experiments)

Ce répertoire (`matrix_2016`) est dédié à la validation fondamentale de la configuration du modèle LIS/Noah-MP pour le domaine du Nord du Maroc, en se limitant strictement à l'année **2016**. 

Suite à une simplification, la matrice se concentre exclusivement sur le **cœur du problème** : comprendre l'impact de l'assimilation SMAP (sans irrigation, sans LAI) et analyser la propagation vers les variables hydrologiques (runoff, baseflow, streamflow).

## Les 5 Expériences Fondamentales

1. **OPL_noirr_2016** : 
   * **Rôle** : Open-loop (baseline). Aucune assimilation, aucune irrigation. Sert de référence absolue pour évaluer l'apport de l'assimilation.
   * *Génère également la climatologie de surface nécessaire pour le calcul du CDF matching.*

2. **DA_nocdf_noirr_2016** : 
   * **Rôle** : Assimilation directe (EnKF) des observations SMAP sans correction de biais (pas de CDF matching). Permet de tester si l'assimilation brute crée des chocs ou améliore l'état.

3. **DA_cdf_noirr_2016** : 
   * **Rôle** : Assimilation SMAP (EnKF) avec application préalable du CDF matching pour corriger les biais systématiques entre le modèle et l'observation.

4. **DA_SMAP_inflation_sensitivity_2016** : 
   * **Rôle** : Expérience de sensibilité sur les paramètres EnKF. Évalue l'impact de la variation de l'inflation de l'ensemble sur la robustesse du filtre et sur la propagation vers les flux intégrés.

5. **DA_SMAP_obs_error_sensitivity_2016** : 
   * **Rôle** : Expérience de sensibilité. Vérifie comment la modification de l'erreur d'observation spécifiée pour SMAP affecte le poids donné aux observations lors de la mise à jour des états.

## Résumé de la chaine d'exécution (Ordre strict)
1. **Générer OPL** : Lancer `chain_da.py` dans `OPL_noirr_2016` (déjà lancé).
2. **Générer CDF** : Lancer `sbatch run_cdf_noirr.sh` dans `CDF/` (déjà complété via `ldt`).
3. **Lancer DA** : Soumettre `DA_nocdf_noirr_2016` et `DA_cdf_noirr_2016` (en cours de fonctionnement).
4. **Sensibilité** : Une fois les bases établies, lancer `DA_SMAP_inflation_sensitivity_2016` et `DA_SMAP_obs_error_sensitivity_2016`.
