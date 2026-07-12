import unittest
import xarray as xr
import pandas as pd
import numpy as np
import os
import tempfile
from src.lis_postproc.diagnostics.quality_control.quality_control import QualityControlDiagnostic

class TestQualityControl(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.qc = QualityControlDiagnostic("test_qc", {})
        
        # Valid dataset (leap year complete)
        time = pd.date_range("2016-01-01", "2016-12-31", freq="D")
        self.valid_ds = xr.Dataset(
            {"Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(366, 10, 10))},
            coords={"time": time, "lat": np.linspace(30, 35, 10), "lon": np.linspace(-10, -5, 10)}
        )
        self.valid_ds["Rainf_f_tavg"].attrs["units"] = "kg m-2 s-1"
        self.valid_path = os.path.join(self.tmpdir.name, "valid.nc")
        self.valid_ds.to_netcdf(self.valid_path)

        # Missing coords
        self.missing_coords_ds = xr.Dataset({"Rainf_f_tavg": (["lat", "lon"], np.random.rand(10, 10))})
        self.missing_coords_path = os.path.join(self.tmpdir.name, "missing_coords.nc")
        self.missing_coords_ds.to_netcdf(self.missing_coords_path)
        
        # Incompatible grid
        self.incompat_ds = xr.Dataset(
            {"Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(366, 5, 5))},
            coords={"time": time, "lat": np.linspace(30, 35, 5), "lon": np.linspace(-10, -5, 5)}
        )
        self.incompat_path = os.path.join(self.tmpdir.name, "incompat.nc")
        self.incompat_ds.to_netcdf(self.incompat_path)
        
        # Missing day
        time_missing = time.drop(pd.Timestamp("2016-02-29"))
        self.missing_day_ds = xr.Dataset(
            {"Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(365, 10, 10))},
            coords={"time": time_missing, "lat": np.linspace(30, 35, 10), "lon": np.linspace(-10, -5, 10)}
        )
        self.missing_day_path = os.path.join(self.tmpdir.name, "missing_day.nc")
        self.missing_day_ds.to_netcdf(self.missing_day_path)
        
        # Duplicated day
        time_dup = time.append(pd.DatetimeIndex(["2016-01-01"]))
        self.dup_day_ds = xr.Dataset(
            {"Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(367, 10, 10))},
            coords={"time": time_dup, "lat": np.linspace(30, 35, 10), "lon": np.linspace(-10, -5, 10)}
        )
        self.dup_day_path = os.path.join(self.tmpdir.name, "dup_day.nc")
        self.dup_day_ds.to_netcdf(self.dup_day_path)
        
        # Unexpected unit
        self.bad_unit_ds = xr.Dataset(
            {"Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(366, 10, 10))},
            coords={"time": time, "lat": np.linspace(30, 35, 10), "lon": np.linspace(-10, -5, 10)}
        )
        self.bad_unit_ds["Rainf_f_tavg"].attrs["units"] = "bad_unit"
        self.bad_unit_path = os.path.join(self.tmpdir.name, "bad_unit.nc")
        self.bad_unit_ds.to_netcdf(self.bad_unit_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_missing_time_coord(self):
        report = self.qc.execute([self.missing_coords_path])
        self.assertTrue(any("Missing time coordinate" in e for e in report["errors"]))

    def test_leap_year_complete(self):
        report = self.qc.execute([self.valid_path])
        # Add basic dummy check logic into QC class in future or assume it returns metadata
        self.assertEqual(len(report["errors"]), 0)

    def test_missing_day(self):
        # Even if not fully implemented in QC class yet, test structure is here
        pass

    def test_duplicate_day(self):
        pass

    def test_incompatible_grid(self):
        pass

    def test_unexpected_unit(self):
        pass

if __name__ == '__main__':
    unittest.main()
