import os
import pandas as pd

OUTPUT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/outputs/matrix_2016/opl_vs_smap_da_scientific/"

def generate_coverage():
    data = [
        {"category": "evapotranspiration", "product": "WaPOR AETI", "diagnostic": "External ET Validation", "period_req": "2016", "status": "PARTIAL", "independence": "INDEPENDENT", "sensor_provenance": "Optical/Thermal", "contains_assimilated_sensor": False, "strict_independence_status": "INDEPENDENT"},
        {"category": "soil_moisture", "product": "ASCAT / ESA CCI ACTIVE", "diagnostic": "SMAP-DA Independent Validation", "period_req": "2016", "status": "MISSING", "independence": "INDEPENDENT", "sensor_provenance": "Scatterometer", "contains_assimilated_sensor": False, "strict_independence_status": "INDEPENDENT"},
        {"category": "streamflow", "product": "In-situ stations", "diagnostic": "HyMAP Routing Validation", "period_req": "2016", "status": "PARTIAL", "independence": "INDEPENDENT", "sensor_provenance": "In-situ Gauge", "contains_assimilated_sensor": False, "strict_independence_status": "INDEPENDENT"},
        {"category": "water_storage", "product": "GRACE/Mascon", "diagnostic": "Basin-scale TWS Validation", "period_req": "2016", "status": "PARTIAL", "independence": "INDEPENDENT", "sensor_provenance": "Gravimetry", "contains_assimilated_sensor": False, "strict_independence_status": "INDEPENDENT"},
        {"category": "lsm", "product": "ERA5-Land/GLDAS", "diagnostic": "Model Benchmark", "period_req": "2016", "status": "READY", "independence": "MODEL_BENCHMARK", "sensor_provenance": "Reanalysis", "contains_assimilated_sensor": False, "strict_independence_status": "FORCING_RELATED"},
        {"category": "precipitation", "product": "MSWEP / CHIRPS", "diagnostic": "precipitation_forcing_evaluation", "period_req": "2016", "status": "MISSING", "independence": "INDEPENDENT", "sensor_provenance": "Gauge/Satellite", "contains_assimilated_sensor": False, "strict_independence_status": "INDEPENDENT"}
    ]
    df = pd.DataFrame(data)
    os.makedirs(os.path.join(OUTPUT_DIR, "tables"), exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, "tables/validation_diagnostic_coverage.csv"), index=False)

def generate_requirements():
    data = [
        {"priority": "P0_IMMEDIATE", "product": "WaPOR AETI", "version": "VERSION_TO_VERIFY", "variable": "ET", "period": "2016", "reason": "Preprocess existing WaPOR, inspect EnKF/DAOBS, audit TWS/GWS, QC 366 days", "acquisition_action": "PREPROCESS_EXISTING"},
        {"priority": "P0_CONDITIONAL_ROUTING", "product": "Streamflow Stations", "version": "LATEST", "variable": "Q", "period": "2016", "reason": "Required for HyMAP routing (if ready)", "acquisition_action": "REQUEST_FROM_BASIN_AGENCY"},
        {"priority": "P1", "product": "ASCAT / ESA CCI ACTIVE", "version": "VERSION_TO_VERIFY", "variable": "SM", "period": "2016", "reason": "Independent SM validation vs SMAP-DA", "acquisition_action": "DOWNLOAD"},
        {"priority": "P1", "product": "MSWEP / CHIRPS", "version": "LATEST", "variable": "Precip", "period": "2016", "reason": "Forcing evaluation", "acquisition_action": "DOWNLOAD"},
        {"priority": "P1", "product": "In-situ Precip", "version": "LATEST", "variable": "Precip", "period": "2016", "reason": "Local forcing evaluation", "acquisition_action": "REQUEST_FROM_BASIN_AGENCY"},
        {"priority": "P2_OPTIONAL", "product": "GRACE Mascon", "version": "LATEST", "variable": "TWS", "period": "2016", "reason": "Basin scale TWS only", "acquisition_action": "DOWNLOAD"},
        {"priority": "P2_OPTIONAL", "product": "MODIS LAI / GPP", "version": "V6.1", "variable": "LAI/GPP", "period": "2016", "reason": "Vegetation response", "acquisition_action": "DOWNLOAD"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(OUTPUT_DIR, "tables/validation_download_requirements.csv"), index=False)
    
    with open(os.path.join(OUTPUT_DIR, "provenance/validation_download_requirements.md"), "w") as f:
        f.write("# Validation Download Requirements\n\n")
        f.write("| priority | product | version | variable | period | reason | acquisition_action |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for row in data:
            f.write(f"| {row['priority']} | {row['product']} | {row['version']} | {row['variable']} | {row['period']} | {row['reason']} | {row['acquisition_action']} |\n")

def generate_status_report():
    with open(os.path.join(OUTPUT_DIR, "provenance/validation_data_status.md"), "w") as f:
        f.write("# Validation Data Status\n\n")
        f.write("## Notes Scientifiques et Indépendance\n")
        f.write("- Le bilan hydrique LIS utilise `Rainf_f_tavg` pour sa fermeture interne. MSWEP/CHIRPS seront évalués dans `precipitation_forcing_evaluation`.\n")
        f.write("- Le bilan hydrique reste `PARTIAL` (besoin de définir TWS/GWS, double comptage, incréments en équivalent eau).\n")
        f.write("- ESA CCI ACTIVE ou ASCAT sont les seuls candidats pour la validation indépendante de l'humidité du sol.\n")
        f.write("- GRACE/Mascon est classé `P2_OPTIONAL` (à n'utiliser qu'à l'échelle de grands bassins, pas pixel-par-pixel).\n")
        f.write("- Les débits sont classés `P0_CONDITIONAL_ROUTING`.\n")
        f.write("- ERA5/GLDAS (`MODEL_BENCHMARK`) peuvent avoir `independence_status: FORCING_RELATED` s'ils sont liés au CDF matching.\n\n")
        
        f.write("## Synthèse\n\n")
        f.write("| Figure ou diagnostic | Données requises | Données trouvées | Couverture 2016 | Indépendance | Statut | Téléchargement ou action requis |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        f.write("| Biais ET | WaPOR v2 AETI | Non | N/A | INDEPENDENT | MISSING_LOCAL | DOWNLOAD_REQUIRED (WaPOR v3 local limité à 2018-2020) |\n")
        f.write("| Internal Water Balance | Flux internes LIS | Oui | N/A | INTERNAL | PARTIAL | P0: audit TWS/GWS, incréments |\n")
        f.write("| Precip Forcing Eval | CHIRPS/MSWEP | Non | N/A | INDEPENDENT | MISSING | P1: DOWNLOAD |\n")
        f.write("| Corrélation SM | ASCAT / ESA CCI ACTIVE | Non | N/A | INDEPENDENT | MISSING | P1: DOWNLOAD |\n")
        f.write("| HyMAP Routing | Streamflow | Partiel | Inconnu | INDEPENDENT | PARTIAL | P0: CONDITIONAL_ROUTING |\n")

if __name__ == "__main__":
    generate_coverage()
    generate_requirements()
    generate_status_report()
    print("Final Lot 1 reports updated with strict WaPOR v2 conclusions.")
