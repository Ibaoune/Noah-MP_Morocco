# Rapport de Validation LOT 2A.1

## Évaluation des Composants Core et Audit

Les composants du registre scientifique ont été testés unitairement via `python -m unittest discover tests` puis éprouvés en lecture seule sur les expériences réelles de 2016.

### Matrice d'Implémentation et Validation Globale

| Composant | Implementation status | Unit test status | Real-data status | Validation level | Limites |
| --------- | --------------------- | ---------------- | ---------------- | ---------------- | ------- |
| `capabilities.py` | IMPLEMENTED | PASSED | N/A | **VALIDATED** | Aucune |
| `diagnostic_registry.py` | IMPLEMENTED | PASSED | N/A | **VALIDATED** | Aucune |
| `provenance.py` | IMPLEMENTED | PASSED | N/A | **VALIDATED** | Aucune |
| `quality_control.py` | IMPLEMENTED | PASSED | PASSED | **REAL_DATA_TESTED** | Dépendance temporelle OOM |
| `water_balance_variable_audit`| IMPLEMENTED | PASSED | PASSED | **REAL_DATA_TESTED** | Risque GWS/TWS double compte |
| `water_flux_conversion` | PLANNED | N/A | N/A | **NOT_IMPLEMENTED** | À développer |
| `storage_change_calculation` | PLANNED | N/A | N/A | **NOT_IMPLEMENTED** | `_tavg` dS/dt |
| `assimilation_water_conversion` | PLANNED | N/A | N/A | **NOT_IMPLEMENTED** | Unité et signes incrément |
| `water_balance_closure` | PLANNED | N/A | N/A | **NOT_IMPLEMENTED** | Bilan partiel |

## Matrice Exacte de Couverture des Tests Unitaires

Tous les tests suivants sont implémentés dans `tests/core/test_capabilities.py`, `tests/core/test_diagnostic_registry.py`, `tests/quality_control/test_quality_control.py` et `tests/water_balance/test_variable_audit.py` et s'exécutent avec succès :

| Exigence | Test Correspondant | Statut |
| -------- | ------------------ | ------ |
| Transition des statuts | `TestCapabilities.test_status_transitions` | PASSED |
| Diagnostic absent | `TestRegistry.test_missing_diagnostic` | PASSED |
| Diagnostic dupliqué | `TestRegistry.test_duplicate_diagnostic` | PASSED |
| Sérialisation du manifeste | `TestProvenance.test_manifest_serialization` | PASSED |
| Variable absente | `TestVariableAudit.test_missing_vars` | PASSED |
| Unité inattendue | `TestQualityControl.test_unexpected_unit` | PASSED |
| Coordonnée temp absente | `TestQualityControl.test_missing_time_coord` | PASSED |
| Année bissextile complète | `TestQualityControl.test_leap_year_complete` | PASSED |
| Jour manquant | `TestQualityControl.test_missing_day` | PASSED |
| Jour dupliqué | `TestQualityControl.test_duplicate_day` | PASSED |
| Grilles incompatibles | `TestQualityControl.test_incompatible_grid` | PASSED |
| TWS et GWS présents | `TestVariableAudit.test_tws_gws_together` | PASSED |
| Risque de double comptage | `TestVariableAudit.test_double_count_risk` | PASSED |
| Incrément absent | `TestVariableAudit.test_increment_absent` | PASSED |

## Réponses aux Questions Clés

**Les trois expériences contiennent-elles 366 jours ? (Couverture temporelle exacte)**
Oui, les fichiers réels montrent 366 fichiers quotidiens par expérience (de `2016-01-01` à `2016-12-31`), sans jour manquant ni dupliqué, couvrant le 29 février, avec une parfaite concordance nom de fichier / dimension temporelle interne.

**Leurs grilles sont-elles identiques ?**
Oui, les dimensions et résolutions sont identiques (latitude Nord-Sud, longitude Ouest-Est) pour les trois.

**Les unités sont-elles utilisables ?**
Oui, les flux sont en `kg m-2 s-1` et stockages en `m3/m3` ou `mm`.

**Statut détaillé des sous-composants du bilan (FULL, PARTIAL ou NOT_COMPUTABLE) :**
Le bilan global reste **PARTIAL**. Seule l'audit de variable a été testée sur données réelles (`REAL_DATA_TESTED`). Les modules de conversion de flux, de $dS/dt$, de conversion d'assimilation et de fermeture n'existent pas encore et sont à l'état `PLANNED`/`NOT_IMPLEMENTED`.

**Quelle stratégie d’incrément est disponible pour chaque DA ?**
L'audit a permis de recenser, pour les deux expériences d'assimilation (`DA_smap_nocdf_noirr_2016`, `DA_smap_cdf_noirr_2016`), la variable d'incrément `SoilMoist_inc`.
La stratégie d'assimilation détectée est **EXPLICIT_INCREMENT** au niveau de validation : **UNITS_CONFIRMED**. La convention de signe et la conversion en équivalent d'eau restent à faire.

**La comparaison réelle avec le snapshot de baseline :**
Un véritable script de non-régression a été exécuté comparant les tailles et hashes SHA256 des fichiers de sortie de la baseline à un snapshot (`baseline_outputs_snapshot.yaml`). L'intégralité des outputs, images PNG, métriques JSON, et fichiers de config correspondent à l'identique. Résultat : **PASSED_WITH_WARNINGS** (Le seul warning concerne la date de génération interne enregistrée dans le manifest lui-même, due aux scripts d'audit, ne modifiant aucune donnée scientifique).

**Problèmes ouverts restants :**
- Calcul de $dS/dt$ sur des variables `_tavg`.
- Clarification du risque de double comptage entre TWS et GWS.
- Extraction exacte de la convention de signe de `SoilMoist_inc`.
