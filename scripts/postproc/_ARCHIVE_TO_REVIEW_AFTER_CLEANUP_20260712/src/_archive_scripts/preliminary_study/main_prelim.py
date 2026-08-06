# Author: M. EL Aabaribaoune (@um6p)

import os
import yaml
import sys

from . import plot_figures
from . import pdf_report

def run_preliminary_study(matrix_name, make_figures=True, make_pdf=True):
    """
    Main driver for the Preliminary Study post-processing.
    """
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, "config_prelim_study.yaml")
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration not found at {config_path}")
        return
        
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    print(f"--- Loaded config for Preliminary Study ({matrix_name}) ---")
    
    # Resolve output directories
    proj_root = config['paths']['project_root']
    out_figures_dir = os.path.join(proj_root, config['paths']['dir_figures_out'].format(matrix_name=matrix_name))
    
    os.makedirs(out_figures_dir, exist_ok=True)
    
    from datetime import datetime
    import sys
    sys.path.append(os.path.join(script_dir, "..", "utils"))
    try:
        from utils_eval import get_lis_files
    except ImportError:
        print("Error: Could not import get_lis_files from utils_eval")
        return
        
    start_date = datetime.strptime(config['analysis_period']['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(config['analysis_period']['end_date'], "%Y-%m-%d")
    
    dir_ol = os.path.join(proj_root, config['paths']['dir_output_ol'].format(matrix_name=matrix_name))
    dir_da_nocdf = os.path.join(proj_root, config['paths']['dir_output_da_nocdf'].format(matrix_name=matrix_name))
    dir_da_cdf = os.path.join(proj_root, config['paths']['dir_output_da_cdf'].format(matrix_name=matrix_name))
    
    files_ol = get_lis_files(dir_ol, start_date, end_date)
    files_da_nocdf = get_lis_files(dir_da_nocdf, start_date, end_date)
    files_da_cdf = get_lis_files(dir_da_cdf, start_date, end_date)
    
    data_dict = {
        'files_ol': files_ol,
        'files_da_nocdf': files_da_nocdf,
        'files_da_cdf': files_da_cdf,
        'start_date': start_date,
        'end_date': end_date
    }
    
    log_warnings = []
    
    generated_figures = []
    
    if make_figures:
        print(f"Saving figures to: {out_figures_dir}")
        if config['figures'].get('fig1_assimilation_diagnostics', False):
            f1 = plot_figures.plot_fig1_assimilation_diagnostics(config, out_figures_dir, log_warnings, data_dict)
            generated_figures.append(f1)
            
        if config['figures'].get('fig2_cdf_sensitivity', False):
            f2 = plot_figures.plot_fig2_cdf_sensitivity(config, out_figures_dir, log_warnings, data_dict)
            generated_figures.append(f2)
            
        if config['figures'].get('fig3_vertical_propagation', False):
            f3 = plot_figures.plot_fig3_vertical_propagation(config, out_figures_dir, log_warnings, data_dict)
            generated_figures.append(f3)
            
        if config['figures'].get('fig4_runoff_partitioning', False):
            f4 = plot_figures.plot_fig4_runoff_partitioning(config, out_figures_dir, log_warnings, data_dict)
            generated_figures.append(f4)
            
        if config['figures'].get('fig5_hymap_streamflow', False):
            f5 = plot_figures.plot_fig5_hymap_streamflow(config, out_figures_dir, log_warnings, data_dict)
            if f5:
                generated_figures.append(f5)
                
    if make_pdf and config['features'].get('generate_pdf', True):
        # Even if we didn't generate figures in this run, we might want to compile existing ones
        # For simplicity, we use the ones we just generated
        if not generated_figures:
            # Reconstruct list from config if we are only running make_pdf
            formats = config['features']['figure_format']
            if config['figures'].get('fig1_assimilation_diagnostics', False): generated_figures.append(os.path.join(out_figures_dir, f"fig01_assimilation_diagnostics_2016.{formats}"))
            if config['figures'].get('fig2_cdf_sensitivity', False): generated_figures.append(os.path.join(out_figures_dir, f"fig02_cdf_sensitivity_2016.{formats}"))
            if config['figures'].get('fig3_vertical_propagation', False): generated_figures.append(os.path.join(out_figures_dir, f"fig03_vertical_propagation_et_2016.{formats}"))
            if config['figures'].get('fig4_runoff_partitioning', False): generated_figures.append(os.path.join(out_figures_dir, f"fig04_runoff_partitioning_2016.{formats}"))
            if config['figures'].get('fig5_hymap_streamflow', False): generated_figures.append(os.path.join(out_figures_dir, f"fig05_hymap_streamflow_2016.{formats}"))
        
        pdf_path = pdf_report.generate_pdf_report(config, generated_figures, log_warnings, matrix_name)
        print(f"--- PDF Successfully Generated: {pdf_path} ---")

if __name__ == "__main__":
    # Test execution
    run_preliminary_study("matrix_2016", make_figures=True, make_pdf=True)
