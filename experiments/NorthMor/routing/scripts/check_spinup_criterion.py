#!/usr/bin/env python3
"""
check_spinup_criterion.py
Calcule les stocks de nappe et totaux a la fin des cycles 1 et 2 de spin-up (2016)
et verifie le critere de convergence :
  Delta_rel = |S_BSF^(2) - S_BSF^(1)| / S_BSF^(1) < 1.0%
"""
import netCDF4 as nc
import numpy as np

rst_c1 = "experiments/NorthMor/routing/output/OPL_spinup_cycle1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
rst_c2 = "experiments/NorthMor/routing/output/OPL_spinup_cycle2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"

def read_stocks(rst_file):
    with nc.Dataset(rst_file, 'r') as ds:
        bsf = ds.variables['BSFSTO'][:]
        rnf = ds.variables['RNFSTO'][:]
        riv = ds.variables['RIVSTO'][:]
        fld = ds.variables['FLDSTO'][:]
        
        bsf_val = np.where(bsf > 0, bsf, 0.0)
        rnf_val = np.where(rnf > 0, rnf, 0.0)
        riv_val = np.where(riv > 0, riv, 0.0)
        fld_val = np.where(fld > 0, fld, 0.0)
        
        tot = bsf_val + rnf_val + riv_val + fld_val
        return {
            'bsf_m3': float(np.sum(bsf_val)),
            'rnf_m3': float(np.sum(rnf_val)),
            'riv_m3': float(np.sum(riv_val)),
            'fld_m3': float(np.sum(fld_val)),
            'tot_m3': float(np.sum(tot)),
        }

stocks_c1 = read_stocks(rst_c1)
stocks_c2 = read_stocks(rst_c2)

bsf1_hm3 = stocks_c1['bsf_m3'] / 1e6
bsf2_hm3 = stocks_c2['bsf_m3'] / 1e6
tot1_hm3 = stocks_c1['tot_m3'] / 1e6
tot2_hm3 = stocks_c2['tot_m3'] / 1e6

delta_bsf_hm3 = bsf2_hm3 - bsf1_hm3
delta_bsf_rel = abs(delta_bsf_hm3) / bsf1_hm3 * 100.0

delta_tot_hm3 = tot2_hm3 - tot1_hm3
delta_tot_rel = abs(delta_tot_hm3) / tot1_hm3 * 100.0

print(f"=== RESULTATS DU SPIN-UP OPTION B (2 BOUCLES SUR 2016) ===")
print(f"Cycle 1 (Initial = Coldstart S=0) :")
print(f"  Stock nappe (BSFSTO) : {bsf1_hm3:.3f} hm3")
print(f"  Stock total          : {tot1_hm3:.3f} hm3")
print(f"  Variation Cycle 1 vs Coldstart : +100.0% (+{bsf1_hm3:.3f} hm3)")
print()
print(f"Cycle 2 (Initial = Restart fin Cycle 1) :")
print(f"  Stock nappe (BSFSTO) : {bsf2_hm3:.3f} hm3")
print(f"  Stock total          : {tot2_hm3:.3f} hm3")
print(f"  Delta nappe Cycle 2 vs Cycle 1 : {delta_bsf_hm3:+.3f} hm3 ({delta_bsf_rel:.4f}%)")
print(f"  Delta total Cycle 2 vs Cycle 1 : {delta_tot_hm3:+.3f} hm3 ({delta_tot_rel:.4f}%)")
print()
if delta_bsf_rel < 1.0:
    print(f"CRITERE VALIDE : {delta_bsf_rel:.4f}% < 1.0%")
else:
    print(f"CRITERE NON ATTEINT : {delta_bsf_rel:.4f}% >= 1.0%")
