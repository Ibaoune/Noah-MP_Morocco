"""
core/recipes.py — Classe Recipe
=================================
Représente une recette de comparaison (fichier configs/recipes/*.yaml).
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class RecipeOutputs:
    """Chemins de sortie pour une recette."""
    figure_dir: str = ""
    metrics_dir: str = ""
    table_dir: str = ""
    pdf_report: str = ""

    def create_dirs(self):
        """Crée tous les dossiers de sortie."""
        for path in [self.figure_dir, self.metrics_dir, self.table_dir]:
            if path:
                os.makedirs(path, exist_ok=True)
        pdf_dir = os.path.dirname(self.pdf_report)
        if pdf_dir:
            os.makedirs(pdf_dir, exist_ok=True)


@dataclass
class Recipe:
    """
    Représente une recette de post-processing.

    Une recette définit :
      - Les expériences à comparer
      - La baseline de référence
      - Les variables à analyser
      - Les diagnostics à activer
      - Les chemins de sortie
    """
    recipe_id: str
    title: str
    description: str = ""
    year: int = 2016
    domain: str = "morocco_001deg"
    comparison_mode: str = "multi_experiment"
    baseline: Optional[str] = None
    experiments: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    outputs: RecipeOutputs = field(default_factory=RecipeOutputs)

    @classmethod
    def from_dict(cls, data: dict) -> 'Recipe':
        """Crée un Recipe depuis un dictionnaire (entrée YAML)."""
        outputs_raw = data.get('outputs', {})
        outputs = RecipeOutputs(
            figure_dir=outputs_raw.get('figure_dir', ''),
            metrics_dir=outputs_raw.get('metrics_dir', ''),
            table_dir=outputs_raw.get('table_dir', ''),
            pdf_report=outputs_raw.get('pdf_report', ''),
        )
        return cls(
            recipe_id=data.get('recipe_id', 'unnamed'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            year=data.get('year', 2016),
            domain=data.get('domain', 'morocco_001deg'),
            comparison_mode=data.get('comparison_mode', 'multi_experiment'),
            baseline=data.get('baseline'),
            experiments=data.get('experiments', []),
            variables=data.get('variables', []),
            diagnostics=data.get('diagnostics', {}),
            outputs=outputs,
        )

    def is_diagnostic_enabled(self, diag_name: str) -> bool:
        """Vérifie si un diagnostic est activé dans cette recette."""
        diag = self.diagnostics.get(diag_name, {})
        return diag.get('enabled', False)

    def get_da_experiments(self) -> List[str]:
        """Retourne la liste des expériences DA référencées dans la recette."""
        return [e for e in self.experiments if e != self.baseline]

    def get_assimilation_config(self) -> Dict[str, Any]:
        """Retourne la config du bloc assimilation."""
        return self.diagnostics.get('assimilation', {})

    def __repr__(self) -> str:
        return (
            f"Recipe(id={self.recipe_id!r}, "
            f"experiments={self.experiments}, "
            f"variables={len(self.variables)} vars)"
        )
