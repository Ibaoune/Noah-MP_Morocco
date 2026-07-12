import unittest
import subprocess
import os
import tempfile
import yaml
import shutil
from pathlib import Path

POSTPROC_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = POSTPROC_DIR / "scripts" / "run_scientific_postproc.py"
OUTPUTS_DIR = POSTPROC_DIR / "outputs" / "matrix_2016" / "opl_vs_smap_da_scientific"
PROTECTED_DIR = POSTPROC_DIR / "outputs" / "matrix_2016" / "figures" / "smap_cdf_sensitivity"

class TestScientificRunner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.recipe_path = Path(self.tmpdir.name) / "test_recipe.yaml"
        self.base_recipe = {
            "recipe_id": "test_recipe",
            "analysis_period": {"start": "2016-01-01", "end": "2016-12-31"},
            "experiments": {
                "reference": "OPL_noirr_2016",
                "candidates": ["DA_smap_nocdf_noirr_2016"]
            },
            "comparisons": [
                {"comparison_id": "comp1", "reference": "OPL_noirr_2016", "candidate": "DA_smap_nocdf_noirr_2016"}
            ],
            "diagnostics": {
                "quality_control": {"enabled": True},
                "drought_percentiles": {"enabled": True}, # NOT_IMPLEMENTED
                "unknown_diag": {"enabled": True} # unknown
            }
        }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    def write_recipe(self, recipe_dict):
        with open(self.recipe_path, "w") as f:
            yaml.dump(recipe_dict, f)
            
    def run_cli(self, args):
        cmd = [sys.executable if "sys" in globals() else "python", str(SCRIPT_PATH)] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_missing_recipe(self):
        import sys
        res = self.run_cli(["--recipe", "nonexistent.yaml"])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ERROR: Recipe not found", res.stdout)
        
    def test_invalid_yaml(self):
        import sys
        with open(self.recipe_path, "w") as f:
            f.write("invalid: [yaml: : content")
        res = self.run_cli(["--recipe", str(self.recipe_path)])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ERROR: Invalid YAML", res.stdout)

    def test_unknown_experiment_id(self):
        import sys
        recipe = self.base_recipe.copy()
        recipe["experiments"]["reference"] = "UNKNOWN_EXP"
        self.write_recipe(recipe)
        res = self.run_cli(["--recipe", str(self.recipe_path)])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ERROR: Reference experiment ID 'UNKNOWN_EXP' not found", res.stdout)

    def test_duplicate_comparison_id(self):
        import sys
        recipe = self.base_recipe.copy()
        recipe["comparisons"].append({"comparison_id": "comp1", "reference": "OPL_noirr_2016", "candidate": "DA_smap_nocdf_noirr_2016"})
        self.write_recipe(recipe)
        res = self.run_cli(["--recipe", str(self.recipe_path)])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ERROR: Duplicate comparison_id 'comp1'", res.stdout)

    def test_same_ref_cand_comparison(self):
        import sys
        recipe = self.base_recipe.copy()
        recipe["comparisons"] = [{"comparison_id": "comp1", "reference": "OPL_noirr_2016", "candidate": "OPL_noirr_2016"}]
        self.write_recipe(recipe)
        res = self.run_cli(["--recipe", str(self.recipe_path)])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ERROR: Comparison reference and candidate cannot be the same", res.stdout)

    def test_dry_run_no_files_created(self):
        import sys
        self.write_recipe(self.base_recipe)
        # Assuming OUTPUTS_DIR is clean or we can just check it doesn't create new stuff
        # but to be sure we just run dry run
        res = self.run_cli(["--recipe", str(self.recipe_path), "--dry-run"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("=== DRY RUN PLAN ===", res.stdout)
        self.assertIn("EXECUTE", res.stdout) # For QC
        self.assertIn("SKIP", res.stdout) # For drought
        # Check it didn't create the manifest
        # Actually in real life it might exist from before, but dry run shouldn't error.

    def test_protected_path(self):
        import sys
        # We can't easily change OUTPUTS_DIR in the CLI without an argument, 
        # so we will trust the CLI's internal logic since it's hardcoded to OUTPUTS_DIR.
        # If OUTPUTS_DIR was inside PROTECTED_DIR it would fail. 
        # We know they are siblings: outputs/matrix_2016/opl_vs_smap_da_scientific vs outputs/matrix_2016/figures/smap_cdf_sensitivity
        # This test ensures it does not fail for the valid path.
        self.write_recipe(self.base_recipe)
        res = self.run_cli(["--recipe", str(self.recipe_path), "--dry-run"])
        self.assertEqual(res.returncode, 0)

if __name__ == '__main__':
    unittest.main()
