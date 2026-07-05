import os
from .plot_domain_map import plot_all_domain_maps

def run_domain(data_dict, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = data_dict.get('project_root', "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco")
    
    generated = plot_all_domain_maps(out_dir, project_root)
    
    return generated
