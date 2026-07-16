import pytest
import os
import pandas as pd
from unittest.mock import patch
from lis_postproc.diagnostics.increment_propagation.loader import extract_time_from_filename

def test_extract_time_from_filename():
    filename = "LIS_DA_EnKF_201606011900_incr.a01.d01.nc"
    t = extract_time_from_filename(filename)
    assert t == pd.Timestamp('2016-06-01 19:00:00')
    
    filename2 = "/path/to/dir/LIS_DA_EnKF_201612311800_incr.a01.d01.nc"
    t2 = extract_time_from_filename(filename2)
    assert t2 == pd.Timestamp('2016-12-31 18:00:00')

def test_extract_time_from_filename_invalid():
    with pytest.raises(ValueError):
        extract_time_from_filename("LIS_DA_EnKF_invalid_incr.a01.d01.nc")

