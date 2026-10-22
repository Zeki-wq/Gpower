"""
G*Power Clone - Two Independent Samples t-Test Statistical Power & Sample Size Calculator
"""

from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    validate_parameters,
    ValidationError,
)

__version__ = "1.0.0"
__all__ = [
    "compute_a_priori",
    "compute_post_hoc",
    "validate_parameters",
    "ValidationError",
]
