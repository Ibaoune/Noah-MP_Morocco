# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.main
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import yaml
from .assimilation.plot_assimilation import run_assimilation_diagnostics
from .soil_moisture.plot_soil_moisture import run_soil_moisture_diagnostics
from .fluxes.plot_fluxes import run_fluxes_diagnostics
from .groundwater.plot_groundwater import run_groundwater_diagnostics
from .runoff.plot_runoff import run_runoff_diagnostics
from .streamflow.plot_streamflow import run_streamflow_diagnostics
from .validation.plot_validation import run_validation_diagnostics
from .spatial_analysis.plot_spatial_analysis import run_spatial_analysis
from .synthesis.plot_synthesis import run_synthesis

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_opl_multiple_da(data_dict, out_dir):
    """
    Main entry point for OPL Multiple DA module.
    Orchestrates the execution of different blocks based on config.yaml.
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # Load module configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = load_config(config_path)
    active_blocks = config.get('active_blocks', {})

    generated_figures = []

    if active_blocks.get('assimilation', False):
        print("Running Assimilation Diagnostics...")
        block_out_dir = os.path.join(out_dir, "assimilation")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_assimilation_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('soil_moisture', False):
        print("Running Soil Moisture Diagnostics...")
        block_out_dir = os.path.join(out_dir, "soil_moisture")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_soil_moisture_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('fluxes', False):
        print("Running Surface Fluxes Diagnostics...")
        block_out_dir = os.path.join(out_dir, "fluxes")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_fluxes_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('groundwater', False):
        print("Running Groundwater Diagnostics...")
        block_out_dir = os.path.join(out_dir, "groundwater")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_groundwater_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('runoff', False):
        print("Running Runoff Diagnostics...")
        block_out_dir = os.path.join(out_dir, "runoff")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_runoff_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('streamflow', False):
        print("Running Streamflow Diagnostics...")
        block_out_dir = os.path.join(out_dir, "streamflow")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_streamflow_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('validation', False):
        print("Running External Validation Diagnostics...")
        block_out_dir = os.path.join(out_dir, "validation")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_validation_diagnostics(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('spatial_analysis', False):
        print("Running Spatial Analysis...")
        block_out_dir = os.path.join(out_dir, "spatial_analysis")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_spatial_analysis(data_dict, block_out_dir)
        generated_figures.extend(figs)

    if active_blocks.get('synthesis', False):
        print("Running Synthesis...")
        block_out_dir = os.path.join(out_dir, "synthesis")
        os.makedirs(block_out_dir, exist_ok=True)
        figs = run_synthesis(data_dict, block_out_dir)
        generated_figures.extend(figs)

    return generated_figures
