"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: external_validation.main
Description: Validation of model outputs against external observational datasets.
================================================================================
"""
import argparse
import sys
import os

# Ensure the parent directory is in the path to access utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from config import Config

def main():
    parser = argparse.ArgumentParser(description="External Validation Module")
    parser.add_argument("--config", type=str, default="config_external_validation.yaml")
    parser.add_argument("--matrix", type=str, default="matrix_2016")
    parser.add_argument("--output-root", type=str, default="")
    parser.add_argument("--table-root", type=str, default="")
    parser.add_argument("--log-root", type=str, default="")
    args = parser.parse_args()

    # Load Configuration
    cfg = Config(
        config_path=args.config, 
        matrix_id=args.matrix, 
        output_root=args.output_root,
        table_root=args.table_root,
        log_root=args.log_root
    )

    print(f"==================================================")
    print(f" Starting External Validation for {args.matrix}")
    print(f"==================================================")

    if cfg.ACTIVE_PLOTS.get("time_series", False):
        import plot_time_series
        plot_time_series.run(cfg)

    if cfg.ACTIVE_PLOTS.get("spatial_maps", False):
        import plot_spatial_maps
        plot_spatial_maps.run(cfg)

    if cfg.ACTIVE_PLOTS.get("ecosystem_stats", False):
        import evaluate_ecosystems
        evaluate_ecosystems.run(cfg)

    if cfg.ACTIVE_PLOTS.get("streamflow", False):
        import evaluate_streamflow
        evaluate_streamflow.run(cfg)

    if cfg.ACTIVE_PLOTS.get("gldas", False):
        import evaluate_gldas
        evaluate_gldas.run(cfg)

    if cfg.ACTIVE_PLOTS.get("extremes", False):
        import evaluate_extremes
        evaluate_extremes.run(cfg)

    print("==================================================")
    print(" External Validation Completed.")
    print("==================================================")

if __name__ == "__main__":
    main()
