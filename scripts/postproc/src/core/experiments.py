# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: lis_postproc.core.experiments
Description: Core framework logic: configuration, variables, and experiment parsing.
================================================================================
"""
"""
core/experiments.py — Experiment Class
========================================
Represents a LIS/Noah-MP experiment with its metadata and path.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Experiment:
    """
    Represents a LIS/Noah-MP experiment.

    Attributes
    ---------
    id          : Unique identifier (key in experiments.yaml)
    label       : Short label for figures (e.g., "DA-SMAP-CDF")
    type        : "open_loop" or "data_assimilation"
    year        : Simulation year
    path        : Path relative to project_root
    path_abs    : Resolved absolute path
    assimilation: Type of assimilated observation ("none", "SMAP", "LAI", "SMAP+LAI")
    cdf_matching: CDF-matching applied (True/False)
    irrigation  : Irrigation enabled (True/False)
    color       : Default color for figures
    linestyle   : Line style for timeseries
    marker      : Marker for scatter plots
    description : Long description (optional)
    """
    id: str
    label: str
    type: str
    year: int
    path: Optional[str] = None
    path_abs: Optional[str] = None
    assimilation: str = "none"
    cdf_matching: bool = False
    irrigation: bool = False
    color: str = "#2166AC"
    linestyle: str = "-"
    marker: str = "o"
    description: str = ""

    @classmethod
    def from_dict(cls, exp_id: str, data: dict) -> 'Experiment':
        """Creates an Experiment object from a dictionary (YAML input)."""
        return cls(
            id=exp_id,
            label=data.get('label', exp_id),
            type=data.get('type', 'open_loop'),
            year=data.get('year', 2016),
            path=data.get('path'),
            path_abs=data.get('path_abs'),
            assimilation=data.get('assimilation', 'none'),
            cdf_matching=data.get('cdf_matching', False),
            irrigation=data.get('irrigation', False),
            color=data.get('color', '#2166AC'),
            linestyle=data.get('linestyle', '-'),
            marker=data.get('marker', 'o'),
            description=data.get('description', ''),
        )

    def is_available(self) -> bool:
        """Returns True if the experiment path is defined and exists."""
        return self.path_abs is not None and os.path.isdir(self.path_abs)

    def is_da(self) -> bool:
        """Returns True if this is a data assimilation experiment."""
        return self.type == 'data_assimilation'

    def validate_path(self) -> str:
        """Verifies path existence. Returns a status message."""
        if self.path_abs is None:
            return f"[WARNING] {self.id}: path=null (future experiment)"
        if not os.path.isdir(self.path_abs):
            return f"[ERROR] {self.id}: path not found: {self.path_abs}"
        return f"[OK] {self.id}: path exists"

    def __repr__(self) -> str:
        status = "available" if self.is_available() else "unavailable"
        return (
            f"Experiment(id={self.id!r}, label={self.label!r}, "
            f"type={self.type!r}, year={self.year}, status={status})"
        )


def build_experiments_from_catalog(catalog: dict) -> dict:
    """Converts a raw catalog (dict) into a dictionary of Experiment objects."""
    return {
        exp_id: Experiment.from_dict(exp_id, exp_data)
        for exp_id, exp_data in catalog.items()
    }
