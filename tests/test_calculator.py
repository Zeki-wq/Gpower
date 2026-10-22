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


class TestUnequalRatiosAndBoundaries:
    """Verifies allocation ratio N2/N1 and integer ceiling behavior on boundary conditions."""

    def test_unbalanced_ceiling_rule(self):
        # When ratio is fractional, N2 must be exactly math.ceil(N1 * ratio)
        for ratio in [0.33, 0.67, 1.33, 2.5, 3.14]:
            res = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=ratio)
            expected_n2 = math.ceil(res["n1"] * ratio)
            assert res["n2"] == expected_n2
            assert res["total_n"] == res["n1"] + res["n2"]

    def test_extreme_allocation_ratios(self):
        # Extreme ratio 0.25 (1:4)
        res_small_ratio = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.25)
        assert res_small_ratio["n2"] == math.ceil(res_small_ratio["n1"] * 0.25)
        assert res_small_ratio["actual_power"] >= 0.80

        # Extreme ratio 4.0 (4:1)
        res_large_ratio = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=4.0)
        assert res_large_ratio["n2"] == math.ceil(res_large_ratio["n1"] * 4.0)
        assert res_large_ratio["actual_power"] >= 0.80


class TestParameterExtremes:
    """Verifies behavior across extreme effect sizes, alphas, and power boundaries."""

    def test_very_small_effect_size(self):
        # d = 0.05 requires very large sample sizes (N > 5000)
        res = compute_post_hoc(tails=2, d=0.05, alpha=0.05, n1=3000, n2=3000)
        assert res["actual_power"] > 0.40
        assert not math.isnan(res["actual_power"])

    def test_very_large_effect_size(self):
        # d = 2.5 reaches near 1.0 power even with small sample sizes
        res = compute_post_hoc(tails=2, d=2.5, alpha=0.05, n1=10, n2=10)
        assert res["actual_power"] > 0.99
        assert not math.isnan(res["actual_power"])

    def test_alpha_boundaries(self):
        # Very strict alpha: 0.0001
        res_strict = compute_post_hoc(tails=2, d=0.8, alpha=0.0001, n1=50, n2=50)
        assert 0.0 < res_strict["actual_power"] < 1.0

        # Lenient alpha: 0.20
        res_lenient = compute_post_hoc(tails=2, d=0.5, alpha=0.20, n1=30, n2=30)
        assert res_lenient["actual_power"] > 0.50

    def test_power_boundaries_a_priori(self):
        # Low target power: 0.50
        res_low = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.50, ratio=1.0)
        assert res_low["actual_power"] >= 0.50

        # High target power: 0.99
        res_high = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.99, ratio=1.0)
        assert res_high["actual_power"] >= 0.99
        assert res_high["total_n"] > res_low["total_n"]


class TestLargeDeltaAsymptotics:
    """Verifies stability when delta >= 10.0 (prevents NaN underflow)."""

    def test_delta_greater_than_10_numerical_stability(self):
        # delta = 10.0, df = 198
        res = compute_post_hoc(tails=2, d=1.41421356, alpha=0.05, n1=100, n2=100)
        assert math.isclose(res["delta"], 10.0, abs_tol=1e-3)
        assert not math.isnan(res["actual_power"])
        assert math.isclose(res["actual_power"], 1.0, abs_tol=1e-4)

    def test_delta_extreme_15(self):
        # delta = 15.0
        res = compute_post_hoc(tails=2, d=1.7320508, alpha=0.01, n1=150, n2=150)
        assert not math.isnan(res["actual_power"])
        assert math.isclose(res["actual_power"], 1.0, abs_tol=1e-5)


class TestStatsmodelsCrossValidation:
    """Cross-validates against independent library statsmodels."""

    def test_compare_against_statsmodels_post_hoc(self):
        from statsmodels.stats.power import TTestIndPower
        ttp = TTestIndPower()

        cases = [
            (2, 0.2, 0.05, 50, 50),
            (2, 0.5, 0.05, 50, 50),
            (2, 0.8, 0.05, 20, 20),
            (1, 0.5, 0.05, 50, 50),
            (2, 0.5, 0.05, 40, 80),
        ]
        for tails, d, alpha, n1, n2 in cases:
            alt = "two-sided" if tails == 2 else "larger"
            ratio = n2 / n1
            sm_power = ttp.power(effect_size=d, nobs1=n1, alpha=alpha, ratio=ratio, alternative=alt)
            gp_res = compute_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)
            # Must agree within 1e-5 with independent library
            assert math.isclose(gp_res["actual_power"], sm_power, abs_tol=1e-5)

    def test_compare_against_statsmodels_a_priori_ceil(self):
        from statsmodels.stats.power import TTestIndPower
        ttp = TTestIndPower()

        cases = [
            (2, 0.2, 0.05, 0.80, 1.0),
            (2, 0.5, 0.05, 0.80, 1.0),
            (2, 0.8, 0.05, 0.80, 1.0),
            (1, 0.5, 0.05, 0.80, 1.0),
            (2, 0.5, 0.05, 0.80, 2.0),
        ]
        for tails, d, alpha, pwr, ratio in cases:
            alt = "two-sided" if tails == 2 else "larger"
            sm_n1_continuous = ttp.solve_power(effect_size=d, power=pwr, alpha=alpha, ratio=ratio, alternative=alt)
            sm_n1_ceil = math.ceil(sm_n1_continuous)
            gp_res = compute_a_priori(tails=tails, d=d, alpha=alpha, power=pwr, ratio=ratio)
            # Discrete integer minimal search must exactly match ceil of continuous solution
            assert gp_res["n1"] == sm_n1_ceil

