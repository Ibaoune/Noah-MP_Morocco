"""
Registry for scientific diagnostics in the LIS Post-Processing Framework.
"""
from typing import Dict, Any, Type
from .capabilities import CapabilityChecker, DiagnosticCapability

class Diagnostic:
    """Base class for all scientific diagnostics."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    def check_capabilities(self) -> DiagnosticCapability:
        raise NotImplementedError

    def execute(self, context: Dict[str, Any]):
        raise NotImplementedError

class DiagnosticRegistry:
    """Central registry for discovering and instantiating diagnostics."""
    _diagnostics: Dict[str, Type[Diagnostic]] = {}

    @classmethod
    def register(cls, name: str, diagnostic_cls: Type[Diagnostic]):
        cls._diagnostics[name] = diagnostic_cls

    @classmethod
    def get(cls, name: str) -> Type[Diagnostic]:
        if name not in cls._diagnostics:
            raise KeyError(f"Diagnostic '{name}' not found in registry.")
        return cls._diagnostics[name]

    @classmethod
    def list_available(cls) -> Dict[str, Type[Diagnostic]]:
        return cls._diagnostics.copy()
