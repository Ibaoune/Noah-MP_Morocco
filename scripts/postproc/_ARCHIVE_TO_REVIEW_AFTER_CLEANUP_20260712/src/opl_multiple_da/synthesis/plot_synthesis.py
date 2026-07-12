"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.synthesis.plot_synthesis
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from .plot_comprehensive import run_comprehensive_panel

def run_synthesis(data_dict, out_dir):
    """
    Bloc 9: Synthesis
    Objectif: Créer des figures récapitulatives et des matrices de décision.
    """
    generated_figures = run_comprehensive_panel(data_dict, out_dir)
    
    figures_to_stub = [
        ("71_summary_matrix_hydrological_impacts_2016.png", "Summary matrix of SMAP assimilation impacts across hydrological variables"),
        ("72_cdf_vs_nocdf_decision_heatmap_2016.png", "Decision heatmap comparing No-CDF and CDF assimilation performance"),
        ("73_water_balance_summary_opl_nocdf_cdf_2016.png", "Water balance summary for OPL, DA-NoCDF and DA-CDF experiments"),
        ("74_hydrological_consistency_score_2016.png", "Hydrological consistency score of No-CDF and CDF SMAP assimilation"),
        ("75_smap_assimilation_pathway_summary_2016.png", "Pathway of SMAP assimilation impacts from surface soil moisture to routed streamflow"),
        ("76_recommended_figures_for_ahmad_pdf_2016.png", "Recommended figure set for expert feedback on the 2016 SMAP assimilation pilot")
    ]
    
    print("  -> Generating placeholders for Synthesis")
    for fn, title in figures_to_stub:
        p = os.path.join(out_dir, fn)
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, "Placeholder\n(Synthesis figures require all modules)", ha='center', va='center')
        plt.title(title)
        plt.savefig(p, dpi=150)
        plt.close()
        generated_figures.append(p)

    return generated_figures
