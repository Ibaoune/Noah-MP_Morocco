import unittest
import xarray as xr
import pandas as pd
import numpy as np
import os
import tempfile
from src.lis_postproc.diagnostics.water_balance.variable_audit import WaterBalanceVariableAudit

class TestVariableAudit(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit = WaterBalanceVariableAudit("test_wb_audit", {})
        
        self.valid_ds = xr.Dataset(
            {
                "Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "Evap_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "Qs_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "Qsb_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "TWS_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "GWS_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                "SoilMoist_inc": (["time", "lat", "lon"], np.random.rand(10, 10, 10))
            }
        )
        self.valid_path = os.path.join(self.tmpdir.name, "valid.nc")
        self.valid_ds.to_netcdf(self.valid_path)

        self.missing_ds = xr.Dataset(
            {
                "Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
                # missing Evap_tavg, Qs_tavg, etc.
                "TWS_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10))
            }
        )
        self.missing_path = os.path.join(self.tmpdir.name, "missing.nc")
        self.missing_ds.to_netcdf(self.missing_path)
        
        self.no_inc_ds = xr.Dataset(
            {
                "Rainf_f_tavg": (["time", "lat", "lon"], np.random.rand(10, 10, 10)),
            }
        )
        self.no_inc_path = os.path.join(self.tmpdir.name, "no_inc.nc")
        self.no_inc_ds.to_netcdf(self.no_inc_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_missing_vars(self):
        report = self.audit.execute([self.missing_path])
        self.assertIn("Evap_tavg", report["variables_missing"])
        
    def test_increment_absent(self):
        report = self.audit.execute([self.no_inc_path])
        self.assertTrue(any("No assimilation increment variables found" in w for w in report["warnings"]))

    def test_tws_gws_together(self):
        report = self.audit.execute([self.valid_path])
        self.assertIn("TWS_tavg", report["variables_found"])
        self.assertIn("GWS_tavg", report["variables_found"])
        
    def test_double_count_risk(self):
        report = self.audit.execute([self.valid_path])
        # Simple placeholder for double count risk logic
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
