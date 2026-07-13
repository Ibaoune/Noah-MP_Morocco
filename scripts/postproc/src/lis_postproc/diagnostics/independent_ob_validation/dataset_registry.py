import os
import yaml
import glob
from pathlib import Path

class DatasetRegistry:
    """Registre de tous les jeux de données de validation et de benchmarking."""
    
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.datasets = {}
        self.load_all_configs()
        
    def load_all_configs(self):
        if not os.path.exists(self.config_dir):
            return
            
        for filepath in glob.glob(os.path.join(self.config_dir, "*.yaml")):
            with open(filepath, 'r') as f:
                cfg = yaml.safe_load(f)
                if not cfg or "dataset_id" not in cfg:
                    continue
                self.datasets[cfg["dataset_id"]] = self._enrich_config(cfg)
                
    def _enrich_config(self, cfg):
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
        raw_path = cfg.get("paths", {}).get("raw", "")
        full_path = project_root / raw_path
        
        cfg["local_full_path"] = str(full_path)
        cfg["readiness_status"] = self._check_readiness(cfg, full_path)
        return cfg
        
    def _check_readiness(self, cfg, full_path):
        if not cfg.get("enabled", False):
            return "SKIPPED_DISABLED"
            
        if not full_path.exists():
            return "MISSING_LOCAL"
            
        files = list(full_path.rglob(cfg.get("files", {}).get("pattern", "*.*")))
        if len(files) == 0:
            return "MISSING_LOCAL"
            
        # Simplification for smoke tests: we assume period matches if files exist
        # In a full implementation, we'd open a sample file and check dates here
        return "READY"
        
    def get_ready_datasets(self):
        return {k: v for k, v in self.datasets.items() if v["readiness_status"] == "READY"}
        
    def get_missing_datasets(self):
        return {k: v for k, v in self.datasets.items() if v["readiness_status"] == "MISSING_LOCAL"}
