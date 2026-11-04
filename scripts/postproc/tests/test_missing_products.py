# Author: M. EL Aabaribaoune (@um6p)

import os, sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import unittest
from pathlib import Path
from src.diagnostics.independent_ob_validation.common import check_data_availability

class TestMissingProducts(unittest.TestCase):
    def test_missing_data(self):
        # Un produit inventé ne devrait pas exister
        self.assertFalse(check_data_availability("FAKE_PRODUCT", "soil_moisture"))
        
    def test_existing_data(self):
        # ESA_CCI devrait exister
        self.assertTrue(check_data_availability("ESA_CCI", "soil_moisture"))
        
if __name__ == '__main__':
    unittest.main()
