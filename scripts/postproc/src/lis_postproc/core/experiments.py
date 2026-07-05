"""
core/experiments.py — Classe Experiment
========================================
Représente une expérience LIS/Noah-MP avec ses métadonnées et son path.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Experiment:
    """
    Représente une expérience LIS/Noah-MP.

    Attributs
    ---------
    id          : Identifiant unique (clé dans experiments.yaml)
    label       : Label court pour les figures (ex: "DA-SMAP-CDF")
    type        : "open_loop" ou "data_assimilation"
    year        : Année de simulation
    path        : Chemin relatif à project_root
    path_abs    : Chemin absolu résolu
    assimilation: Type d'observation assimilée ("none", "SMAP", "LAI", "SMAP+LAI")
    cdf_matching: CDF-matching appliqué (True/False)
    irrigation  : Irrigation activée (True/False)
    color       : Couleur par défaut pour les figures
    linestyle   : Style de ligne pour les séries temporelles
    marker      : Marqueur pour les scatter plots
    description : Description longue (optionnel)
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
        """Crée un Experiment depuis un dictionnaire (entrée YAML)."""
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
        """Retourne True si le path de l'expérience est défini et existe."""
        return self.path_abs is not None and os.path.isdir(self.path_abs)

    def is_da(self) -> bool:
        """Retourne True si c'est une expérience d'assimilation."""
        return self.type == 'data_assimilation'

    def validate_path(self) -> str:
        """Vérifie l'existence du path. Retourne un message d'état."""
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
    """Convertit un catalogue brut (dict) en dict d'objets Experiment."""
    return {
        exp_id: Experiment.from_dict(exp_id, exp_data)
        for exp_id, exp_data in catalog.items()
    }
