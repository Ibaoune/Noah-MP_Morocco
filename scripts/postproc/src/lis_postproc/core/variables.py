"""
core/variables.py — Classe Variable
======================================
Représente une variable hydrologique/physique avec ses métadonnées
et ses paramètres de plotting.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class Variable:
    """
    Représente une variable LIS/Noah-MP/HyMAP.

    Attributs
    ---------
    variable_id     : Identifiant unique (nom du fichier YAML sans extension)
    long_name       : Nom complet ("Surface soil moisture")
    short_name      : Nom court ("SSM")
    unit            : Unité physique ("m³ m⁻³")
    category        : Catégorie ("soil_moisture", "runoff", "fluxes", ...)
    lis_variable_names : Liste des noms de variables LIS NetCDF
    operation       : Opération de calcul ("direct", "sum", "layer_mean", ...)
    scale_factor    : Facteur de conversion
    cmap            : Colormap matplotlib pour les cartes
    difference_cmap : Colormap pour les cartes de différences
    colorbar_label  : Label de la colorbar
    difference_label: Label pour les cartes de différences
    """
    variable_id: str
    long_name: str
    short_name: str
    unit: str
    category: str = "other"
    lis_variable_names: List[str] = field(default_factory=list)
    operation: str = "direct"
    scale_factor: float = 1.0
    layer: Optional[int] = None
    layers: Optional[List[int]] = None
    cmap: str = "viridis"
    difference_cmap: str = "RdBu"
    colorbar_label: str = ""
    difference_label: str = ""
    auto_limits: bool = True
    robust_percentiles: List[float] = field(default_factory=lambda: [2, 98])
    center_difference_on_zero: bool = True
    difference_bounds: Optional[List[float]] = None
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    levels: Optional[List[float]] = None
    difference_vmin: Optional[float] = None
    difference_vmax: Optional[float] = None
    difference_levels: Optional[List[float]] = None
    unit_label: Optional[str] = None
    tick_format: Optional[str] = None
    difference_type: Optional[str] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Variable':
        """Crée un Variable depuis un dictionnaire (entrée YAML)."""
        input_cfg = data.get('input', {})
        plot_cfg = data.get('plotting', {})
        return cls(
            variable_id=data.get('variable_id', ''),
            long_name=data.get('long_name', ''),
            short_name=data.get('short_name', ''),
            unit=data.get('unit', ''),
            category=data.get('category', 'other'),
            lis_variable_names=input_cfg.get('lis_variable_names', []),
            operation=input_cfg.get('operation', 'direct'),
            scale_factor=input_cfg.get('scale_factor', 1.0),
            layer=input_cfg.get('layer'),
            layers=input_cfg.get('layers'),
            cmap=plot_cfg.get('cmap', 'viridis'),
            difference_cmap=plot_cfg.get('difference_cmap', 'RdBu'),
            colorbar_label=plot_cfg.get('colorbar_label', ''),
            difference_label=plot_cfg.get('difference_label', ''),
            auto_limits=plot_cfg.get('auto_limits', True),
            robust_percentiles=plot_cfg.get('robust_percentiles', [2, 98]),
            center_difference_on_zero=plot_cfg.get('center_difference_on_zero', True),
            difference_bounds=plot_cfg.get('difference_bounds'),
            vmin=plot_cfg.get('vmin'),
            vmax=plot_cfg.get('vmax'),
            levels=plot_cfg.get('levels'),
            difference_vmin=plot_cfg.get('difference_vmin'),
            difference_vmax=plot_cfg.get('difference_vmax'),
            difference_levels=plot_cfg.get('difference_levels'),
            unit_label=plot_cfg.get('unit_label'),
            tick_format=plot_cfg.get('tick_format'),
            difference_type=plot_cfg.get('difference_type'),
            y_min=plot_cfg.get('y_min'),
            y_max=plot_cfg.get('y_max'),
        )

    def __repr__(self) -> str:
        return (
            f"Variable(id={self.variable_id!r}, "
            f"short={self.short_name!r}, unit={self.unit!r})"
        )


def build_variables_from_dicts(variables_data: Dict[str, Dict]) -> Dict[str, Variable]:
    """Convertit un dict de données YAML brutes en dict d'objets Variable."""
    return {
        var_id: Variable.from_dict(data)
        for var_id, data in variables_data.items()
    }
