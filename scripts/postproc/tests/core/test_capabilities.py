import unittest
from src.lis_postproc.core.capabilities import DiagnosticCapability, ImplementationStatus, DataCapabilityStatus

class TestCapabilities(unittest.TestCase):
    def test_status_transitions(self):
        # A diagnostic with missing data should not be runnable even if implemented
        cap1 = DiagnosticCapability(
            name="test_diag",
            implementation_status=ImplementationStatus.VALIDATED,
            data_status=DataCapabilityStatus.FAILED,
            missing_requirements=["file.nc"]
        )
        self.assertFalse(cap1.can_run())

        # A diagnostic that is planned but data is ready cannot run
        cap2 = DiagnosticCapability(
            name="test_diag",
            implementation_status=ImplementationStatus.NOT_IMPLEMENTED,
            data_status=DataCapabilityStatus.READY,
            missing_requirements=[]
        )
        self.assertFalse(cap2.can_run())

        # An existing diagnostic with ready data can run
        cap3 = DiagnosticCapability(
            name="test_diag",
            implementation_status=ImplementationStatus.VALIDATED,
            data_status=DataCapabilityStatus.READY,
            missing_requirements=[]
        )
        self.assertTrue(cap3.can_run())

if __name__ == '__main__':
    unittest.main()
