"""
Core capabilities module for LIS Post-Processing Framework.
Defines statuses and required capabilities for diagnostics.
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class DataCapabilityStatus(Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

class ImplementationStatus(Enum):
    CREATED_UNTESTED = "CREATED_UNTESTED"
    UNIT_TESTED = "UNIT_TESTED"
    REAL_DATA_TESTED = "REAL_DATA_TESTED"
    INTEGRATION_TESTED = "INTEGRATION_TESTED"
    VALIDATED = "VALIDATED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

@dataclass
class DiagnosticCapability:
    name: str
    implementation_status: ImplementationStatus
    data_status: DataCapabilityStatus
    missing_requirements: List[str]
    notes: Optional[str] = None

    def can_run(self) -> bool:
        return self.implementation_status in [
            ImplementationStatus.UNIT_TESTED, 
            ImplementationStatus.REAL_DATA_TESTED, 
            ImplementationStatus.INTEGRATION_TESTED, 
            ImplementationStatus.VALIDATED
        ] and self.data_status == DataCapabilityStatus.READY

class CapabilityChecker:
    """Base class for evaluating if a diagnostic can run."""
    def evaluate(self, context) -> DiagnosticCapability:
        raise NotImplementedError("evaluate() must be implemented by subclasses.")
