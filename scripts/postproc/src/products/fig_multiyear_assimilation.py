#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image

def trim_whitespace(im):
    """Trims whitespace from an image."""
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = Image.chops.difference(im, bg)
    diff = Image.chops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im
    
import PIL.ImageChops as ImageChops
Image.chops = ImageChops

def build_composite_figure(base_dir, out_path):
    # Image paths
    images = {
        'obs': os.path.join(base_dir, 'DA_CDF', 'DA_CDF_obs_count.png'), # Obs count is same for both DA experiments
        'hist_nocdf': os.path.join(base_dir, 'DA_NoCDF', 'DA_NoCDF_increment_histogram.png'),
        'hist_cdf': os.path.join(base_dir, 'DA_CDF', 'DA_CDF_increment_histogram.png'),
        'inno_nocdf': os.path.join(base_dir, 'DA_NoCDF', 'DA_NoCDF_innovation_map.png'),
        'inno_cdf': os.path.join(base_dir, 'DA_CDF', 'DA_CDF_innovation_map.png'),
        'incr_nocdf': os.path.join(base_dir, 'DA_NoCDF', 'DA_NoCDF_increment_map.png'),
        'incr_cdf': os.path.join(base_dir, 'DA_CDF', 'DA_CDF_increment_map.png'),
        'seas_nocdf': os.path.join(base_dir, 'DA_NoCDF', 'DA_NoCDF_seasonal_increments.png'),
        'seas_cdf': os.path.join(base_dir, 'DA_CDF', 'DA_CDF_seasonal_increments.png'),
    }
    
    # Load and trim
    loaded_imgs = {}
    for key, path in images.items():
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
            loaded_imgs[key] = None
        else:
            with Image.open(path) as im:
                loaded_imgs[key] = trim_whitespace(im.convert('RGB'))
                
    # Create figure
    fig = plt.figure(figsize=(24, 18))
    # Add a bit of space on the left for row labels
    gs = gridspec.GridSpec(3, 4, width_ratios=[1, 1, 1, 1], height_ratios=[1, 1, 1], 
                           wspace=0.08, hspace=0.15, left=0.06, right=0.98, top=0.92, bottom=0.05)
    
    panels = [
        ('obs', gs[0, 0], '(a) Assimilated Observation Frequency'),
        ('hist_nocdf', gs[0, 1], '(b) Increment Distribution — NoCDF'),
        ('hist_cdf', gs[0, 2], '(c) Increment Distribution — CDF'),
        ('inno_nocdf', gs[1, 0], '(d) Mean Innovation — NoCDF'),
        ('incr_nocdf', gs[1, 1], '(e) Mean Analysis Increment — NoCDF'),
        ('seas_nocdf', gs[1, 2:4], '(f) Seasonal Analysis Increments — NoCDF'),
        ('inno_cdf', gs[2, 0], '(g) Mean Innovation — CDF'),
        ('incr_cdf', gs[2, 1], '(h) Mean Analysis Increment — CDF'),
        ('seas_cdf', gs[2, 2:4], '(i) Seasonal Analysis Increments — CDF')
    ]
    
    for key, gss, title in panels:
        ax = fig.add_subplot(gss)
        ax.axis('off')
        img = loaded_imgs.get(key)
        if img:
            ax.imshow(img)
            # Add a title at the top left of each panel area, but outside the image if possible
            # We place it slightly above the image box
            ax.set_title(title, loc='left', fontsize=13, fontweight='bold', pad=5)
            
    # Add vertical row headers
    row_headers = [
        (0.83, 'Observation coverage and\nincrement distributions'),
        (0.50, 'NoCDF assimilation'),
        (0.18, 'CDF assimilation')
    ]
    for y_pos, text in row_headers:
        fig.text(0.015, y_pos, text, va='center', ha='center', rotation=90, 
                 fontsize=14, fontweight='semibold')
            
    fig.suptitle("Multi-year SMAP Assimilation Diagnostics (2016–2020)", fontsize=18, fontweight='bold', y=0.97)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    
    # Save as PDF as requested
    pdf_path = out_path.replace('.png', '.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white')
    
    print(f"Figure saved to {out_path} and {pdf_path}")

if __name__ == "__main__":
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_dir = os.path.join(project_root, "scripts/postproc/matrix_2016_2020/figures/smap_cdf_sensitivity_2016_2020/assimilation")
    out_path = os.path.join(base_dir, "Fig_MultiYear_Assimilation.png")
    build_composite_figure(base_dir, out_path)
