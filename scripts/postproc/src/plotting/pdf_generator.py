# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: lis_postproc.plotting.pdf_generator
Description: Generic plotting utilities and visualization functions.
================================================================================
"""
"""
plotting/pdf_generator.py — Générateur de rapport PDF V2
================================================================
Crée un rapport PDF scientifique V2 contenant exclusivement
les diagnostics d'assimilation et des textes explicatifs.
"""
import os
import json
import logging
import csv
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend

logger = logging.getLogger(__name__)

# Ordre d'affichage des diagnostics d'assimilation
DIAG_ORDER = [
    "obs_count",
    "assim_frequency",
    "innovation_map",
    "increment_map",
    "increment_histogram",
    "seasonal_increments",
    "spread_consistency",
    "spread_comparison"
]

def _create_text_page(pdf, text: str, title: str = None, fontsize: int = 12, align: str = 'center'):
    """Crée une page contenant uniquement du texte."""
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape
    ax.axis('off')
    
    if title:
        fig.suptitle(title, fontsize=20, fontweight='bold', y=0.88)
        y_pos = 0.75
    else:
        y_pos = 0.5

    kwargs = {'ha': 'center', 'va': 'center'} if align == 'center' else {'ha': 'left', 'va': 'top'}
    x_pos = 0.5 if align == 'center' else 0.1
    
    ax.text(x_pos, y_pos, text, fontsize=fontsize, wrap=True, **kwargs)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def _create_cover_page(pdf, recipe):
    """Crée la page de garde du rapport V2."""
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    ax.axis('off')
    
    title = recipe.title if hasattr(recipe, 'title') else "Diagnostic Report"
    domain = recipe.domain if hasattr(recipe, 'domain') else "Unknown Domain"
    year = recipe.year if hasattr(recipe, 'year') else "Unknown Year"
    experiments = recipe.experiments if hasattr(recipe, 'experiments') else []
    
    ax.text(0.5, 0.85, title, fontsize=24, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.75, f"Domain: {domain} | Year: {year}", fontsize=16, ha='center', va='center')
    
    ax.text(0.5, 0.60, "Objective:", fontsize=14, fontweight='bold', ha='center', va='center')
    objective = (
        "This report evaluates the internal behaviour of the SMAP EnKF assimilation system\n"
        f"over {domain} in {year}. It focuses on SMAP observation availability, innovations,\n"
        "analysis increments, seasonal correction patterns, and ensemble spread diagnostics\n"
        "for the noCDF and CDF assimilation configurations."
    )
    ax.text(0.5, 0.50, objective, fontsize=12, ha='center', va='center', style='italic')
    
    ax.text(0.5, 0.35, "Experiments Compared:", fontsize=14, fontweight='bold', ha='center', va='center')
    y = 0.30
    for exp in experiments:
        ax.text(0.5, y, f"• {exp}", fontsize=12, ha='center', va='center')
        y -= 0.04
        
    warning = (
        "Note: This report does not include hydrological impact diagnostics.\n"
        "Soil moisture, ET, runoff, groundwater, streamflow, and external\n"
        "validation diagnostics were not generated in this report version."
    )
    ax.text(0.5, 0.15, warning, fontsize=11, color='darkred', ha='center', va='center', bbox=dict(facecolor='mistyrose', edgecolor='red', boxstyle='round,pad=0.5'))
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def _create_toc_page(pdf, sections):
    """Crée la table des matières V2."""
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    ax.axis('off')
    
    ax.text(0.5, 0.85, "Table of Contents", fontsize=24, fontweight='bold', ha='center', va='center')
    
    y = 0.70
    for title in sections:
        ax.text(0.2, y, title, fontsize=16, ha='left', va='center')
        y -= 0.06
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def generate_diagnostic_report(recipe, figure_files: list, out_pdf_path: str):
    """
    Génère le PDF V2 complet et structuré, et crée un inventaire CSV.
    """
    os.makedirs(os.path.dirname(out_pdf_path), exist_ok=True)
    logger.info(f"Generating structured PDF V2 report: {out_pdf_path}")
    
    json_files = [f for f in figure_files if f.endswith('.json')]
    
    metadata_list = []
    for jf in json_files:
        try:
            with open(jf, 'r') as f:
                meta = json.load(f)
                meta['json_path'] = jf
                metadata_list.append(meta)
        except Exception as e:
            logger.error(f"Failed to read metadata {jf}: {e}")
            
    nocdf_meta = [m for m in metadata_list if "nocdf" in m.get('experiment', '').lower() and m.get('experiment') not in ['OPL_noCDF_CDF', 'DA_Differences']]
    cdf_meta = [m for m in metadata_list if "nocdf" not in m.get('experiment', '').lower() and "cdf" in m.get('experiment', '').lower() and m.get('experiment') not in ['OPL_noCDF_CDF', 'DA_Differences']]
    
    def get_order_idx(meta):
        for i, suffix in enumerate(DIAG_ORDER):
            if meta['filename'].endswith(f"{suffix}.png"):
                return i
        return 999
        
    nocdf_meta.sort(key=get_order_idx)
    cdf_meta.sort(key=get_order_idx)
    
    hydro_meta = [m for m in metadata_list if m.get('experiment') in ['OPL_noCDF_CDF', 'DA_Differences']]
    
    def get_hydro_group(var_id):
        group = [m for m in hydro_meta if m.get('variable') == var_id]
        order = {"annual_mean": 1, "difference": 2, "timeseries": 3, "partitioning": 4}
        group.sort(key=lambda m: order.get(m.get('diagnostic_type', ''), 99))
        return group
        
    inc_meta = [m for m in metadata_list if m.get('diagnostic_type') == 'increment_propagation']
    val_meta = [m for m in metadata_list if m.get('diagnostic_type') == 'independent_ob_validation']

    sections_config = [
        ("Surface soil moisture response", "surface_soil_moisture"),
        ("Root-zone and vertical soil moisture propagation", "rootzone_soil_moisture"),
        ("Surface fluxes", "evapotranspiration"),
        ("Groundwater response", ["groundwater_storage", "water_table_depth"]),
        ("Runoff and baseflow response", ["total_runoff", "surface_runoff", "baseflow", "runoff_partitioning"]),
    ]

    sections = [
        "1. Report scope",
        "2. DA-SMAP-noCDF assimilation diagnostics",
        "3. DA-SMAP-CDF assimilation diagnostics",
        "4. noCDF vs CDF interpretation notes",
    ]
    
    current_sec_num = 5
    hydro_sections_to_plot = []
    
    for title, var_ids in sections_config:
        if isinstance(var_ids, str):
            var_ids = [var_ids]
            
        group = []
        for vid in var_ids:
            group.extend(get_hydro_group(vid))
            
        if group:
            sec_title = f"{current_sec_num}. {title}"
            sections.append(sec_title)
            hydro_sections_to_plot.append((group, sec_title))
            current_sec_num += 1

    if inc_meta:
        sec_title = f"{current_sec_num}. Assimilation Increment Propagation and Persistence"
        sections.append(sec_title)
        hydro_sections_to_plot.append((inc_meta, sec_title))
        current_sec_num += 1

    if val_meta:
        sec_title = f"{current_sec_num}. Independent Observations Validation"
        sections.append(sec_title)
        # Order the independent validation figures by variable
        order = {"Soil_Moisture": 1, "Evapotranspiration": 2, "GPP": 3, "Water_Storage": 4}
        val_meta.sort(key=lambda m: (order.get(m.get('variable', ''), 99), m.get('filename', '')))
        hydro_sections_to_plot.append((val_meta, sec_title))
        current_sec_num += 1

    if not val_meta:
        sections.append(f"{current_sec_num}. Streamflow & External validation")
        current_sec_num += 1

    sections.append(f"{current_sec_num}. Scientific checklist")
    
    inventory_path = os.path.join(os.path.dirname(out_pdf_path), "..", "metrics", "smap_cdf_sensitivity", "figure_inventory_v2.csv")
    os.makedirs(os.path.dirname(inventory_path), exist_ok=True)
    
    total_added = 0
    pdf_page = 3
    inventory_rows = []
    
    with pdf_backend.PdfPages(out_pdf_path) as pdf:
        _create_cover_page(pdf, recipe)
        _create_toc_page(pdf, sections)
        
        def plot_diagnostic_group(group_meta, section_title):
            nonlocal pdf_page, total_added
            _create_text_page(pdf, "", title=section_title)
            pdf_page += 1
            
            for meta in group_meta:
                img_path = os.path.join(os.path.dirname(meta['json_path']), meta['filename'])
                if not os.path.exists(img_path):
                    continue
                
                try:
                    img = plt.imread(img_path)
                    fig = plt.figure(figsize=(11.69, 8.27))
                    
                    ax_title = fig.add_axes([0.1, 0.90, 0.8, 0.05])
                    ax_title.axis('off')
                    ax_title.text(0.5, 0.5, meta['title'], fontsize=14, fontweight='bold', ha='center', va='center')
                    
                    ax_img = fig.add_axes([0.1, 0.25, 0.8, 0.65])
                    ax_img.axis('off')
                    ax_img.imshow(img)
                    
                    ax_cap = fig.add_axes([0.1, 0.05, 0.8, 0.15])
                    ax_cap.axis('off')
                    ax_cap.text(0.0, 1.0, f"Source file: {meta['filename']}", fontsize=8, color='gray', ha='left', va='top')
                    ax_cap.text(0.0, 0.7, meta.get('caption', ''), fontsize=11, ha='left', va='top', wrap=True)
                    
                    pdf.savefig(fig, bbox_inches='tight', dpi=150)
                    plt.close(fig)
                    total_added += 1
                    pdf_page += 1
                    
                    inventory_rows.append({
                        "original_pdf_page": pdf_page - 1,
                        "source_file": meta['filename'],
                        "detected_experiment": meta.get('experiment', ''),
                        "diagnostic_type": meta.get('diagnostic_type', ''),
                        "new_title": meta.get('title', ''),
                        "caption": meta.get('caption', ''),
                        "action": "kept",
                        "warning": ""
                    })
                except Exception as e:
                    logger.error(f"Failed to add {img_path} to PDF: {e}")

        if nocdf_meta:
            plot_diagnostic_group(nocdf_meta, "2. DA-SMAP-noCDF assimilation diagnostics")
        if cdf_meta:
            plot_diagnostic_group(cdf_meta, "3. DA-SMAP-CDF assimilation diagnostics")
        
        notes = (
            "When comparing noCDF and CDF assimilation diagnostics, check:\n\n"
            "• whether the spatial coverage of assimilated observations is consistent between experiments;\n"
            "• whether CDF-matching reduces systematic innovation bias;\n"
            "• whether the increment distribution becomes more centred around zero;\n"
            "• whether wet-season and dry-season increments show coherent spatial patterns;\n"
            "• whether spread diagnostics remain consistent;\n"
            "• whether any difference in observation count reflects a real processing choice or a labelling/input-file issue.\n\n"
            "Do not invent scientific conclusions. This page should only guide the interpretation."
        )
        _create_text_page(pdf, notes, title="4. noCDF vs CDF interpretation notes", align='left')
        
        for group, sec_title in hydro_sections_to_plot:
            plot_diagnostic_group(group, sec_title)
            
        # Streamflow missing warning
        if not val_meta:
            streamflow_warn = (
                "Streamflow and External validation figures were not generated.\n\n"
                "This typically happens because HyMAP routing outputs are not yet available,\n"
                "or the necessary in-situ observations have not been provided to the framework."
            )
            _create_text_page(pdf, streamflow_warn, title=f"{current_sec_num - 1}. Streamflow & External validation", align='left')
        
        checklist = (
            "[ ] Are SMAP observations spatially well distributed?\n"
            "[ ] Are there spatial gaps in the assimilation coverage?\n"
            "[ ] Is the monthly observation availability realistic?\n"
            "[ ] Are the noCDF and CDF observation counts consistent?\n"
            "[ ] Are innovations mostly positive, negative, or spatially mixed?\n"
            "[ ] Are increments physically coherent with the sign of innovations?\n"
            "[ ] Is the increment distribution centred close to zero?\n"
            "[ ] Does CDF-matching reduce systematic innovation bias?\n"
            "[ ] Are wet-season and dry-season increments different?\n"
            "[ ] Are there regions with unrealistic or noisy increments?\n"
            "[ ] Are spread diagnostics consistent enough for interpretation?\n"
            "[ ] Which assimilation figures should be kept for the paper?\n"
            "[ ] Which assimilation figures should go to supplementary material?\n"
            "[ ] Which figures need revised colorbar limits, titles, or captions?"
        )
        _create_text_page(pdf, checklist, title=f"{current_sec_num}. Scientific checklist", align='left')

    if inventory_rows:
        with open(inventory_path, 'w', newline='') as csvfile:
            fieldnames = ["original_pdf_page", "source_file", "detected_experiment", "diagnostic_type", "new_title", "caption", "action", "warning"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in inventory_rows:
                writer.writerow(row)
        logger.info(f"Inventory saved to {inventory_path}")
        
    logger.info(f"PDF V2 generated successfully with {total_added} figures.")
    return out_pdf_path
