# Test d'Audit : DA_nocdf_TEST_nowilt

* **But** : Tester l'effet du seuil de flétrissement du QC sur l'assimilation directe SMAP sans CDF (`DA_nocdf`).
* **Modification du code source** : Utilise le binaire `src/lisf_nowilt/lis/LIS`, dans lequel la condition `smobs(t) - smcwlt_obs(t) < 0.02` dans `noahmp401_qc_soilmobs.F90` a été commentée.
* **Période simulée** : Juillet–Août 2018 (2 mois terminés : `2018-07` et `2018-08`).
* **Membres d'ensemble** : 20 membres.
* **Statut** : Test terminé.
* **Note sur les chemins historiques** : Ce test a été exécuté dans l'ancien chemin `experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt` avant son reclassement dans `tests/`. Les scripts historiques dans `generated/` conservent leurs chemins d'origine pour préserver la reproductibilité brute.
* **Restarts** : Les liens symboliques dans `restarts/surf/` et `restarts/pert/` pointent de manière absolue et valide vers le run de production `DA_nocdf_noirr_2016_2020`.
