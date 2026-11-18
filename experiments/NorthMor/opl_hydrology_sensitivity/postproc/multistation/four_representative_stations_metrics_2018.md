# Synthèse des Performances aux Quatre Stations Représentatives (2018)

Ce tableau résume les métriques d'évaluation et les principaux enseignements hydrologiques tirés de la comparaison des quatre schémas de ruissellement Noah-MP routés avec HyMAP-2 (`linres=0`).

> [!IMPORTANT]
> **Règle méthodologique stricte :** Les métriques journalières (Lalla Chafia, Sidi Jabeur) et mensuelles (Aïn Timedrine, Dar El Hamra) correspondent à des résolutions temporelles distinctes et ne sont pas agrégées dans un classement unique.

| Station | Bassin | Aire D8 (km²) | Résolution | N obs | Formulation | NSE | KGE | PBIAS (%) | $r$ | Principal enseignement / Limitation |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **Lalla Chafia** | Bouregreg | 3,333.3 | journalier | 364 | SIMGM (Reference) | +0.169 | +0.079 | -17.9% | 0.456 | Schéma de référence : sous-estimation des pointes de crue et sur-estimation estivale (NSE = 0.17). |
| **Lalla Chafia** | Bouregreg | 3,333.3 | journalier | 364 | SIMTOP | +0.592 | +0.593 | +16.9% | 0.777 | Meilleure performance globale : forte amélioration du NSE (+0.59) et du KGE (+0.59); timing des crues nettement rehaussé. |
| **Lalla Chafia** | Bouregreg | 3,333.3 | journalier | 364 | Schaake96 | +0.240 | +0.569 | -9.3% | 0.589 | Bonne dynamique volumique globale (PBIAS -9.3%) et KGE satisfaisant (0.57), mais réactivité d'inondation modérée. |
| **Lalla Chafia** | Bouregreg | 3,333.3 | journalier | 364 | BATS | -0.193 | +0.138 | +65.4% | 0.705 | Sur-estimation volumique annuelle (PBIAS +65.4%) et ruissellement excessif dégradant le NSE (-0.19). |
| **Sidi Jabeur** | Bouregreg (Grou) | 3,130.6 | journalier | 365 | SIMGM (Reference) | +0.054 | -0.161 | -63.8% | 0.656 | Schéma de référence : sous-estimation sévère des crues flash (PBIAS -63.8%, KGE négatif -0.16). |
| **Sidi Jabeur** | Bouregreg (Grou) | 3,130.6 | journalier | 365 | SIMTOP | +0.310 | +0.191 | -26.4% | 0.675 | Amélioration intermédiaire (NSE = 0.31, PBIAS = -26.4%); débits d'étiage maintenus au-dessus de 1.5 m³/s. |
| **Sidi Jabeur** | Bouregreg (Grou) | 3,130.6 | journalier | 365 | Schaake96 | +0.075 | +0.070 | -54.4% | 0.386 | Déficit volumique important (PBIAS -54.4%); réduction estivale plus forte mais pas d'assec strict. |
| **Sidi Jabeur** | Bouregreg (Grou) | 3,130.6 | journalier | 365 | BATS | +0.422 | +0.476 | -10.1% | 0.652 | Meilleure reproduction des volumes de crues (NSE = 0.42, PBIAS = -10.1%), mais échec sur l'assec estival. |
| **Aïn Timedrine** | Sebou (Haut Sebou) | 4,437.6 | mensuel | 12 | SIMGM (Reference) | -2.008 | -0.212 | -79.8% | 0.772 | Schéma de référence : déficit volumique massif de -80% dû aux pertes/délais karstiques non résolus. |
| **Aïn Timedrine** | Sebou (Haut Sebou) | 4,437.6 | mensuel | 12 | SIMTOP | -0.565 | +0.176 | -56.8% | 0.846 | Réduction modérée du déficit volumique (PBIAS -56.8%, KGE +0.18, r = 0.85). |
| **Aïn Timedrine** | Sebou (Haut Sebou) | 4,437.6 | mensuel | 12 | Schaake96 | -1.418 | -0.001 | -74.5% | 0.858 | Sous-estimation volumique persistante (PBIAS -74.5%, NSE -1.42). |
| **Aïn Timedrine** | Sebou (Haut Sebou) | 4,437.6 | mensuel | 12 | BATS | +0.330 | +0.529 | -36.8% | 0.909 | Réduction spectaculaire du déficit volumique (PBIAS passe de -80% à -37%, NSE passe à +0.33, r = 0.91). |
| **Dar El Hamra** | Sebou (Oued Zloul) | 654.8 | mensuel | 12 | SIMGM (Reference) | -0.643 | -0.292 | -84.5% | 0.773 | Schéma de référence : déficit volumique aigu (-84.5%), débit simulé moyen 0.56 vs 3.62 m³/s observé. |
| **Dar El Hamra** | Sebou (Oued Zloul) | 654.8 | mensuel | 12 | SIMTOP | -0.135 | -0.051 | -69.5% | 0.921 | Corrélation élevée (r = 0.92) mais déficit volumique marqué (PBIAS -69.5%, NSE -0.14). |
| **Dar El Hamra** | Sebou (Oued Zloul) | 654.8 | mensuel | 12 | Schaake96 | -0.459 | -0.202 | -83.7% | 0.956 | Très forte synchronicité (r = 0.96) mais sous-estimation volumique sévère (PBIAS -83.7%). |
| **Dar El Hamra** | Sebou (Oued Zloul) | 654.8 | mensuel | 12 | BATS | +0.258 | +0.161 | -54.1% | 0.946 | Seul schéma atteignant un NSE mensuel positif (+0.26, r = 0.95); déficit réduit de moitié (-54%). |
