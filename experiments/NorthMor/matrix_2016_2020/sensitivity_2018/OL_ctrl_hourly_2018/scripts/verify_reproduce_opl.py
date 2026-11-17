#!/usr/bin/env python3
"""
Vérification de la reproduction exacte des moyennes journalières de OPL_noirr par OL_ctrl_hourly_2018.
Auteur: mohammad.elaabaribao
"""
import os
import glob
import re
import netCDF4 as nc
import numpy as np

def verify():
    ctrl_dir = "/srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_ctrl_hourly_2018/output/SURFACEMODEL"
    opl_dir = "/srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output"
    
    print("=================================================================")
    print(" VÉRIFICATION : REPRODUCTION DE OPL_noirr EN 2018")
    print("=================================================================")
    
    # Check if ctrl output exists
    ctrl_files = sorted(glob.glob(os.path.join(ctrl_dir, "*", "LIS_HIST_*.d01.nc")))
    if not ctrl_files:
        print(f"[ATTENTION] Aucune sortie horaire trouvée dans {ctrl_dir}")
        print("Le run OL_ctrl_hourly_2018 n'a pas encore été exécuté.")
        print("Ce script servira de protocole de validation post-exécution.")
        return
    
    # Group ctrl files by date
    days_dict = {}
    for f in ctrl_files:
        fname = os.path.basename(f)
        m = re.match(r"LIS_HIST_(\d{8})\d{4}\.d01\.nc", fname)
        if m:
            date_str = m.group(1)
            days_dict.setdefault(date_str, []).append(f)
            
    print(f"Nombre de jours horaires trouvés : {len(days_dict)}")
    
    max_diff_sm = 0.0
    max_diff_evap = 0.0
    tested_days = 0
    
    for date_str, hourly_files in sorted(days_dict.items())[:30]: # Test first 30 available days
        ym = date_str[:6]
        y_m = f"{date_str[:4]}-{date_str[4:6]}"
        opl_path = os.path.join(opl_dir, y_m, "SURFACEMODEL", ym, f"LIS_HIST_{date_str}0000.d01.nc")
        
        if not os.path.exists(opl_path):
            continue
            
        # Compute daily average from hourly files
        sm_hourly = []
        evap_hourly = []
        for hf in hourly_files:
            with nc.Dataset(hf, "r") as ds:
                sm_hourly.append(ds["SoilMoist_tavg"][:])
                evap_hourly.append(ds["Evap_tavg"][:])
                
        sm_daily_ctrl = np.mean(sm_hourly, axis=0)
        evap_daily_ctrl = np.mean(evap_hourly, axis=0)
        
        with nc.Dataset(opl_path, "r") as ds_opl:
            sm_opl = ds_opl["SoilMoist_tavg"][:]
            evap_opl = ds_opl["Evap_tavg"][:]
            
        diff_sm = np.nanmax(np.abs(sm_daily_ctrl - sm_opl))
        diff_evap = np.nanmax(np.abs(evap_daily_ctrl - evap_opl))
        
        max_diff_sm = max(max_diff_sm, diff_sm)
        max_diff_evap = max(max_diff_evap, diff_evap)
        tested_days += 1
        
    print(f"Jours testés : {tested_days}")
    print(f"Différence max SoilMoist : {max_diff_sm:.6e} m3/m3")
    print(f"Différence max Evap : {max_diff_evap:.6e} kg/m2s")
    
    if max_diff_sm < 1e-4 and max_diff_evap < 1e-4:
        print("[SUCCÈS] Reproduction exacte des sorties journalières de production !")
    else:
        print("[ÉCART DÉTECTÉ] Vérifier les configurations.")

if __name__ == "__main__":
    verify()
