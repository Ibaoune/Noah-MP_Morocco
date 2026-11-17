import os
import netCDF4 as nc
import numpy as np
import pandas as pd

REPO_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_PATH = os.path.join(REPO_ROOT, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
PAIRING_PATH = os.path.join(REPO_ROOT, "experiments/NorthMor/routing/stations/hymap_stations_pairing.csv")
STATIONS_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/stations.csv")
OBS_DAILY_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/obs_daily.csv")
OBS_MONTHLY_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/obs_monthly.csv")

OUT_CSV = os.path.join(REPO_ROOT, "experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv")
OUT_MD = os.path.join(REPO_ROOT, "experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.md")

def main():
    ds_ldt = nc.Dataset(LDT_PATH)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    drain_area = ds_ldt["HYMAP_drain_area"][:].filled(0.0)
    R, C = flow_x.shape
    ds_ldt.close()

    down_r = np.full((R, C), -1, dtype=int)
    down_c = np.full((R, C), -1, dtype=int)
    for c in range(C):
        for r in range(R):
            if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
                vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
                if 1 <= vx <= C and 1 <= vy <= R:
                    down_c[r, c], down_r[r, c] = vx - 1, vy - 1

    parents = {}
    for r in range(R):
        for c in range(C):
            pr, pc = down_r[r, c], down_c[r, c]
            if pr >= 0 and pc >= 0:
                if (pr, pc) not in parents:
                    parents[(pr, pc)] = []
                parents[(pr, pc)].append((r, c))

    def get_catchment(orow, ocol):
        vis = set([(orow, ocol)])
        q = [(orow, ocol)]
        while q:
            curr = q.pop(0)
            if curr in parents:
                for p in parents[curr]:
                    if p not in vis:
                        vis.add(p)
                        q.append(p)
        return vis

    df_d = pd.read_csv(OBS_DAILY_CSV)
    df_d["date"] = pd.to_datetime(df_d["date"])
    d_2018 = df_d[df_d["date"].dt.year == 2018]

    df_m = pd.read_csv(OBS_MONTHLY_CSV)
    m_2018 = df_m[df_m["annee"] == 2018]

    df_st = pd.read_csv(STATIONS_CSV)
    df_pair = pd.read_csv(PAIRING_PATH)
    pair_dict = {r["station_id"]: r for _, r in df_pair.iterrows()}

    records = []
    station_catchments = {}

    for _, srow in df_st.iterrows():
        sid = srow["station_id"]
        nom = srow["nom"]
        ire = srow["ire"] if pd.notna(srow["ire"]) else ""
        bassin = srow["bassin"]
        oued = srow["oued"] if pd.notna(srow["oued"]) else ""
        pas = srow["pas_de_temps"]
        date_fin = str(srow["date_fin"])
        
        if pas == "journalier":
            sub = d_2018[d_2018["station_id"] == sid]
            n_obs = int(sub["q_m3s"].count())
            n_nan = int(sub["q_m3s"].isna().sum())
            couv_pct = round(n_obs / 365.0 * 100.0, 1)
        else:
            sub = m_2018[m_2018["station_id"] == sid]
            n_obs = int(sub["q_m3s"].count())
            n_nan = int(sub["q_m3s"].isna().sum())
            couv_pct = round(n_obs / 12.0 * 100.0, 1)

        is_paired = sid in pair_dict
        if is_paired:
            p = pair_dict[sid]
            r_hy, c_hy = int(p["row_hymap"]), int(p["col_hymap"])
            lon_hy = float(p["lon_hymap"])
            lat_hy = float(p["lat_hymap"])
            dist_km = round(float(p["dist_km"]), 2)
            hymap_drain = round(float(drain_area[r_hy, c_hy] / 1e6), 2)
            
            cat = get_catchment(r_hy, c_hy)
            station_catchments[sid] = cat
            n_cells_d8 = len(cat)
            d8_area_km2 = round(sum(grid_area[cr, cc] for cr, cc in cat) / 1e6, 2)
            
            aire_off = float(p["aire_off_km2"]) if pd.notna(p["aire_off_km2"]) else np.nan
            if not np.isnan(aire_off):
                ecart_aire_pct = round((d8_area_km2 - aire_off) / aire_off * 100.0, 2)
            else:
                ecart_aire_pct = np.nan
            qual_app = p["niveau"]
        else:
            r_hy, c_hy = np.nan, np.nan
            lon_hy, lat_hy = np.nan, np.nan
            dist_km = np.nan
            hymap_drain = np.nan
            n_cells_d8 = 0
            d8_area_km2 = np.nan
            aire_off = float(srow["aire_officielle_km2"]) if pd.notna(srow["aire_officielle_km2"]) else np.nan
            ecart_aire_pct = np.nan
            qual_app = "Non apparié"

        if sid in ["b_l_chafia", "b_s_jabeur"]:
            statut = "Retenue — Évaluation principale"
            motif = "Station journalière Bouregreg complète (364-365 j), exutoire amont naturel non régulé, morphologie validée."
            influence = "Amont naturel préservé, situé en amont du barrage SMBA. Aucune régulation majeure active en amont."
            emboitement = "Sous-bassin autonome (confluence avec Grou/Bouregreg dans la retenue SMBA)."
            reserves = "Aucune réserve majeure. Superficie officielle administrative non chiffrée par l ABH (Niveau B), mais réseau D8 morphologiquement calé."
        elif sid in ["ain_timedrine", "azzaba", "pont_de_mdez", "ait_khabbach", "dar_el_hamra"]:
            statut = "Retenue — Évaluation principale"
            motif = "Station mensuelle Sebou 2018 complète (12/12 mois), appariement Niveau A validé (< 10% écart d aire)."
            if sid == "pont_de_mdez":
                influence = "Site du barrage M Dez en amont (génie civil et dérivation provisoire actifs en 2017-2018)."
                emboitement = "Englobe Ait Khabbach (53 mailles) et Pont Ait Aissa (11 mailles)."
            elif sid == "ain_timedrine":
                influence = "Sources karstiques (Ain Sebou) et chantier barrage M Dez en amont."
                emboitement = "Englobe Pont de Mdez (135 mailles), Ait Khabbach (53 mailles), Dar El Hamra (26 mailles), Pont Ait Aissa (11 mailles)."
            elif sid == "azzaba":
                influence = "Aval immédiat d Ain Timedrine. Influence identique à Ain Timedrine."
                emboitement = "Englobe l intégralité du Haut Sebou (182 mailles, incluant Ain Timedrine)."
            elif sid == "ait_khabbach":
                influence = "Régime karstique du Moyen Atlas, pompages agricoles saisonniers dans le causse/plaine du Guigou."
                emboitement = "Englobe Pont Ait Aissa (11 mailles). Englobé dans Pont de Mdez, Ain Timedrine, Azzaba."
            elif sid == "dar_el_hamra":
                influence = "Régime naturel de montagne (Oued Zloul), pas de barrage amont."
                emboitement = "Affluent indépendant rive droite, conflue avec le Sebou avant Ain Timedrine."
            reserves = "Observations mensuelles uniquement (agrégation mensuelle requise pour la comparaison). Flag ABH suspect sur l historique."
        elif sid in ["b_a_loudah", "b_s_cherif"]:
            statut = "Retenue — Avec réserves"
            motif = "Station journalière complète en 2018 (365 j), appariée à HyMAP, mais série d observation strictement dupliquée."
            influence = "Régime naturel, plateau amont Bouregreg."
            emboitement = "Sous-bassins distincts sur la grille HyMAP (26 mailles chacun), confluant en aval."
            reserves = "Doublon d observation ABH : séries de débit mesurées identiques à 96.3% (r = 1.000). Ne peut pas servir d évaluation indépendante."
        elif sid == "pont_ait_aissa":
            statut = "Retenue — Avec réserves"
            motif = "Station mensuelle complète en 2018 (12/12 mois), mais très petit bassin versant (205 km²)."
            influence = "Tête de bassin karstique du Guigou."
            emboitement = "Tête de réseau, englobée successivement dans Ait Khabbach, Pont de Mdez, Ain Timedrine, Azzaba."
            reserves = "Écart d aire HyMAP/ABH élevé (+23.8%) dû à la résolution spatiale de 0.05° (~25 km²/maille pour un bassin de 205 km²)."
        elif sid in ["b_a_ziar", "b_r_fathia"]:
            statut = "Exclue"
            motif = "Coordonnées géographiques manquantes dans toutes les archives ABH."
            influence = "Inconnue."
            emboitement = "Non positionnable sur la grille HyMAP."
            reserves = "Inexploitable sans localisation spatiale."
        elif sid in ["adamna", "el_mers"]:
            statut = "Exclue"
            motif = "Aucune observation disponible sur l année 2018 (enregistrement arrêté avant 2018 : fin " + date_fin + ")."
            influence = "Sans objet pour 2018."
            emboitement = "Non exploitable sur 2018."
            reserves = "Données 2018 inexistantes."
        else:
            statut = "Exclue"
            motif = "Station historique fermée avant la période simulée (arrêt en " + date_fin + ")."
            influence = "Sans objet."
            emboitement = "Sans objet."
            reserves = "Données 2018 inexistantes."

        records.append({
            "station_id": sid,
            "nom": nom,
            "ire": ire,
            "bassin": bassin,
            "sous_bassin": oued,
            "pas_temps": pas,
            "n_obs_2018": n_obs,
            "couverture_2018_pct": couv_pct,
            "row_hymap": int(r_hy) if pd.notna(r_hy) else "",
            "col_hymap": int(c_hy) if pd.notna(c_hy) else "",
            "dist_hymap_km": dist_km if pd.notna(dist_km) else "",
            "aire_off_km2": aire_off if pd.notna(aire_off) else "",
            "aire_hymap_km2": hymap_drain if pd.notna(hymap_drain) else "",
            "aire_d8_km2": d8_area_km2 if pd.notna(d8_area_km2) else "",
            "n_mailles_d8": n_cells_d8 if n_cells_d8 > 0 else "",
            "ecart_aire_pct": ecart_aire_pct if pd.notna(ecart_aire_pct) else "",
            "qualite_appariement": qual_app,
            "statut_2018": statut,
            "influence_ouvrages_regulation": influence,
            "emboitement_amont": emboitement,
            "reserves_methodologiques": reserves,
            "motif_statut": motif
        })

    df_inv = pd.DataFrame(records)
    statut_order = {"Retenue — Évaluation principale": 1, "Retenue — Avec réserves": 2, "Exclue": 3}
    df_inv["order"] = df_inv["statut_2018"].map(statut_order)
    df_inv = df_inv.sort_values(by=["order", "bassin", "nom"]).drop(columns=["order"])

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df_inv.to_csv(OUT_CSV, index=False)
    print("Inventaire CSV généré :", OUT_CSV, "(", len(df_inv), "stations)")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Inventaire des Stations Hydrométriques ABH — Année 2018\n\n")
        f.write("Ce document présente l inventaire méthodologique et le statut d exploitation des 20 stations hydrométriques "
                "couvertes par les données d observation ABH pour l évaluation des simulations Noah-MP / HyMAP-2 (2018).\n\n")
        
        f.write("## 1. Synthèse par Catégorie d Exploitation 2018\n\n")
        counts = df_inv["statut_2018"].value_counts()
        for st, c in counts.items():
            f.write("- **" + str(st) + "** : " + str(c) + " stations\n")
        f.write("\n---\n\n")

        f.write("## 2. Tableau Exhaustif des Stations\n\n")
        cols_disp = ["station_id", "nom", "ire", "bassin", "sous_bassin", "pas_temps", "n_obs_2018", 
                     "row_hymap", "col_hymap", "aire_off_km2", "aire_d8_km2", "ecart_aire_pct", 
                     "qualite_appariement", "statut_2018"]
        df_sub = df_inv[cols_disp].fillna("")
        f.write("| " + " | ".join(cols_disp) + " |\n")
        f.write("| " + " | ".join(["---"] * len(cols_disp)) + " |\n")
        for _, row in df_sub.iterrows():
            f.write("| " + " | ".join([str(val) for val in row.values]) + " |\n")
        f.write("\n---\n\n")

        f.write("## 3. Détail des Réserves et Régulations par Station Retenue\n\n")
        retained = df_inv[df_inv["statut_2018"] != "Exclue"]
        for _, r in retained.iterrows():
            f.write("### " + str(r["nom"]) + " (`" + str(r["station_id"]) + "`)\n")
            f.write("- **Bassin / Sous-bassin** : " + str(r["bassin"]) + " (" + str(r["sous_bassin"]) + ")\n")
            f.write("- **Statut 2018** : " + str(r["statut_2018"]) + "\n")
            f.write("- **Résolution temporelle** : " + str(r["pas_temps"]) + " (" + str(r["n_obs_2018"]) + " pas valides en 2018)\n")
            f.write("- **Appariement HyMAP** : Maille `[" + str(r["row_hymap"]) + ", " + str(r["col_hymap"]) + "]`, Distance = " + str(r["dist_hymap_km"]) + " km, Niveau = " + str(r["qualite_appariement"]) + "\n")
            f.write("- **Surfaces** : D8 = " + str(r["aire_d8_km2"]) + " km² (" + str(r["n_mailles_d8"]) + " mailles) | HyMAP = " + str(r["aire_hymap_km2"]) + " km² | Off = " + str(r["aire_off_km2"]) + " km² (Écart = " + str(r["ecart_aire_pct"]) + " %)\n")
            f.write("- **Influence régulations / barrages** : " + str(r["influence_ouvrages_regulation"]) + "\n")
            f.write("- **Emboîtement hydrologique** : " + str(r["emboitement_amont"]) + "\n")
            f.write("- **Réserves méthodologiques** : " + str(r["reserves_methodologiques"]) + "\n\n")

        f.write("## 4. Stations Exclues et Motifs\n\n")
        excluded = df_inv[df_inv["statut_2018"] == "Exclue"]
        for _, r in excluded.iterrows():
            f.write("- **" + str(r["nom"]) + " (`" + str(r["station_id"]) + "`)" + "** [" + str(r["bassin"]) + "] : " + str(r["motif_statut"]) + "\n")

    print("Inventaire Markdown généré :", OUT_MD)

if __name__ == "__main__":
    main()
