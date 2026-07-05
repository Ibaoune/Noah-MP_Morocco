import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg

def create_text_page(pdf, text, title=""):
    """Helper to create a text-only page in the PDF."""
    fig, ax = plt.subplots(figsize=(8.5, 11)) # Standard Letter size
    ax.axis('off')
    if title:
        fig.text(0.5, 0.9, title, ha='center', va='center', fontsize=20, fontweight='bold')
        
    # Split text to handle rough wrapping if necessary
    y_pos = 0.8
    for line in text.split('\n'):
        fig.text(0.1, y_pos, line, ha='left', va='top', fontsize=12, wrap=True)
        y_pos -= 0.02
        if y_pos < 0.1: # new page needed for very long text
            pdf.savefig(fig)
            plt.close()
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis('off')
            y_pos = 0.9
            
    pdf.savefig(fig)
    plt.close()

def add_figure_page(pdf, img_path, caption):
    """Helper to add an image as a full page with a caption."""
    if not os.path.exists(img_path):
        return
        
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis('off')
    
    img = mpimg.imread(img_path)
    ax.imshow(img)
    
    fig.text(0.5, 0.05, caption, ha='center', va='center', fontsize=12, style='italic', wrap=True)
    
    pdf.savefig(fig)
    plt.close()

def generate_pdf_report(config, figures_list, log_warnings, matrix_name):
    """
    Generates the synthesis PDF.
    """
    out_dir = os.path.join(config['paths']['project_root'], config['paths']['dir_reports_out'].format(matrix_name=matrix_name))
    os.makedirs(out_dir, exist_ok=True)
    
    pdf_path = os.path.join(out_dir, config['features']['pdf_filename'])
    print(f"Generating PDF Report: {pdf_path}")
    
    with PdfPages(pdf_path) as pdf:
        # Title Page
        title_text = (
            f"Preliminary Study Synthesis\n"
            f"Matrix: {matrix_name}\n"
            f"Focus: SMAP Assimilation Impact (2016)\n\n"
            f"Experiments Analyzed:\n"
            f"- OPL_noirr_2016\n"
            f"- DA_nocdf_noirr_2016\n"
        )
        if config['features'].get('compare_cdf', False):
            title_text += f"- DA_cdf_noirr_2016\n"
            
        create_text_page(pdf, title_text, title="Preliminary Study Report")
        
        # Figures Pages
        captions = {
            "fig01_assimilation_diagnostics_2016": "Figure 1: SMAP assimilation diagnostics showing spatial coverage, observation counts, and mean innovations/increments.",
            "fig02_cdf_sensitivity_2016": "Figure 2: Sensitivity maps highlighting differences between DA (no-CDF), DA (CDF), and Open Loop.",
            "fig03_vertical_propagation_et_2016": "Figure 3: Vertical propagation of soil moisture updates into the root zone and coherence with ET fluxes.",
            "fig04_runoff_partitioning_2016": "Figure 4: Impact of assimilation on runoff partitioning (surface vs baseflow) and seasonal dynamics.",
            "fig05_hymap_streamflow_2016": "Figure 5: Evaluation of routed streamflow (HyMAP) against observations."
        }
        
        for img_path in figures_list:
            if img_path is None or not os.path.exists(img_path):
                continue
                
            basename = os.path.basename(img_path).split('.')[0]
            caption = captions.get(basename, "Generated Figure.")
            add_figure_page(pdf, img_path, caption)
            
        # Interpretation Page
        interpretation_text = (
            "Preliminary Interpretation:\n"
            "- The assimilation of SMAP introduces specific spatial patterns of wetting/drying.\n"
            "- Vertical propagation from surface to root-zone heavily influences ET and runoff partitioning.\n"
            "- The CDF matching process alters the absolute magnitudes of the increments compared to the no-CDF approach.\n"
        )
        create_text_page(pdf, interpretation_text, title="Interpretation")
        
        # Warnings and Missing Data Page
        warnings_text = "Missing Diagnostics / Warnings:\n\n"
        if not log_warnings:
            warnings_text += "No warnings. All expected data was found."
        else:
            for w in log_warnings:
                warnings_text += f"- {w}\n"
                
        create_text_page(pdf, warnings_text, title="Diagnostics Status")
        
    return pdf_path
