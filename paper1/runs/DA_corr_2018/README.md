# Simulation DA_corr_2018 — Assimilation SMAP Corrigée (2018)

- **Objectif :** Disposer d une assimilation EnKF SMAP NoCDF sans perturbation additive d état (State perturbation algorithm: "none"), sans recentrage de Ryu (Apply perturbation bias correction: 0), et sans filtre de flétrissement QC.
- **Diagnostics DA complets :** Activés (, , , ).
- **Période :** 2018-01-01 00:00 au 2019-01-01 00:00.
- **Condition Initiale :** Restart DA_nocdf_noirr au 2018-01-01 ( et ).
- **Binaire utilisé :**  [ERR] LIS config file, lis.config, does not exist.
  Also, if the LIS config file you wanted to run with
   is not 'lis.config', please put an '-f' or '--file'
   in front of your intended LIS config file.
  This LIS run is stopping here ....
- **Contrôle de validité post-EnKF :** Vérifié dans le code : l assimilation EnKF applique systématiquement  (écrêtage et recentrage post-analyse) indépendamment de l algorithme de perturbation d état.
- **Configuration :** .
- **Répertoire d exécution :** .
