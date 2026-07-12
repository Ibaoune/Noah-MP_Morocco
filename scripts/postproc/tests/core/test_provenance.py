import unittest
import os
import tempfile
import yaml
from src.lis_postproc.core.provenance import ProvenanceManifest

class TestProvenance(unittest.TestCase):
    def test_manifest_write_read(self):
        config = {"domain": "NorthMor", "recipe": "test"}
        manifest = ProvenanceManifest("test_recipe", config)
        manifest.add_input("LIS_OUTPUT", "/path/to/lis.nc")
        manifest.add_diagnostic_run("QualityControl", "SUCCESS")
        manifest.add_output("/path/to/fig.png")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = manifest.write(tmpdir)
            self.assertTrue(os.path.exists(filepath))
            
            # Re-read and check without loss of info
            with open(filepath, 'r') as f:
                loaded = yaml.safe_load(f)
                
            self.assertEqual(loaded["recipe"], "test_recipe")
            self.assertEqual(loaded["config_snapshot"]["domain"], "NorthMor")
            self.assertEqual(len(loaded["inputs"]), 1)
            self.assertEqual(loaded["inputs"][0]["path"], "/path/to/lis.nc")
            self.assertEqual(len(loaded["diagnostics_run"]), 1)
            self.assertEqual(loaded["outputs"][0], "/path/to/fig.png")

if __name__ == '__main__':
    unittest.main()
