"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.core.variables
Description: Core framework logic: configuration, variables, and experiment parsing.
================================================================================
"""
"""
core/variables.py — Variable Class
======================================
Represents a hydrological/physical variable with its metadata
and plotting parameters.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class Variable:
    """
    Represents a LIS/Noah-MP/HyMAP variable.

    Attributes
    ---------
    variable_id     : Unique identifier (YAML filename without extension)
    long_name       : Full name ("Surface soil moisture")
    short_name      : Short name ("SSM")
    unit            : Physical unit ("m³ m⁻³")
    category        : Category ("soil_moisture", "runoff", "fluxes", ...)
    lis_variable_names : List of LIS NetCDF variable names
    operation       : Calculation operation ("direct", "sum", "layer_mean", ...)
    scale_factor    : Conversion factor
    cmap            : Matplotlib colormap for maps
    difference_cmap : Colormap for difference maps
    colorbar_label  : Colorbar label
    difference_label: Label for difference maps
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
        """Creates a Variable object from a dictionary (YAML input)."""
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
    """Converts a dictionary of raw YAML data into a dictionary of Variable objects."""
    return {
        var_id: Variable.from_dict(data)
        for var_id, data in variables_data.items()
    }
