import unittest
from src.lis_postproc.core.diagnostic_registry import DiagnosticRegistry, Diagnostic

class DummyDiagnostic(Diagnostic):
    pass

class TestDiagnosticRegistry(unittest.TestCase):
    def setUp(self):
        # Clear registry for clean tests
        DiagnosticRegistry._diagnostics = {}

    def test_register_and_get(self):
        DiagnosticRegistry.register("dummy", DummyDiagnostic)
        self.assertIn("dummy", DiagnosticRegistry.list_available())
        
        cls = DiagnosticRegistry.get("dummy")
        self.assertEqual(cls, DummyDiagnostic)

    def test_get_missing(self):
        with self.assertRaises(KeyError):
            DiagnosticRegistry.get("missing")

    def test_duplicate_override(self):
        class Dummy2(Diagnostic): pass
        DiagnosticRegistry.register("dummy", DummyDiagnostic)
        DiagnosticRegistry.register("dummy", Dummy2)
        # Should be overriden
        cls = DiagnosticRegistry.get("dummy")
        self.assertEqual(cls, Dummy2)

if __name__ == '__main__':
    unittest.main()
