#!/usr/bin/env python3
import os, glob, datetime, sys
import netCDF4 as nc
import numpy as np
from multiprocessing import Pool

# Load LDT parameters
ldt_path = 'experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc'
ds_ldt = nc.Dataset(ldt_path)
bmask = ds_ldt['HYMAP_basin_mask'][:].astype(np.int32)
grarea = ds_ldt['HYMAP_grid_area'][:].astype(np.float64)
lat_tgt = ds_ldt['lat'][:].astype(np.float64)
lon_tgt = ds_ldt['lon'][:].astype(np.float64)
ds_ldt.close()

# Geometric spherical cell area for target grid (120, 180)
R_earth = 6371000.0 # meters
dlon_rad = np.radians(0.05)
lat_s = np.radians(lat_tgt - 0.025)
lat_n = np.radians(lat_tgt + 0.025)
area_tgt_geom = (R_earth**2) * (np.sin(lat_n) - np.sin(lat_s)) * dlon_rad # m^2

# For source grid (121, 181)
weights_src = np.ones((121, 181), dtype=np.float64)
weights_src[0, :] *= 0.5
weights_src[-1, :] *= 0.5
weights_src[:, 0] *= 0.5
weights_src[:, -1] *= 0.5

lats_src_1d = np.linspace(30.0, 36.0, 121)
lats_src_2d = np.repeat(lats_src_1d[:, None], 181, axis=1)
lat_src_s = np.radians(lats_src_2d - 0.025)
lat_src_n = np.radians(lats_src_2d + 0.025)
area_src_geom = (R_earth**2) * (np.sin(lat_src_n) - np.sin(lat_src_s)) * dlon_rad # m^2

SEC_PER_DAY = 86400.0
FACTOR = SEC_PER_DAY / (1000.0 * 1e6) # m3 to hm3

# Build list of 365 physical dates for 2018
y2018_files = []
for m in range(1, 13):
    for d in range(1, 32):
        try:
            dt = datetime.date(2018, m, d)
            if not (m == 1 and d == 1):
                y2018_files.append(f'LIS_HIST_2018{m:02d}{d:02d}0000.d01.nc')
        except ValueError:
            pass
y2018_files.append('LIS_HIST_201901010000.d01.nc')
assert len(y2018_files) == 365

def process_single_day(args):
    f_src, f_rem = args
    
    # Read source
    ds_s = nc.Dataset(f_src)
    qs_s = ds_s['Qs_tavg'][:]
    qsb_s = ds_s['Qsb_tavg'][:]
    if qs_s.ndim == 3: qs_s = qs_s[0]
    if qsb_s.ndim == 3: qsb_s = qsb_s[0]
    qs_s = np.where((qs_s < 0) | np.isnan(qs_s), 0.0, qs_s).astype(np.float64)
    qsb_s = np.where((qsb_s < 0) | np.isnan(qsb_s), 0.0, qsb_s).astype(np.float64)
    ds_s.close()
    
    qs_s1 = np.sum(qs_s * weights_src * area_src_geom) * FACTOR
    qsb_s1 = np.sum(qsb_s * weights_src * area_src_geom) * FACTOR
    
    # Read remapped
    ds_r = nc.Dataset(f_rem)
    qs_r = ds_r['Qs_tavg'][:]
    qsb_r = ds_r['Qsb_tavg'][:]
    if qs_r.ndim == 3: qs_r = qs_r[0]
    if qsb_r.ndim == 3: qsb_r = qsb_r[0]
    qs_r = qs_r.astype(np.float64)
    qsb_r = qsb_r.astype(np.float64)
    ds_r.close()
    
    qs_s2 = np.sum(qs_r * area_tgt_geom) * FACTOR
    qsb_s2 = np.sum(qsb_r * area_tgt_geom) * FACTOR
    
    qs_s3 = np.sum(qs_r[bmask == 1] * area_tgt_geom[bmask == 1]) * FACTOR
    qsb_s3 = np.sum(qsb_r[bmask == 1] * area_tgt_geom[bmask == 1]) * FACTOR
    
    qs_s4 = np.sum(qs_r[bmask == 1] * grarea[bmask == 1]) * FACTOR
    qsb_s4 = np.sum(qsb_r[bmask == 1] * grarea[bmask == 1]) * FACTOR
    
    return np.array([qs_s1, qsb_s1, qs_s2, qsb_s2, qs_s3, qsb_s3, qs_s4, qsb_s4])

def compute_2018(exp_label, src_base, remap_base, pool):
    src_all = glob.glob(f"{src_base}/**/LIS_HIST_*.d01.nc", recursive=True)
    rem_all = glob.glob(f"{remap_base}/**/LIS_HIST_*.d01.nc", recursive=True)
    src_dict = {os.path.basename(f): f for f in src_all}
    rem_dict = {os.path.basename(f): f for f in rem_all}
    
    tasks = [(src_dict[fn], rem_dict[fn]) for fn in y2018_files]
    results = pool.map(process_single_day, tasks)
    sums = np.sum(results, axis=0)
    
    qs_s1, qsb_s1, qs_s2, qsb_s2, qs_s3, qsb_s3, qs_s4, qsb_s4 = sums
    
    return {
        'label': exp_label,
        'qs': (qs_s1, qs_s2, qs_s3, qs_s4),
        'qsb': (qsb_s1, qsb_s2, qsb_s3, qsb_s4),
        'tot': (qs_s1 + qsb_s1, qs_s2 + qsb_s2, qs_s3 + qsb_s3, qs_s4 + qsb_s4)
    }

if __name__ == '__main__':
    with Pool(processes=16) as pool:
        experiments = [
            ("Open-Loop (OL)", "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output", "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"),
            ("DA-NoCDF", "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output", "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL"),
            ("DA-CDF (corrigee)", "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output", "experiments/NorthMor/routing/runoff_remap_180x120/DA_cdf_noirr_2016_2020/SURFACEMODEL"),
        ]
        
        all_res = []
        for label, s_base, r_base in experiments:
            res = compute_2018(label, s_base, r_base, pool)
            all_res.append(res)
            print(f"\n==========================================================================================")
            print(f"RÉSULTATS 2018 (365 jours physiques) : {res['label']}")
            print(f"==========================================================================================")
            for var, key in [('Ruissellement (Qs)', 'qs'), ('Débit de base (Qsb)', 'qsb'), ('Total (Qtot)', 'tot')]:
                s1, s2, s3, s4 = res[key]
                ratio_s2_s1 = (s2 / s1) * 100.0
                excl = s2 - s3
                excl_pct = (excl / s2) * 100.0
                ratio_s4_s3 = (s4 / s3) * 100.0
                print(f"{var:<20} | S1={s1:9.2f} hm3 | S2={s2:9.2f} hm3 | S3={s3:9.2f} hm3 | S4={s4:9.2f} hm3 | S2/S1={ratio_s2_s1:.4f}% | Excl={excl:6.2f} hm3 ({excl_pct:.2f}%) | S4/S3={ratio_s4_s3:.2f}%")

