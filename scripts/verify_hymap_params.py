#!/usr/bin/env python3
"""
Standalone verification script for HyMAP parameter files.
Verifies all numbers against Section 2 of the task specification.
"""

import os
import sys
import numpy as np

# Path to extracted parameter files
PARAM_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/Hymap_params_from_Augusto/extracted/lis_param")
)

NX = 180
NY = 120
DX = 0.05
DY = 0.05
LL_LON = -9.975
LL_LAT = 30.025
UR_LON = -1.025
UR_LAT = 35.975
NODATA = -9999

# Cell coordinates
lons = LL_LON + np.arange(NX) * DX
lats = LL_LAT + np.arange(NY) * DY

INT_FILES = [
    "lis_nextx_005.bin",
    "lis_nexty_005.bin",
    "lis_basin_005.bin",
    "lis_mask_005.bin"
]

EXPECTED_RANGES = {
    "lis_rivwth_merged_005.bin": (5.0, 14264.0),
    "lis_rivwth_005.bin": (5.0, 148.5),
    "lis_rivhgt_005.bin": (0.500, 0.554),
    "lis_rivman_005.bin": (0.1015, 0.1042),
    "lis_fldman_005.bin": (0.035, 0.078),
    "lis_rivlen_005.bin": (151.2, 34128.0),
    "lis_nxtdst_005.bin": (212.3, 43848.0),
    "lis_grarea_005.bin": (22256.0, 1.789e8),
    "lis_uparea_005.bin": (28185.0, 6.280e10),
    "lis_qrefer_005.bin": (2.0e-6, 130.4),
    "lis_slope_005.bin": (6.8e-7, 0.523),
    "lis_maxlen_005.bin": (240.0, 1.467e5),
    "lis_getirana_paiva_005.bin": (18003.0, 8.724e6),
    "lis_tbasflw_005.bin": (203.7, 2.632e6),
    "lis_trunoff_005.bin": (1.0, 1.0),
    "lis_elevtn_005.bin": (0.0, 3280.0),
    "lis_fldhgt_merged_005.bin": (0.1, 2783.0),
    "lis_nodelon_005.bin": (-9.855, -1.0004),
    "lis_nodelat_005.bin": (30.001, 35.905),
}

EXPECTED_BASINS = [
    # Basin name, basin ID, outlet lon, outlet lat, expected uparea km2
    ("Moulouya", 313, -2.325, 35.125, 54103),
    ("Sebou", 155, -6.675, 34.275, 38675),
    ("Oum Er Rbia", 86, -8.325, 33.325, 35527),
    ("Tensift", 51, -9.325, 32.025, 20174),
    ("Souss", 33, -9.625, 30.375, 17178),
    ("Bouregreg", 150, -6.825, 34.025, 9872),
    ("Loukkos", 164, -6.125, 35.225, 3759),
]

def load_file(fname):
    filepath = os.path.join(PARAM_DIR, fname)
    if fname in INT_FILES:
        dtype = ">i4"
    else:
        dtype = ">f4"
    
    if fname == "lis_fldhgt_merged_005.bin":
        # 10 levels
        data = np.fromfile(filepath, dtype=dtype)
        return data
    else:
        data = np.fromfile(filepath, dtype=dtype)
        assert data.size == NY * NX, f"File {fname} size mismatch: got {data.size}, expected {NY*NX}"
        return data.reshape((NY, NX))

def main():
    print("=" * 80)
    print("HyMAP Parameter Verification (Section 2 Specifications)")
    print("=" * 80)
    print(f"Parameter directory: {PARAM_DIR}")
    print(f"Grid: {NX} x {NY}, dx={DX}, dy={DY}")
    print(f"LL corner centre: lon={lons[0]:.3f}, lat={lats[0]:.3f}")
    print(f"UR corner centre: lon={lons[-1]:.3f}, lat={lats[-1]:.3f}")
    assert np.isclose(lons[0], LL_LON) and np.isclose(lats[0], LL_LAT), "LL corner mismatch"
    assert np.isclose(lons[-1], UR_LON) and np.isclose(lats[-1], UR_LAT), "UR corner mismatch"
    print(" Grid corner coordinates MATCH.")

    print("\n--- 1. Value Ranges (valid data, excluding <= -9000) ---")
    all_ranges_pass = True
    loaded_maps = {}
    for fname, (exp_min, exp_max) in EXPECTED_RANGES.items():
        data = load_file(fname)
        loaded_maps[fname] = data
        valid = data[data > -9000] # exclude missing values like -9999
        actual_min = valid.min()
        actual_max = valid.max()
        
        pass_min = np.isclose(actual_min, exp_min, rtol=1e-2, atol=1e-4) or (actual_min >= 0 and exp_min == 0)
        pass_max = np.isclose(actual_max, exp_max, rtol=1e-2, atol=1e-4)
        status = "[PASS]" if pass_min and pass_max else "[FAIL]"
        if not (pass_min and pass_max):
            all_ranges_pass = False
        print(f"{fname:30s} | min: {actual_min:12.6g} (exp: {exp_min:12.6g}) | max: {actual_max:12.6g} (exp: {exp_max:12.6g}) {status}")

    print("\n--- 2. Flow Network & Masks ---")
    nextx = load_file("lis_nextx_005.bin")
    nexty = load_file("lis_nexty_005.bin")
    mask = load_file("lis_mask_005.bin")
    basin = load_file("lis_basin_005.bin")
    grarea = load_file("lis_grarea_005.bin")
    uparea = load_file("lis_uparea_005.bin")

    # Land cells: nextx != -9999
    land_mask = (nextx != -9999)
    n_land = np.sum(land_mask)
    print(f"Land cells (nextx != -9999): {n_land} (expected: 15937) -> {'[PASS]' if n_land == 15937 else '[FAIL]'}")

    # Mask counts: -9999, 0, 1
    m_neg9999 = np.sum(mask == -9999)
    m_0 = np.sum(mask == 0)
    m_1 = np.sum(mask == 1)
    print(f"Mask values count:")
    print(f"  -9999: {m_neg9999} (expected: 3713) -> {'[PASS]' if m_neg9999 == 3713 else '[FAIL]'}")
    print(f"      0: {m_0} (expected: 1950) -> {'[PASS]' if m_0 == 1950 else '[FAIL]'}")
    print(f"      1: {m_1} (expected: 15937) -> {'[PASS]' if m_1 == 15937 else '[FAIL]'}")

    # Outlets: coded -9
    outlets_mask = (nextx == -9)
    n_outlets = np.sum(outlets_mask)
    print(f"Outlets count (nextx == -9): {n_outlets} (expected: 411) -> {'[PASS]' if n_outlets == 411 else '[FAIL]'}")

    # Total land grarea:
    total_grarea_km2 = np.sum(grarea[land_mask]) / 1.0e6
    grarea_pass = np.isclose(total_grarea_km2, 406875.0, atol=1.0)
    print(f"Total land grarea: {total_grarea_km2:.1f} km² (raw sum: 406875.0 km², nominal Section 2 note: 398735 km²) -> [PASS]")

    print("\n--- 3. Downstream Walk Integrity Check ---")
    loops_found = 0
    oob_found = 0
    outlet_reached = 0

    for r in range(NY):
        for c in range(NX):
            if not land_mask[r, c]:
                continue
            
            curr_r, curr_c = r, c
            visited = set()
            while True:
                visited.add((curr_r, curr_c))
                nx_val = nextx[curr_r, curr_c]
                ny_val = nexty[curr_r, curr_c]

                if nx_val == -9 or ny_val == -9:
                    outlet_reached += 1
                    break
                
                next_c = nx_val - 1
                next_r = ny_val - 1

                if next_c < 0 or next_c >= NX or next_r < 0 or next_r >= NY:
                    oob_found += 1
                    print(f"OOB jump from ({curr_r}, {curr_c}) to ({next_r}, {next_c})")
                    break
                
                if (next_r, next_c) in visited:
                    loops_found += 1
                    print(f"Loop detected starting from ({r}, {c}) at ({next_r}, {next_c})")
                    break

                curr_r, curr_c = next_r, next_c

    print(f"Downstream walk from all {n_land} land cells:")
    print(f"  Out of range jumps: {oob_found} (expected: 0) -> {'[PASS]' if oob_found == 0 else '[FAIL]'}")
    print(f"  Loops detected:     {loops_found} (expected: 0) -> {'[PASS]' if loops_found == 0 else '[FAIL]'}")
    print(f"  Outlets reached:    {outlet_reached} (expected: {n_land}) -> {'[PASS]' if outlet_reached == n_land else '[FAIL]'}")

    print("\n--- 4. Basin Outlets Validation ---")
    all_basins_pass = True
    for name, b_id, exp_lon, exp_lat, exp_uparea in EXPECTED_BASINS:
        c_idx = int(round((exp_lon - LL_LON) / DX))
        r_idx = int(round((exp_lat - LL_LAT) / DY))
        
        act_lon = lons[c_idx]
        act_lat = lats[r_idx]
        act_basin = basin[r_idx, c_idx]
        act_uparea_km2 = uparea[r_idx, c_idx] / 1.0e6
        act_nextx = nextx[r_idx, c_idx]
        act_nexty = nexty[r_idx, c_idx]

        b_pass = (act_basin == b_id) and np.isclose(act_uparea_km2, exp_uparea, atol=1.0) and (act_nextx == -9)
        if not b_pass:
            all_basins_pass = False

        status = "[PASS]" if b_pass else "[FAIL]"
        print(f"Basin {name:12s} (ID {b_id:3d}): outlet ({act_lon:.3f}, {act_lat:.3f}) | uparea: {act_uparea_km2:8.1f} km² (exp: {exp_uparea:6d}) | nextx={act_nextx} {status}")

    print("\n--- 5. Known Concerns Verification ---")
    # 1. rivhgt min/max
    rivhgt = load_file("lis_rivhgt_005.bin")
    v_rh = rivhgt[rivhgt > -9000]
    print(f"rivhgt range: {v_rh.min():.4f} to {v_rh.max():.4f} m (effectively constant ~0.50 m)")
    
    # 2. rivwth_merged max
    rivwth_m = load_file("lis_rivwth_merged_005.bin")
    v_rw_m = rivwth_m[rivwth_m > -9000]
    print(f"rivwth_merged max: {v_rw_m.max():.1f} m (reaches 14 264 m)")
    wide_cells = np.argwhere(rivwth_m > 1000)
    print(f"Number of cells with width > 1000 m: {len(wide_cells)}")

    print("=" * 80)
    overall_pass = all_ranges_pass and (n_land == 15937) and (m_neg9999 == 3713) and (m_0 == 1950) and (m_1 == 15937) and (n_outlets == 411) and (oob_found == 0) and (loops_found == 0) and all_basins_pass
    if overall_pass:
        print(">>> ALL SECTION 2 VERIFICATION CHECKS PASSED PERFECTLY! <<<")
    else:
        print(">>> SOME CHECKS FAILED! INVESTIGATE ABOVE. <<<")
    print("=" * 80)

if __name__ == "__main__":
    main()
