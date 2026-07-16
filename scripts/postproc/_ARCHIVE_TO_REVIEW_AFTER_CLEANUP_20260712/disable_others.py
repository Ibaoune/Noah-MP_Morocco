import yaml

with open('configs/recipes/smap_cdf_sensitivity_2016.yaml', 'r') as f:
    recipe = yaml.safe_load(f)

for k, v in recipe['diagnostics'].items():
    if k != 'increment_propagation':
        if isinstance(v, dict):
            v['enabled'] = False
        else:
            recipe['diagnostics'][k] = {'enabled': False}

with open('configs/recipes/smap_cdf_sensitivity_2016.yaml', 'w') as f:
    yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)
