import sys
from lis_postproc.cli import _load_context
from lis_postproc.core.config import load_recipe
from lis_postproc.core.recipes import Recipe
from lis_postproc.runner import RecipeRunner
import lis_postproc.runner

# Monkey-patch independent validation to do nothing
lis_postproc.runner.run_independent_validation = lambda *args: None

ctx = _load_context('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc')
recipe_raw = load_recipe('configs/recipes/smap_cdf_sensitivity_2016.yaml', ctx['global_cfg'])
recipe = Recipe.from_dict(recipe_raw)
runner = RecipeRunner(recipe, ctx['experiments_raw'], ctx['global_cfg'], ctx['variables_dir'], dry_run=True)
runner.run(make_figures=True)
