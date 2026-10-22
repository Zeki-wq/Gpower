"""
Unit tests for the statistical calculation engine (src/calculator.py).
"""

import pytest
import math
from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    validate_parameters,
    ValidationError,
)


class TestInputValidation:
    """Tests boundary condition validations and domain constraints."""

    def test_invalid_mode(self):
        with pytest.raises(ValidationError, match="Geçersiz analiz modu"):
            validate_parameters(mode="invalid", tails=2, d=0.5, alpha=0.05)

    def test_invalid_tails(self):
        with pytest.raises(ValidationError, match="Geçersiz kuyruk"):
            compute_post_hoc(tails=3, d=0.5, alpha=0.05, n1=30, n2=30)
        with pytest.raises(ValidationError, match="Geçersiz kuyruk"):
            compute_post_hoc(tails=0, d=0.5, alpha=0.05, n1=30, n2=30)

    def test_invalid_effect_size(self):
        with pytest.raises(ValidationError, match="pozitif olmalıdır"):
            compute_post_hoc(tails=2, d=0.0, alpha=0.05, n1=30, n2=30)
        with pytest.raises(ValidationError, match="pozitif olmalıdır"):
            compute_post_hoc(tails=2, d=-0.5, alpha=0.05, n1=30, n2=30)

    def test_invalid_alpha(self):
        with pytest.raises(ValidationError, match="aralığında olmalıdır"):
            compute_post_hoc(tails=2, d=0.5, alpha=0.0, n1=30, n2=30)
        with pytest.raises(ValidationError, match="aralığında olmalıdır"):
            compute_post_hoc(tails=2, d=0.5, alpha=1.0, n1=30, n2=30)
        with pytest.raises(ValidationError, match="aralığında olmalıdır"):
            compute_post_hoc(tails=2, d=0.5, alpha=-0.05, n1=30, n2=30)

    def test_invalid_target_power(self):
        with pytest.raises(ValidationError, match=r"(?i)power|hedef"):
            compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.0)
        with pytest.raises(ValidationError, match=r"(?i)power|hedef"):
            compute_a_priori(tails=2, d=0.5, alpha=0.05, power=1.0)
        with pytest.raises(ValidationError, match=r"(?i)power|hedef"):
            compute_a_priori(tails=2, d=0.5, alpha=0.05, power=1.5)

    def test_invalid_allocation_ratio(self):
        with pytest.raises(ValidationError, match="tahsis oranı"):
            compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.0)
        with pytest.raises(ValidationError, match="tahsis oranı"):
            compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=-1.0)

    def test_invalid_sample_sizes(self):
        with pytest.raises(ValidationError, match="en az 2"):
            compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=1, n2=30)
        with pytest.raises(ValidationError, match="en az 2"):
            compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=30, n2=0)


class TestPostHocPowerCalculations:
    """Tests Post Hoc statistical power calculations against known statistical benchmarks."""

    def test_post_hoc_standard_two_tailed(self):
        # Scenario 2.1 from SPEC.md: d=0.5, alpha=0.05, n1=50, n2=50, tails=2
        res = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=50, n2=50)
        assert res["df"] == 98
        assert math.isclose(res["delta"], 2.500000, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.984467, abs_tol=1e-4)
        assert math.isclose(res["actual_power"], 0.696893, abs_tol=1e-4)

    def test_post_hoc_unbalanced_one_tailed(self):
        # Scenario 2.2 from SPEC.md: d=0.3, alpha=0.05, n1=60, n2=90, tails=1
        res = compute_post_hoc(tails=1, d=0.3, alpha=0.05, n1=60, n2=90)
        assert res["df"] == 148
        assert math.isclose(res["delta"], 1.800000, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.655215, abs_tol=1e-4)
        assert math.isclose(res["actual_power"], 0.558399, abs_tol=1e-4)

    def test_power_monotonicity_with_sample_size(self):
        # Increasing sample size MUST increase statistical power
        res_small = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=30, n2=30)
        res_large = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=60, n2=60)
        assert res_large["actual_power"] > res_small["actual_power"]

    def test_power_monotonicity_with_effect_size(self):
        # Increasing effect size MUST increase statistical power
        res_small = compute_post_hoc(tails=2, d=0.2, alpha=0.05, n1=50, n2=50)
        res_large = compute_post_hoc(tails=2, d=0.8, alpha=0.05, n1=50, n2=50)
        assert res_large["actual_power"] > res_small["actual_power"]

    def test_one_tailed_greater_power_than_two_tailed(self):
        # For positive d, one-tailed test has lower critical t and higher power
        res_1tail = compute_post_hoc(tails=1, d=0.5, alpha=0.05, n1=50, n2=50)
        res_2tail = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=50, n2=50)
        assert res_1tail["critical_t"] < res_2tail["critical_t"]
        assert res_1tail["actual_power"] > res_2tail["actual_power"]


class TestAPrioriSampleCalculations:
    """Tests A Priori sample size calculations."""

    def test_a_priori_standard_two_tailed(self):
        # Scenario 1.1 from SPEC.md: d=0.5, alpha=0.05, power=0.80, ratio=1.0, tails=2
        res = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=1.0)
        assert res["n1"] == 64
        assert res["n2"] == 64
        assert res["total_n"] == 128
        assert res["df"] == 126
        assert math.isclose(res["delta"], 2.828427, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.978971, abs_tol=1e-4)
        assert res["actual_power"] >= 0.80
        assert math.isclose(res["actual_power"], 0.801460, abs_tol=1e-4)

    def test_a_priori_minimal_sample_property(self):
        # Verifies that n1 - 1 fails to achieve target power (minimal integer property)
        res = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=1.0)
        n1 = res["n1"]
        # With n1 - 1, power must be strictly less than target power
        res_sub = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=n1 - 1, n2=n1 - 1)
        assert res_sub["actual_power"] < 0.80

    def test_a_priori_unbalanced_ratio(self):
        # Scenario 1.2 from SPEC.md: d=0.5, alpha=0.05, power=0.80, ratio=2.0, tails=1
        res = compute_a_priori(tails=1, d=0.5, alpha=0.05, power=0.80, ratio=2.0)
        assert res["n1"] == 38
        assert res["n2"] == 76
        assert res["total_n"] == 114
        assert res["df"] == 112
        assert math.isclose(res["delta"], 2.516611, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.658573, abs_tol=1e-4)
        assert res["actual_power"] >= 0.80
        assert math.isclose(res["actual_power"], 0.804142, abs_tol=1e-4)
