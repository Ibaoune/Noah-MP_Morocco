#!/usr/bin/env python3
import os
import netCDF4 as nc
import numpy as np

rst_c1 = "experiments/NorthMor/routing/output/DA_nocdf_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
rst_c2 = "experiments/NorthMor/routing/output/DA_nocdf_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"

def read_stocks(rst_file):
    if not os.path.exists(rst_file):
        return None
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
            'bsf_hm3': float(np.sum(bsf_val)) / 1e6,
            'rnf_hm3': float(np.sum(rnf_val)) / 1e6,
            'riv_hm3': float(np.sum(riv_val)) / 1e6,
            'fld_hm3': float(np.sum(fld_val)) / 1e6,
            'tot_hm3': float(np.sum(tot)) / 1e6,
        }

stocks_c1 = read_stocks(rst_c1)
stocks_c2 = read_stocks(rst_c2)

print("=== VERIFICATION DU SPIN-UP DA_nocdf (2016) ===")
if stocks_c1:
    print(f"Cycle 1 (Fin 2016) :")
    print(f"  BSFSTO (nappe) : {stocks_c1['bsf_hm3']:.3f} hm3")
    print(f"  RNFSTO (surf)  : {stocks_c1['rnf_hm3']:.3f} hm3")
    print(f"  RIVSTO (riv)   : {stocks_c1['riv_hm3']:.3f} hm3")
    print(f"  FLDSTO (fld)   : {stocks_c1['fld_hm3']:.3f} hm3")
    print(f"  Stock total    : {stocks_c1['tot_hm3']:.3f} hm3")
else:
    print("Cycle 1 restart non disponible pour le moment.")

if stocks_c2 and stocks_c1:
    print(f"\nCycle 2 (Fin 2016) :")
    print(f"  BSFSTO (nappe) : {stocks_c2['bsf_hm3']:.3f} hm3")
    print(f"  RNFSTO (surf)  : {stocks_c2['rnf_hm3']:.3f} hm3")
    print(f"  RIVSTO (riv)   : {stocks_c2['riv_hm3']:.3f} hm3")
    print(f"  FLDSTO (fld)   : {stocks_c2['fld_hm3']:.3f} hm3")
    print(f"  Stock total    : {stocks_c2['tot_hm3']:.3f} hm3")
    
    delta_bsf = stocks_c2['bsf_hm3'] - stocks_c1['bsf_hm3']
    delta_bsf_rel = abs(delta_bsf) / stocks_c1['bsf_hm3'] * 100.0
    delta_tot = stocks_c2['tot_hm3'] - stocks_c1['tot_hm3']
    delta_tot_rel = abs(delta_tot) / stocks_c1['tot_hm3'] * 100.0
    
    print(f"\nEcarts Cycle 2 vs Cycle 1 :")
    print(f"  Delta BSFSTO : {delta_bsf:+.3f} hm3 ({delta_bsf_rel:.4f} %)")
    print(f"  Delta Total  : {delta_tot:+.3f} hm3 ({delta_tot_rel:.4f} %)")
    if delta_bsf_rel < 1.0:
        print(f"--> CRITERE DE STABILISATION VALIDE : {delta_bsf_rel:.4f} % < 1.0 %")
    else:
        print(f"--> CRITERE NON ATTEINT : {delta_bsf_rel:.4f} % >= 1.0 %")
