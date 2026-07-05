import os
import yaml
from datetime import datetime

class Config:
    def __init__(self, config_path, matrix_id="matrix_2016", output_root=None, table_root=None, log_root=None):
        with open(config_path, 'r') as f:
            self.yaml_cfg = yaml.safe_load(f)

        self.PROJECT_ROOT = self.yaml_cfg.get("project_root", "")
        self.MODULE_NAME = self.yaml_cfg.get("module_name", "external_validation")

        # Set up output directories
        base_output = output_root if output_root else os.path.join(self.PROJECT_ROOT, "scripts/postproc/figures")
        base_table = table_root if table_root else os.path.join(self.PROJECT_ROOT, "scripts/postproc/tables")
        base_log = log_root if log_root else os.path.join(self.PROJECT_ROOT, "scripts/postproc/logs")

        self.DIR_FIGURES = os.path.join(base_output, matrix_id, self.MODULE_NAME)
        self.DIR_TABLES = os.path.join(base_table, matrix_id, self.MODULE_NAME)
        self.DIR_LOGS = os.path.join(base_log, matrix_id, self.MODULE_NAME)

        os.makedirs(self.DIR_FIGURES, exist_ok=True)
        os.makedirs(self.DIR_TABLES, exist_ok=True)
        os.makedirs(self.DIR_LOGS, exist_ok=True)

        # Retrieve matrix-specific config
        run_modes = self.yaml_cfg.get("run_modes", [])
        mode_cfg = next((m for m in run_modes if m["id"] == matrix_id), None)
        if not mode_cfg:
            raise ValueError(f"Matrix {matrix_id} not found in config.")

        self.START_DATE = datetime.strptime(mode_cfg["start_date"], "%Y-%m-%d")
        self.END_DATE = datetime.strptime(mode_cfg["end_date"], "%Y-%m-%d")
        self.DIR_OUTPUT_OL = os.path.join(self.PROJECT_ROOT, mode_cfg["experiment_ol"])
        self.DIR_OUTPUT_DA = os.path.join(self.PROJECT_ROOT, mode_cfg["experiment_da"])

        # Domain
        domain = self.yaml_cfg.get("domain", {})
        self.DOMAIN_LON_MIN = domain.get("lon_min", -10.0)
        self.DOMAIN_LON_MAX = domain.get("lon_max", -1.0)
        self.DOMAIN_LAT_MIN = domain.get("lat_min", 30.0)
        self.DOMAIN_LAT_MAX = domain.get("lat_max", 36.0)

        # Validation Data
        val_data = self.yaml_cfg.get("validation_data", {})
        self.LDT_FILE = os.path.join(self.PROJECT_ROOT, val_data.get("land_cover", ""))
        self.DIR_OBS_WAPOR = os.path.join(self.PROJECT_ROOT, val_data.get("wapor", ""))
        self.DIR_OBS_FLUXSAT = os.path.join(self.PROJECT_ROOT, val_data.get("fluxsat", ""))
        self.DIR_OBS_GLDAS = os.path.join(self.PROJECT_ROOT, val_data.get("gldas", ""))
        self.DIR_OBS_INSITU = os.path.join(self.PROJECT_ROOT, val_data.get("streamflow", ""))
        self.FILE_GRACE = os.path.join(self.PROJECT_ROOT, val_data.get("grace", ""))
        self.DIR_ASCAT = os.path.join(self.PROJECT_ROOT, val_data.get("ascat", ""))
        self.DIR_OBS_MODIS_LAI = os.path.join(self.PROJECT_ROOT, val_data.get("modis_lai", ""))

        self.ACTIVE_PLOTS = self.yaml_cfg.get("active_plots", {})

        # Plotting configuration
        self.PLOT_RC_PARAMS = {
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'figure.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.format': 'png'
        }

        self.COLORS = {
            'OL': '#1f77b4',     # Blue
            'DA': '#ff7f0e',     # Orange
            'OBS': '#2ca02c',    # Green
            'DIFF': 'coolwarm',
            'AGRI': '#e377c2',
            'FOREST': '#2ca02c',
            'SHRUB': '#8c564b',
            'GRASS': '#bcbd22'
        }
