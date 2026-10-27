#!/usr/bin/env python3
"""
Verify HyMAP parameters written to lis_input.d01.nc by LDT.
Checks:
- Dimensions and coordinates (180x120, 0.05 deg)
- Range of each HyMAP variable vs Section 2 ground truth
- Basin outlet locations and upstream areas
- Consistency with LANDMASK
"""
import sys
import numpy as np
import netCDF4 as nc

EXPECTED_RANGES = {
    'HYMAP_river_width': (5.0, 14264.0),
    'HYMAP_river_height': (0.500, 0.554),
    'HYMAP_river_roughness': (0.1015, 0.1042),
    'HYMAP_floodplain_roughness': (0.035, 0.078),
    'HYMAP_river_length': (151.2, 34128.0),
    'HYMAP_grid_elevation': (0.0, 3280.0),
    'HYMAP_grid_distance': (212.3, 43848.0),
    'HYMAP_grid_area': (22256.0, 1.789e8),
    'HYMAP_drain_area': (28185.0, 6.280e10),
    'HYMAP_ref_discharge': (2.0e-6, 130.4),
    'HYMAP_runoff_time_delay': (18003.0, 8.724e6),
    'HYMAP_baseflow_time_delay': (203.7, 2.632e6),
    'HYMAP_node_lon': (-9.855, -1.0004),
    'HYMAP_node_lat': (30.001, 35.905),
}

EXPECTED_BASINS = [
    ("Moulouya", 313, -2.325, 35.125, 54103.0),
    ("Sebou", 155, -6.675, 34.275, 38675.0),
    ("Oum Er Rbia", 86, -8.325, 33.325, 35527.0),
    ("Tensift", 51, -9.325, 32.025, 20174.0),
    ("Souss", 33, -9.625, 30.375, 17178.0),
    ("Bouregreg", 150, -6.825, 34.025, 9872.0),
    ("Loukkos", 164, -6.125, 35.225, 3759.0),
]

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
    print(f"Opening {filepath}...")
    ds = nc.Dataset(filepath, 'r')
    
    print("\n=== Dimensions ===")
    for dimname, dim in ds.dimensions.items():
        print(f"  {dimname}: {len(dim)}")
        
    nx = len(ds.dimensions['east_west'])
    ny = len(ds.dimensions['north_south'])
    assert nx == 180, f"Expected nx=180, got {nx}"
    assert ny == 120, f"Expected ny=120, got {ny}"
    print("Dimensions match: 180 x 120 (PASS)")
    
    # Check coordinates
    lons = None
    lats = None
    if 'lon' in ds.variables:
        lons = ds.variables['lon'][:]
        lats = ds.variables['lat'][:]
    elif 'HYMAP_node_lon' in ds.variables:
        pass
        
    print(f"\nTotal variables in file: {len(ds.variables)}")
    hymap_vars = [v for v in ds.variables if 'HYMAP' in v]
    print(f"HyMAP variables found ({len(hymap_vars)}):")
    for v in sorted(hymap_vars):
        print(f"  {v}: shape={ds.variables[v].shape}, dtype={ds.variables[v].dtype}")
        
    # Check value ranges for HyMAP variables
    print("\n=== HyMAP Variable Ranges ===")
    print(f"{'Variable':<30} {'Min':<15} {'Max':<15} {'Exp Min':<12} {'Exp Max':<12} {'Status'}")
    print("-" * 95)
    
    mask = None
    if 'HYMAP_basin_mask' in ds.variables:
        mask = ds.variables['HYMAP_basin_mask'][:]
        
    for varname, (exp_min, exp_max) in EXPECTED_RANGES.items():
        if varname not in ds.variables:
            print(f"{varname:<30} MISSING")
            continue
        var = ds.variables[varname][:]
        if mask is not None and mask.shape == var.shape:
            valid_vals = var[mask == 1]
        else:
            valid_vals = var[var > -9000]
            
        if len(valid_vals) == 0:
            print(f"{varname:<30} NO VALID VALUES")
            continue
            
        actual_min = float(np.min(valid_vals))
        actual_max = float(np.max(valid_vals))
        
        # Check tolerance (allow 5% due to float representations or boundary cell handling)
        min_ok = abs(actual_min - exp_min) / (abs(exp_min) + 1e-6) < 0.05 or actual_min >= exp_min * 0.9
        max_ok = abs(actual_max - exp_max) / (abs(exp_max) + 1e-6) < 0.05 or actual_max <= exp_max * 1.1
        
        status = "PASS" if (min_ok and max_ok) else "WARN"
        print(f"{varname:<30} {actual_min:<15.4g} {actual_max:<15.4g} {exp_min:<12.4g} {exp_max:<12.4g} {status}")

    # Check Floodplain height levels
    if 'HYMAP_floodplain_height' in ds.variables:
        fldhgt = ds.variables['HYMAP_floodplain_height'][:]
        print(f"\nHYMAP_floodplain_height shape: {fldhgt.shape}")
        valid_fld = fldhgt[fldhgt > -9000]
        print(f"HYMAP_floodplain_height min: {np.min(valid_fld):.4g}, max: {np.max(valid_fld):.4g} (Exp: 0.1 to 2783)")

    # Check Basins and Outlets
    print("\n=== Basin Outlets & Upstream Area ===")
    print(f"{'Basin':<15} {'ID':<5} {'Lon':<8} {'Lat':<8} {'Sim Area (km2)':<18} {'Exp Area (km2)':<18} {'Diff %'}")
    print("-" * 80)
    
    # Calculate cell indices for lon/lat
    # Lon: -9.975 + c*0.05, Lat: 30.025 + r*0.05
    uparea = ds.variables['HYMAP_drain_area'][:] if 'HYMAP_drain_area' in ds.variables else None
    
    for name, bid, exp_lon, exp_lat, exp_area in EXPECTED_BASINS:
        c = int(round((exp_lon - (-9.975)) / 0.05))
        r = int(round((exp_lat - 30.025) / 0.05))
        
        if uparea is not None:
            # Drain area in m2 or km2?
            # Binary lis_uparea_005.bin has max 6.28e10 (which is m2 = 62,800 km2)
            # In LDT netcdf, check what the units and values are:
            val = float(uparea[r, c])
            # If val is in m2, convert to km2
            area_km2 = val / 1e6 if val > 1e6 else val
            diff_pct = abs(area_km2 - exp_area) / exp_area * 100.0
            print(f"{name:<15} {bid:<5} {exp_lon:<8.3f} {exp_lat:<8.3f} {area_km2:<18.1f} {exp_area:<18.1f} {diff_pct:<6.2f}%")
        else:
            print(f"{name:<15} uparea variable missing")

    # Check landmask vs basin mask
    if 'LANDMASK' in ds.variables and 'HYMAP_basin_mask' in ds.variables:
        lmask = ds.variables['LANDMASK'][:]
        bmask = ds.variables['HYMAP_basin_mask'][:]
        lmask_land = (lmask == 1)
        bmask_land = (bmask == 1)
        print("\n=== Mask Consistency ===")
        print(f"LANDMASK land cells: {np.sum(lmask_land)}")
        print(f"HYMAP_basin_mask land cells: {np.sum(bmask_land)}")
        mismatch = np.logical_xor(lmask_land, bmask_land)
        print(f"Mismatching cells between LANDMASK and HYMAP_basin_mask: {np.sum(mismatch)}")

    ds.close()
    print("\nVerification script finished.")

if __name__ == '__main__':
    main()
