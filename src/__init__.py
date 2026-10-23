"""G*Power clone's shared statistical power-analysis engine and interfaces."""

from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    compute_power_analysis,
    validate_parameters,
    ValidationError,
)

__version__ = "1.3.0"
__all__ = [
    "compute_a_priori",
    "compute_post_hoc",
    "compute_power_analysis",
    "validate_parameters",
    "ValidationError",
]
