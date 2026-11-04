# Expérience Prévue : DA_anomaly_noirr_2016_2020

* **But** : Assimilation SMAP par mise à l'échelle d'anomalies (méthode Kwon et al., 2022) pour préserver le signal d'irrigation.
* **Configuration** : `config/experiment.ini`, `scripts/chain_da.py`, `templates/lis_da.config.template`.
* **Statut** : **PRÉVUE / EN ATTENTE**.
* **AVERTISSEMENT CRITIQUE AVANT TOUT LANCEMENT** :
  Le fichier template actuel (`templates/lis_da.config.template`) pointe vers l'ancien chemin de CDF archivé :
  `./experiments/NorthMor/matrix_2016/CDF/OUTPUT_noirr/smap_cdf.nc`
  Ce template **doit impérativement être corrigé** pour pointer vers la CDF NorthMor valide (`./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_...`) avant toute exécution de la chaîne.
