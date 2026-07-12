"""
Provenance module for recording inputs, commands, and versions
used during execution of the LIS Post-Processing Framework.
"""
import yaml
from datetime import datetime
from typing import Dict, Any, List
import os

class ProvenanceManifest:
    """Manages creation and writing of execution manifests."""
    def __init__(self, recipe_name: str, config: Dict[str, Any]):
        self.manifest = {
            "execution_timestamp": datetime.now().isoformat(),
            "recipe": recipe_name,
            "inputs": [],
            "diagnostics_run": [],
            "outputs": [],
            "config_snapshot": config
        }
        
    def add_input(self, input_type: str, filepath: str, meta: Dict[str, Any] = None):
        self.manifest["inputs"].append({
            "type": input_type,
            "path": filepath,
            "meta": meta or {}
        })
        
    def add_diagnostic_run(self, name: str, status: str):
        self.manifest["diagnostics_run"].append({
            "name": name,
            "status": status
        })

    def add_output(self, filepath: str):
        self.manifest["outputs"].append(filepath)

    def write(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manifest_path = os.path.join(output_dir, f"manifest_{timestamp}.yaml")
        with open(manifest_path, 'w') as f:
            yaml.dump(self.manifest, f, default_flow_style=False)
        return manifest_path
