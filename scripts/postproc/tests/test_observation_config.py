import unittest
import yaml
from pathlib import Path

class TestObservationConfig(unittest.TestCase):
    def test_configs_exist(self):
        config_dir = Path(__file__).resolve().parent.parent / "configs" / "observations"
        self.assertTrue(config_dir.exists())
        
        # Vérifier qu'au moins esa_cci_soil_moisture est là
        cci_file = config_dir / "esa_cci_soil_moisture.yaml"
        self.assertTrue(cci_file.exists())
        
        with open(cci_file, 'r') as f:
            cfg = yaml.safe_load(f)
            
        self.assertEqual(cfg['observation_id'], 'esa_cci_soil_moisture')
        self.assertEqual(cfg['category'], 'soil_moisture')
        self.assertTrue(cfg['enabled'])

if __name__ == '__main__':
    unittest.main()
