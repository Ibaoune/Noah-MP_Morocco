# Author: M. EL Aabaribaoune (@um6p)

import pytest
import pandas as pd
import numpy as np
from lis_postproc.diagnostics.increment_propagation.composites import compute_event_composites, compute_metrics

def test_compute_event_composites():
    dates = pd.date_range('2016-01-01', periods=20, freq='1D')
    
    events_df = pd.DataFrame({
        'date': [pd.Timestamp('2016-01-05')],
        'sign': ['positive'],
        'increment': [2.0],
        'abs_increment': [2.0],
        'strong': [True]
    })
    
    # Response peaks at lag 1
    resp = np.zeros(20)
    resp[5] = 1.0 # 2016-01-06 is index 5
    ts_dict = {'layer_1': pd.Series(resp, index=dates)}
    
    df_comp = compute_event_composites(ts_dict, events_df, max_lag_days=5)
    
    assert not df_comp.empty
    assert len(df_comp) == 6 # lag 0 to 5
    
    val_lag_1 = df_comp.loc[df_comp['lag_days'] == 1, 'response_median'].iloc[0]
    assert val_lag_1 == 1.0

def test_compute_metrics():
    dates = pd.date_range('2016-01-01', periods=30, freq='1D')
    incr = pd.Series(np.random.randn(30), index=dates)
    resp = incr.shift(1).fillna(0) # perfect correlation at lag 1
    
    events_df = pd.DataFrame()
    df_corr, df_prop, df_pers, df_trans = compute_metrics(incr, {'resp': resp}, events_df, max_lag_days=3)
    
    assert not df_corr.empty
    
    lag1_corr = df_corr.loc[df_corr['lag_days'] == 1, 'pearson'].iloc[0]
    assert lag1_corr > 0.99

