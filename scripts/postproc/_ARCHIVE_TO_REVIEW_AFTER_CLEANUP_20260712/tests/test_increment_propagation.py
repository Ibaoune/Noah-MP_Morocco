# Author: M. EL Aabaribaoune (@um6p)

import numpy as np
import pandas as pd
import pytest
from datetime import datetime, timedelta

from src.lis_postproc.diagnostics.increment_propagation.utils import (
    volumetric_sm_to_storage,
    compute_layer_storage_difference,
    compute_integrated_rzsm,
    compute_integrated_storage,
    compute_integrated_storage_response,
    detect_increment_events,
    extract_event_windows,
    compute_event_composite,
    compute_bootstrap_interval,
    compute_lagged_correlation,
    compute_peak_response_lag,
    compute_persistence_duration,
    compute_efolding_time,
    compute_transfer_efficiency,
    compute_cumulative_flux_response,
    control_precipitation_events
)

def test_volumetric_sm_to_storage():
    # 0.1 m3/m3 * 0.1m * 1000 = 10 mm
    res = volumetric_sm_to_storage(0.1, 0.1)
    assert np.isclose(res, 10.0)

def test_compute_integrated_rzsm():
    layers = [np.array([0.1]), np.array([0.2]), np.array([0.3])]
    thicknesses = [0.1, 0.3, 0.6]
    # (0.1*0.1 + 0.2*0.3 + 0.3*0.6) / 1.0 = (0.01 + 0.06 + 0.18) = 0.25
    rzsm = compute_integrated_rzsm(layers, thicknesses, max_depth_m=1.0)
    assert np.isclose(rzsm[0], 0.25)
    
    # Check ValueError if thicknesses don't match max_depth
    with pytest.raises(ValueError):
        compute_integrated_rzsm(layers, [0.1, 0.3, 0.5], max_depth_m=1.0)

def test_compute_integrated_storage():
    layers = [np.array([0.1]), np.array([0.2]), np.array([0.3])]
    thicknesses = [0.1, 0.3, 0.6]
    # RZSM = 0.25 m3/m3. Storage = 0.25 * 1.0 * 1000 = 250 mm
    storage = compute_integrated_storage(layers, thicknesses, max_depth_m=1.0)
    assert np.isclose(storage[0], 250.0)

def test_detect_increment_events():
    dates = pd.date_range("2016-01-01", periods=10, freq="D")
    increments = np.array([0.0, 5.0, 2.0, 0.0, -6.0, 0.0, 1.0, 10.0, 8.0, 0.0])
    
    # sign="positive", quantile=0.5, min_abs=0.1, min_sep=3
    # pos: 5.0 (idx 1), 2.0 (idx 2), 1.0 (idx 6), 10.0 (idx 7), 8.0 (idx 8)
    # declustered pos: max of cluster 1 (5.0, 2.0) -> 5.0. cluster 2 (1.0, 10.0, 8.0) -> 10.0.
    events = detect_increment_events(increments, dates, threshold_method="absolute", 
                                     threshold_quantile=0.5, minimum_separation_days=2, sign="positive")
    
    assert len(events) == 2
    assert events.iloc[0]['increment'] == 5.0
    assert events.iloc[1]['increment'] == 10.0
    
    events_neg = detect_increment_events(increments, dates, threshold_method="absolute", 
                                         threshold_quantile=0.5, sign="negative")
    assert len(events_neg) == 1
    assert events_neg.iloc[0]['increment'] == -6.0

def test_extract_event_windows():
    data = np.arange(10)
    dates = pd.date_range("2016-01-01", periods=10, freq="D")
    event_dates = pd.DatetimeIndex(["2016-01-02", "2016-01-05"])
    
    windows = extract_event_windows(data, dates, event_dates, start_lag_days=0, end_lag_days=3)
    assert windows.shape == (2, 4)
    # event 1 at 2016-01-02 (idx 1), lag 0-3 -> [1, 2, 3, 4]
    assert np.allclose(windows[0], [1, 2, 3, 4])
    # event 2 at 2016-01-05 (idx 4), lag 0-3 -> [4, 5, 6, 7]
    assert np.allclose(windows[1], [4, 5, 6, 7])

def test_compute_lagged_correlation():
    np.random.seed(42)
    # create synthetic signal where response is surface delayed by 2 days
    inc = np.random.randn(50)
    resp = np.roll(inc, 2)
    resp[:2] = 0 # zero out wrapped around
    
    # Min samples 20, max_lag 5
    corrs, pvals = compute_lagged_correlation(inc, resp, max_lag_days=5, minimum_samples=20)
    assert len(corrs) == 6
    # Lag 2 should have highest correlation (close to 1)
    assert np.argmax(corrs) == 2
    assert corrs[2] > 0.9

def test_compute_peak_response_lag():
    comp = np.array([0, 1, 5, 2, 1])
    lag = compute_peak_response_lag(comp)
    assert lag == 2

def test_compute_persistence_duration():
    comp = np.array([0, 10, 8, 5, 2, 1, 0])
    # peak at lag 1 (10). Threshold 0.2*10 = 2.0
    # lags: 1=10, 2=8, 3=5, 4=2(threshold), 5=1(<thresh), 6=0(<thresh)
    # consecutive_days=2. so at lag 6, we have 2 days < 2.0 (lags 5 and 6).
    # it dropped below at lag 5.
    dur = compute_persistence_duration(comp, threshold_fraction=0.20, consecutive_days=2)
    assert dur == 5
    
def test_compute_efolding_time():
    comp = np.array([0, 10, 3.6, 2.0])
    # threshold = 10 / e = 3.67
    # drop below at lag 2 (3.6)
    ef = compute_efolding_time(comp)
    assert ef == 2

def test_compute_transfer_efficiency():
    eff = compute_transfer_efficiency(5.0, 10.0, minimum_denominator_mm=0.1)
    assert np.isclose(eff, 0.5)
    eff_nan = compute_transfer_efficiency(5.0, 0.05, minimum_denominator_mm=0.1)
    assert np.isnan(eff_nan)

def test_compute_cumulative_flux_response():
    da = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    opl = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    # diff = [1, 2, 3, 4, 5]
    # cum sum over window=2 (lag 1)
    # idx 0: 1+2 = 3
    # idx 1: 2+3 = 5
    # idx 2: 3+4 = 7
    cum = compute_cumulative_flux_response(da, opl, accumulation_windows_days=(1,))
    assert cum.shape == (1, 5)
    assert np.allclose(cum[0, :3], [3, 5, 7])

def test_control_precipitation_events():
    events_df = pd.DataFrame({'date': pd.to_datetime(["2016-01-01", "2016-01-05"])})
    dates = pd.date_range("2016-01-01", periods=10, freq="D")
    precip_ts = np.array([0, 0, 0, 0, 0, 10, 0, 0, 0, 0])
    
    # Event 1 (idx 0): precip on 01-01 to 01-04 is 0. Mean = 0 < 1.0 (dry)
    # Event 2 (idx 4): precip on 01-05 to 01-08 includes 10 on 01-06. Mean = 10/4 = 2.5 >= 1.0 (wet)
    res = control_precipitation_events(events_df, precip_ts, dates, accumulation_window_days=3, dry_event_threshold_mm_day=1.0)
    
    assert res.iloc[0]['is_wet'] == False
    assert res.iloc[1]['is_wet'] == True
