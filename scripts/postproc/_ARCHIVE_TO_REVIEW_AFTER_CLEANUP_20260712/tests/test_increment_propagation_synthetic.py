# Author: M. EL Aabaribaoune (@um6p)

import pytest
import pandas as pd
import numpy as np
import xarray as xr
import os
from lis_postproc.diagnostics.increment_propagation.events import build_event_catalog
from lis_postproc.diagnostics.increment_propagation.composites import compute_event_composites, compute_metrics

def test_synthetic_pipeline(tmp_path):
    # Create 100 days of data
    dates = pd.date_range('2016-01-01', periods=100, freq='1D')
    
    # Surface increment with 2 events
    incr = np.zeros(100)
    incr[10] = 5.0
    incr[50] = -3.0
    surf_incr_ts = pd.Series(incr, index=dates)
    
    # Layer responses with exact lags
    l1_resp = np.zeros(100)
    l1_resp[11] = 2.0 # lag 1
    l1_resp[51] = -1.0
    
    l2_resp = np.zeros(100)
    l2_resp[13] = 1.0 # lag 3
    l2_resp[53] = -0.5
    
    l3_resp = np.zeros(100)
    l3_resp[17] = 0.5 # lag 7
    l3_resp[57] = -0.2
    
    response_ts_dict = {
        'layer_1': pd.Series(l1_resp, index=dates),
        'layer_2': pd.Series(l2_resp, index=dates),
        'layer_3': pd.Series(l3_resp, index=dates),
    }
    
    # Run catalog
    catalog = build_event_catalog(surf_incr_ts)
    catalog.to_csv(tmp_path / "event_catalog.csv", index=False)
    assert len(catalog) == 2
    
    # Run composites
    composites = compute_event_composites(response_ts_dict, catalog, max_lag_days=14)
    # Save composite to NC (simulate)
    comp_ds = composites.set_index(['sign', 'variable', 'lag_days']).to_xarray()
    comp_ds.to_netcdf(tmp_path / "event_composites.nc")
    
    assert 'sign' in comp_ds.dims
    assert 'variable' in comp_ds.dims
    assert 'lag_days' in comp_ds.dims
    
    # Run metrics
    df_corr, df_prop, df_pers, df_trans = compute_metrics(surf_incr_ts, response_ts_dict, catalog)
    
    df_corr.to_csv(tmp_path / "lagged_correlations.csv", index=False)
    
    # Print shapes for the report
    print(f"event_catalog.csv shape: {catalog.shape}")
    print(f"event_composites.nc dims: {comp_ds.sizes}")
    print(f"lagged_correlations.csv shape: {df_corr.shape}")
    
    # Verify exact lags
    # Layer 1 max lag = 1
    l1_corr = df_corr[df_corr['variable'] == 'layer_1']
    assert l1_corr.loc[l1_corr['pearson'].idxmax()]['lag_days'] == 1
    
    # Layer 2 max lag = 3
    l2_corr = df_corr[df_corr['variable'] == 'layer_2']
    assert l2_corr.loc[l2_corr['pearson'].idxmax()]['lag_days'] == 3
    
    # Layer 3 max lag = 7
    l3_corr = df_corr[df_corr['variable'] == 'layer_3']
    assert l3_corr.loc[l3_corr['pearson'].idxmax()]['lag_days'] == 7


    # Test plotting
    from lis_postproc.diagnostics.increment_propagation.plotting import generate_all_figures
    import glob
    
    out_dir = tmp_path / "figures"
    generate_all_figures(catalog, composites, df_corr, df_trans, str(out_dir))
    
    png_files = glob.glob(str(out_dir / "*.png"))
    print(f"Generated {len(png_files)} PNG files.")
    assert len(png_files) == 20
