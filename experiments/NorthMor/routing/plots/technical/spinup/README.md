# Contrôles Numériques du Spin-up HyMAP (Cycles 1 & 2)

Pour chaque expérience de routage HyMAP, un protocole strict de spin-up en deux cycles annuels répétés (année 2016) a été appliqué afin d'équilibrer les réservoirs d'eau souterraine (`BSFSTO`), de surface (`RNFSTO`), de rivière (`RIVSTO`) et de plaine d'inondation (`FLDSTO`) :
- **Cycle 1 (C1)** : Démarrage à froid (`coldstart`), du 01/01/2016 au 01/01/2017.
- **Cycle 2 (C2)** : Démarrage à chaud (`restart`) à partir du restart produit par C1 au 01/01/2017, ré-exécution exacte de l'année 2016 avec les mêmes forçages de ruissellement.
- **Critère d'arrêt de spin-up** : Variation relative du stock d'eau souterraine (`BSFSTO`) entre la fin de C1 et la fin de C2 strictement inférieure à 1.0 % :
  $$\Delta_{\text{rel}} = \frac{|S_{\text{BSF}}^{(\text{C2})} - S_{\text{BSF}}^{(\text{C1})}|}{S_{\text{BSF}}^{(\text{C1})}} < 1.0\%$$

---

## 1. Données Validées Extraites Directement des Restarts LISF

*Les valeurs ci-dessous sont issues de la sommation des variables d'état NetCDF dans les fichiers `LIS_RST_HYMAP2_router_201701010000.d01.nc` de chaque cycle.*

| Expérience | Stock BSFSTO C1 ($\text{hm}^3$) | Stock BSFSTO C2 ($\text{hm}^3$) | $\Delta_{\text{rel}}$ BSFSTO | Stock Total C1 ($\text{hm}^3$) | Stock Total C2 ($\text{hm}^3$) | $\Delta_{\text{rel}}$ Stock Total | Statut |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **OPL corrigée** | 46.50 | 46.57 | **0.132 %** | 574.41 | 574.81 | 0.068 % | Conforme (< 1.0 %) |
| **DA-NoCDF** | 146.11 | 146.21 | **0.065 %** | 1 111.11 | 1 111.54 | 0.039 % | Conforme (< 1.0 %) |
| **DA-CDF corrigée** | 134.69 | 134.79 | **0.076 %** | 883.23 | 883.67 | 0.050 % | Conforme (< 1.0 %) |

---

## 2. Emplacement des Fichiers de Restart Utilisés pour la Production 2016–2020

Les fichiers de restart produits à l'issue de C2 constituent les conditions initiales physiques de la production quinquennale 2016–2020 :
- **OPL** : `output/OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`
- **DA-NoCDF** : `output/DA_nocdf_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`
- **DA-CDF** : `output/DA_cdf_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`
