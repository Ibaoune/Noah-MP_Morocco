# Author: M. EL Aabaribaoune (@um6p)

import pytest
import pandas as pd
import numpy as np
from lis_postproc.diagnostics.increment_propagation.events import build_event_catalog

def test_build_event_catalog():
    # 20 days of data
    dates = pd.date_range('2016-01-01', periods=20, freq='1D')
    
    # Base is small noise
    vals = np.random.uniform(-0.05, 0.05, 20)
    
    # Inject events
    vals[2] = 2.0   # strong positive
    vals[3] = 1.5   # clustered positive
    vals[8] = -1.8  # strong negative
    vals[15] = 0.5  # moderate positive
    
    ts = pd.Series(vals, index=dates)
    
    df_events = build_event_catalog(
        ts, 
        threshold_quantile=0.75, 
        strong_quantile=0.90, 
        min_abs_mm=0.1, 
        min_separation_days=3
    )
    
    assert not df_events.empty
    
    # 2.0 and 1.5 are clustered, so only 2.0 should remain
    dates_kept = df_events['date'].dt.strftime('%Y-%m-%d').tolist()
    assert '2016-01-03' in dates_kept # idx 2
    assert '2016-01-04' not in dates_kept # idx 3 clustered
    assert '2016-01-09' in dates_kept # idx 8
    
    # Check sign
    assert df_events.loc[df_events['date'] == '2016-01-03', 'sign'].iloc[0] == 'positive'
    assert df_events.loc[df_events['date'] == '2016-01-09', 'sign'].iloc[0] == 'negative'

