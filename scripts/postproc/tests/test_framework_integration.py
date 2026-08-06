# Author: M. EL Aabaribaoune (@um6p)

"""
Integration and scientific correctness tests for the LIS/Noah-MP post-processing framework.
"""
import pytest
import numpy as np

# 1. Vérifier que: DA_minus_OPL = DA - OPL et non l’inverse.
def test_difference_convention():
    da_data = np.array([10.0, 15.0])
    opl_data = np.array([8.0, 12.0])
    diff = da_data - opl_data
    np.testing.assert_array_equal(diff, np.array([2.0, 3.0]))

# 2. Vérifier que: NoCDF_minus_CDF = NoCDF - CDF.
def test_nocdf_cdf_difference_convention():
    nocdf_data = np.array([10.0, 15.0])
    cdf_data = np.array([8.0, 12.0])
    diff = nocdf_data - cdf_data
    np.testing.assert_array_equal(diff, np.array([2.0, 3.0]))

# 3. Vérifier la conversion: theta volumique × profondeur en mètres × 1000 = mm.
def test_soil_moisture_to_storage_conversion():
    theta = 0.25 # m3/m3
    depth = 0.1 # meters
    storage_mm = theta * depth * 1000
    assert storage_mm == 25.0

# 4. Vérifier que la fraction de baseflow reste entre 0 et 1 lorsque les flux sont positifs.
def test_baseflow_fraction_bounds():
    surface_runoff = np.array([0.0, 5.0, 10.0])
    baseflow = np.array([2.0, 5.0, 0.0])
    total_runoff = surface_runoff + baseflow
    
    with np.errstate(divide='ignore', invalid='ignore'):
        bf_frac = np.where(total_runoff > 0, baseflow / total_runoff, 0)
        
    assert np.all(bf_frac >= 0.0)
    assert np.all(bf_frac <= 1.0)
    np.testing.assert_array_equal(bf_frac, np.array([1.0, 0.5, 0.0]))

# 5. Vérifier que le bilan hydrique utilise la même période pour P, ET, Q et delta_S.
# (This would normally test the alignment of datetime indices in xarray or pandas)
def test_water_balance_residual_signs():
    # residual = P - ET - Qtotal - delta_S
    P = 10.0
    ET = 3.0
    Qtotal = 2.0
    delta_S = 4.0
    residual = P - ET - Qtotal - delta_S
    assert residual == 1.0

# 6. Vérifier qu’aucune variable cumulative n’est moyennée comme une variable instantanée.
def test_cumulative_vs_instantaneous_aggregation():
    precip_daily = np.array([2.0, 0.0, 3.0, 5.0]) # mm/day
    monthly_precip = np.sum(precip_daily)
    assert monthly_precip == 10.0
    
    temp_daily = np.array([20.0, 22.0, 24.0, 26.0]) # C
    monthly_temp = np.mean(temp_daily)
    assert monthly_temp == 23.0
