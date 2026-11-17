import pandas as pd
import numpy as np

# Load inventory
df_inv = pd.read_csv("experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv")
stations = ["b_l_chafia", "b_s_jabeur", "ain_timedrine", "dar_el_hamra", "pont_de_mdez", "ait_khabbach"]
sub_inv = df_inv[df_inv["station_id"].isin(stations)]

print("="*80)
print("STATION INVENTORY AUDIT")
print("="*80)
for _, r in sub_inv.iterrows():
    print(f"ID: {r['station_id']} | Nom: {r['nom']} | Bassin: {r['bassin']} | Pas: {r['pas_temps']}")
    print(f"  Obs 2018: {r['n_obs_2018']} ({r['couverture_2018_pct']}%) | Cell: ({r['row_hymap']}, {r['col_hymap']}) | Dist: {r['dist_hymap_km']} km")
    print(f"  Aires: off={r['aire_off_km2']} km2, hymap={r['aire_hymap_km2']} km2, d8={r['aire_d8_km2']} km2 (ecart={r['ecart_aire_pct']}%)")
    print(f"  Statut: {r['statut_2018']}")
    print(f"  Ouvrages: {r['influence_ouvrages_regulation']}")
    print(f"  Emboitement: {r['emboitement_amont']}")
    print(f"  Reserves: {r['reserves_methodologiques']}")
    print()

print("="*80)
print("METRICS AUDIT (2018)")
print("="*80)
df_met = pd.read_csv("experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/table_multistation_metrics_2018.csv")
sub_met = df_met[df_met["station_id"].isin(stations)]
cols = ["station_id", "nom", "experiment", "pas_temps", "aire_d8_km2", "NSE_daily", "KGE_daily", "PBIAS_daily_pct", "r_daily", "NSE_monthly", "KGE_monthly", "PBIAS_monthly_pct", "r_monthly", "q_mean_obs_m3s", "q_mean_sim_m3s"]
print(sub_met[cols].to_string())
