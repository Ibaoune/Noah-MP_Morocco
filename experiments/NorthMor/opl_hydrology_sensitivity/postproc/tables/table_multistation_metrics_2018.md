# Évaluation des Performances Multi-Stations — Année 2018

Ce document présente la comparaison des 4 formulations OPL (SIMGM, SIMTOP, Schaake96, BATS) sur l'ensemble des 10 stations hydrométriques ABH exploitables.

## 1. Synthèse Globale des Performances par Station

| nom | bassin | pas_temps | formulation | NSE_daily | KGE_daily | delta_NSE_daily | NSE_monthly | KGE_monthly | PBIAS_monthly_pct | r_monthly |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ain Loudah | Bouregreg | journalier | SIMGM (Réf) | 0.15 | -0.02 | 0.00 | 0.18 | 0.11 | -41.20 | 0.86 |
| Ain Loudah | Bouregreg | journalier | SIMTOP | 0.26 | 0.21 | 0.11 | 0.42 | 0.53 | 42.80 | 0.80 |
| Ain Loudah | Bouregreg | journalier | Schaake96 | 0.14 | 0.43 | -0.02 | 0.83 | 0.80 | -5.20 | 0.92 |
| Ain Loudah | Bouregreg | journalier | BATS | -0.60 | -0.22 | -0.76 | -0.87 | -0.26 | 105.50 | 0.88 |
| Lalla Chafia | Bouregreg | journalier | SIMGM (Réf) | 0.17 | 0.08 | 0.00 | 0.17 | 0.12 | -18.20 | 0.45 |
| Lalla Chafia | Bouregreg | journalier | SIMTOP | 0.59 | 0.59 | 0.42 | 0.90 | 0.82 | 16.90 | 0.96 |
| Lalla Chafia | Bouregreg | journalier | Schaake96 | 0.24 | 0.57 | 0.07 | 0.81 | 0.87 | -8.20 | 0.91 |
| Lalla Chafia | Bouregreg | journalier | BATS | -0.19 | 0.14 | -0.36 | -0.15 | -0.03 | 65.60 | 0.95 |
| S.M. Cherif | Bouregreg | journalier | SIMGM (Réf) | 0.18 | 0.04 | 0.00 | 0.23 | 0.14 | -35.30 | 0.83 |
| S.M. Cherif | Bouregreg | journalier | SIMTOP | 0.23 | 0.21 | 0.05 | 0.36 | 0.48 | 47.90 | 0.80 |
| S.M. Cherif | Bouregreg | journalier | Schaake96 | -1.43 | 0.07 | -1.61 | 0.61 | 0.62 | 28.50 | 0.90 |
| S.M. Cherif | Bouregreg | journalier | BATS | -1.49 | -0.53 | -1.68 | -1.49 | -0.51 | 125.80 | 0.90 |
| Sidi Jabeur | Bouregreg | journalier | SIMGM (Réf) | 0.05 | -0.16 | 0.00 | -0.40 | -0.17 | -64.00 | 0.56 |
| Sidi Jabeur | Bouregreg | journalier | SIMTOP | 0.31 | 0.19 | 0.26 | 0.62 | 0.52 | -26.50 | 0.89 |
| Sidi Jabeur | Bouregreg | journalier | Schaake96 | 0.07 | 0.07 | 0.02 | 0.10 | 0.26 | -54.40 | 0.71 |
| Sidi Jabeur | Bouregreg | journalier | BATS | 0.42 | 0.48 | 0.37 | 0.79 | 0.83 | -10.40 | 0.90 |
| Ain Timedrine | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -2.01 | -0.21 | -79.80 | 0.77 |
| Ain Timedrine | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.56 | 0.18 | -56.80 | 0.85 |
| Ain Timedrine | Sebou | mensuel | Schaake96 | nan | nan | nan | -1.42 | -0.00 | -74.50 | 0.86 |
| Ain Timedrine | Sebou | mensuel | BATS | nan | nan | nan | 0.33 | 0.53 | -36.80 | 0.91 |
| Ait Khabbach | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -0.01 | -0.09 | -12.40 | 0.16 |
| Ait Khabbach | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.78 | -0.13 | 102.40 | 0.53 |
| Ait Khabbach | Sebou | mensuel | Schaake96 | nan | nan | nan | -0.93 | 0.14 | 43.30 | 0.28 |
| Ait Khabbach | Sebou | mensuel | BATS | nan | nan | nan | -6.28 | -1.44 | 220.00 | 0.34 |
| Azzaba | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -1.50 | -0.31 | -86.20 | 0.70 |
| Azzaba | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.68 | -0.04 | -70.40 | 0.93 |
| Azzaba | Sebou | mensuel | Schaake96 | nan | nan | nan | -1.18 | -0.17 | -81.90 | 0.75 |
| Azzaba | Sebou | mensuel | BATS | nan | nan | nan | -0.09 | 0.18 | -55.70 | 0.91 |
| Dar El Hamra | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -0.64 | -0.29 | -84.50 | 0.77 |
| Dar El Hamra | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.14 | -0.05 | -69.50 | 0.92 |
| Dar El Hamra | Sebou | mensuel | Schaake96 | nan | nan | nan | -0.46 | -0.20 | -83.70 | 0.96 |
| Dar El Hamra | Sebou | mensuel | BATS | nan | nan | nan | 0.26 | 0.16 | -54.10 | 0.95 |
| Pont Ait Aissa | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -2.51 | -0.56 | -80.20 | -0.06 |
| Pont Ait Aissa | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.55 | 0.18 | -49.60 | 0.66 |
| Pont Ait Aissa | Sebou | mensuel | Schaake96 | nan | nan | nan | -2.48 | -0.37 | -80.60 | 0.15 |
| Pont Ait Aissa | Sebou | mensuel | BATS | nan | nan | nan | -0.65 | 0.14 | -47.20 | 0.46 |
| Pont de Mdez | Sebou | mensuel | SIMGM (Réf) | nan | nan | nan | -2.21 | -0.29 | -75.80 | 0.39 |
| Pont de Mdez | Sebou | mensuel | SIMTOP | nan | nan | nan | -0.52 | 0.22 | -46.90 | 0.61 |
| Pont de Mdez | Sebou | mensuel | Schaake96 | nan | nan | nan | -1.77 | -0.06 | -69.50 | 0.41 |
| Pont de Mdez | Sebou | mensuel | BATS | nan | nan | nan | 0.01 | 0.50 | -25.70 | 0.59 |

---

## 2. Diagnostic d'Étiage Estival (Juin–Septembre 2018, 122 jours)

| nom | bassin | formulation | q_mean_obs_m3s | q_mean_sim_m3s | n_days_le_01_obs | n_days_le_01_sim | n_days_zero_obs | n_days_zero_sim | max_dry_spell_obs_days | max_dry_spell_sim_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ain Loudah | Bouregreg | SIMGM (Réf) | 0.03 | 0.30 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Ain Loudah | Bouregreg | SIMTOP | 0.03 | 0.28 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Ain Loudah | Bouregreg | Schaake96 | 0.03 | 0.12 | 121.00 | 31 | 0.00 | 0 | 0.00 | 0 |
| Ain Loudah | Bouregreg | BATS | 0.03 | 0.38 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Lalla Chafia | Bouregreg | SIMGM (Réf) | 0.73 | 6.88 | 0.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Lalla Chafia | Bouregreg | SIMTOP | 0.73 | 2.76 | 0.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Lalla Chafia | Bouregreg | Schaake96 | 0.73 | 1.84 | 0.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Lalla Chafia | Bouregreg | BATS | 0.73 | 3.71 | 0.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| S.M. Cherif | Bouregreg | SIMGM (Réf) | 0.03 | 0.35 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| S.M. Cherif | Bouregreg | SIMTOP | 0.03 | 0.28 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| S.M. Cherif | Bouregreg | Schaake96 | 0.03 | 0.15 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| S.M. Cherif | Bouregreg | BATS | 0.03 | 0.41 | 121.00 | 0 | 0.00 | 0 | 0.00 | 0 |
| Sidi Jabeur | Bouregreg | SIMGM (Réf) | 1.35 | 3.25 | 60.00 | 0 | 47.00 | 0 | 47.00 | 0 |
| Sidi Jabeur | Bouregreg | SIMTOP | 1.35 | 2.65 | 60.00 | 0 | 47.00 | 0 | 47.00 | 0 |
| Sidi Jabeur | Bouregreg | Schaake96 | 1.35 | 1.34 | 60.00 | 0 | 47.00 | 0 | 47.00 | 0 |
| Sidi Jabeur | Bouregreg | BATS | 1.35 | 3.23 | 60.00 | 0 | 47.00 | 0 | 47.00 | 0 |
| Ain Timedrine | Sebou | SIMGM (Réf) | nan | 1.86 | nan | 0 | nan | 0 | nan | 0 |
| Ain Timedrine | Sebou | SIMTOP | nan | 2.41 | nan | 0 | nan | 0 | nan | 0 |
| Ain Timedrine | Sebou | Schaake96 | nan | 1.05 | nan | 0 | nan | 0 | nan | 0 |
| Ain Timedrine | Sebou | BATS | nan | 3.22 | nan | 0 | nan | 0 | nan | 0 |
| Ait Khabbach | Sebou | SIMGM (Réf) | nan | 0.35 | nan | 0 | nan | 0 | nan | 0 |
| Ait Khabbach | Sebou | SIMTOP | nan | 0.53 | nan | 0 | nan | 0 | nan | 0 |
| Ait Khabbach | Sebou | Schaake96 | nan | 0.21 | nan | 65 | nan | 0 | nan | 0 |
| Ait Khabbach | Sebou | BATS | nan | 0.74 | nan | 0 | nan | 0 | nan | 0 |
| Azzaba | Sebou | SIMGM (Réf) | nan | 1.91 | nan | 0 | nan | 0 | nan | 0 |
| Azzaba | Sebou | SIMTOP | nan | 2.46 | nan | 0 | nan | 0 | nan | 0 |
| Azzaba | Sebou | Schaake96 | nan | 1.09 | nan | 0 | nan | 0 | nan | 0 |
| Azzaba | Sebou | BATS | nan | 3.33 | nan | 0 | nan | 0 | nan | 0 |
| Dar El Hamra | Sebou | SIMGM (Réf) | nan | 0.44 | nan | 0 | nan | 0 | nan | 0 |
| Dar El Hamra | Sebou | SIMTOP | nan | 0.38 | nan | 0 | nan | 0 | nan | 0 |
| Dar El Hamra | Sebou | Schaake96 | nan | 0.19 | nan | 30 | nan | 0 | nan | 0 |
| Dar El Hamra | Sebou | BATS | nan | 0.59 | nan | 0 | nan | 0 | nan | 0 |
| Pont Ait Aissa | Sebou | SIMGM (Réf) | nan | 0.08 | nan | 103 | nan | 0 | nan | 0 |
| Pont Ait Aissa | Sebou | SIMTOP | nan | 0.14 | nan | 40 | nan | 0 | nan | 0 |
| Pont Ait Aissa | Sebou | Schaake96 | nan | 0.04 | nan | 114 | nan | 0 | nan | 0 |
| Pont Ait Aissa | Sebou | BATS | nan | 0.15 | nan | 33 | nan | 0 | nan | 0 |
| Pont de Mdez | Sebou | SIMGM (Réf) | nan | 1.32 | nan | 0 | nan | 0 | nan | 0 |
| Pont de Mdez | Sebou | SIMTOP | nan | 1.90 | nan | 0 | nan | 0 | nan | 0 |
| Pont de Mdez | Sebou | Schaake96 | nan | 0.76 | nan | 0 | nan | 0 | nan | 0 |
| Pont de Mdez | Sebou | BATS | nan | 2.39 | nan | 0 | nan | 0 | nan | 0 |


