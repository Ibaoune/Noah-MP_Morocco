# Validation Data Status

## Notes Scientifiques et Indépendance
- Le bilan hydrique LIS utilise `Rainf_f_tavg` pour sa fermeture interne. MSWEP/CHIRPS seront évalués dans `precipitation_forcing_evaluation`.
- Le bilan hydrique reste `PARTIAL` (besoin de définir TWS/GWS, double comptage, incréments en équivalent eau).
- ESA CCI ACTIVE ou ASCAT sont les seuls candidats pour la validation indépendante de l'humidité du sol.
- GRACE/Mascon est classé `P2_OPTIONAL` (à n'utiliser qu'à l'échelle de grands bassins, pas pixel-par-pixel).
- Les débits sont classés `P0_CONDITIONAL_ROUTING`.
- ERA5/GLDAS (`MODEL_BENCHMARK`) peuvent avoir `independence_status: FORCING_RELATED` s'ils sont liés au CDF matching.

## Synthèse

| Figure ou diagnostic | Données requises | Données trouvées | Couverture 2016 | Indépendance | Statut | Téléchargement ou action requis |
|---|---|---|---|---|---|---|
| Biais ET | WaPOR v2 AETI | Non | N/A | INDEPENDENT | MISSING_LOCAL | DOWNLOAD_REQUIRED (WaPOR v3 local limité à 2018-2020) |
| Internal Water Balance | Flux internes LIS | Oui | N/A | INTERNAL | PARTIAL | P0: audit TWS/GWS, incréments |
| Precip Forcing Eval | CHIRPS/MSWEP | Non | N/A | INDEPENDENT | MISSING | P1: DOWNLOAD |
| Corrélation SM | ASCAT / ESA CCI ACTIVE | Non | N/A | INDEPENDENT | MISSING | P1: DOWNLOAD |
| HyMAP Routing | Streamflow | Partiel | Inconnu | INDEPENDENT | PARTIAL | P0: CONDITIONAL_ROUTING |
