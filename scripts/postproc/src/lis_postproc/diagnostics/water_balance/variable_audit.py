"""
Water Balance Variable Audit Diagnostic for LIS Post-Processing Framework.
Checks variables required for the internal water balance closure.
"""
from typing import Dict, Any, List
import xarray as xr
from ...core.diagnostic_registry import Diagnostic, DiagnosticCapability
from ...core.capabilities import DataCapabilityStatus, ImplementationStatus

class WaterBalanceVariableAudit(Diagnostic):
    """
    Validates variables needed for water balance: Rainf_f_tavg, Evap_tavg, Qs_tavg, Qsb_tavg, TWS_tavg, GWS_tavg.
    Highlights risks of double counting or missing increments for assimilation runs.
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

    def check_capabilities(self, input_files: List[str]) -> DiagnosticCapability:
        if not input_files:
            return DiagnosticCapability(
                name=self.name,
                implementation_status=ImplementationStatus.IMPLEMENTED,
                data_status=DataCapabilityStatus.FAILED,
                missing_requirements=["Input files list is empty"]
            )
        return DiagnosticCapability(
            name=self.name,
            implementation_status=ImplementationStatus.IMPLEMENTED,
            data_status=DataCapabilityStatus.READY,
            missing_requirements=[]
        )

    def execute(self, input_files: List[str]) -> Dict[str, Any]:
        report = {
            "variables_found": [],
            "variables_missing": [],
            "warnings": []
        }

        required_vars = ["Rainf_f_tavg", "Evap_tavg", "Qs_tavg", "Qsb_tavg", "TWS_tavg", "GWS_tavg"]

        if input_files:
            try:
                ds = xr.open_dataset(input_files[0])
                for var in required_vars:
                    if var in ds.data_vars:
                        report["variables_found"].append(var)
                    else:
                        report["variables_missing"].append(var)
                
                # Check for assimilation increments
                inc_vars = [v for v in ds.data_vars if "inc" in v.lower()]
                if not inc_vars:
                    report["warnings"].append("No assimilation increment variables found in output. Closure might fail for DA runs.")
                else:
                    report["variables_found"].extend(inc_vars)

                ds.close()
            except Exception as e:
                report["warnings"].append(f"Failed to read sample file {input_files[0]}: {str(e)}")
        
        return report
