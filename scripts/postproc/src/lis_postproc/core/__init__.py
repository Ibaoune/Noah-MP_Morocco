"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.core.__init__
Description: Core framework logic: configuration, variables, and experiment parsing.
================================================================================
"""
"""core/__init__.py"""
from .config import (
    load_yaml, load_global_config, load_experiments_catalog,
    load_recipe, load_variable, load_all_variables_for_recipe,
    list_available_experiments, list_available_variables,
    list_available_recipes, validate_recipe_against_catalog,
    check_all_configs
)
from .experiments import Experiment, build_experiments_from_catalog
from .variables import Variable, build_variables_from_dicts
from .recipes import Recipe, RecipeOutputs

__all__ = [
    'load_yaml', 'load_global_config', 'load_experiments_catalog',
    'load_recipe', 'load_variable', 'load_all_variables_for_recipe',
    'list_available_experiments', 'list_available_variables',
    'list_available_recipes', 'validate_recipe_against_catalog',
    'check_all_configs',
    'Experiment', 'build_experiments_from_catalog',
    'Variable', 'build_variables_from_dicts',
    'Recipe', 'RecipeOutputs',
]
