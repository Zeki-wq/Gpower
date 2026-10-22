"""
Tests for Model Context Protocol (MCP) server tools (src/mcp_server.py).
"""

import math
from src.mcp_server import (
    compute_a_priori_sample_size,
    compute_post_hoc_power,
)


class TestMCPServerTools:
    """Verifies MCP server tool functions directly."""

    def test_mcp_a_priori_standard_success(self):
        res = compute_a_priori_sample_size(
            d=0.5,
            power=0.80,
            alpha=0.05,
            tails=2,
            ratio=1.0,
        )
        assert res["status"] == "success"
        assert res["n1"] == 64
        assert res["n2"] == 64
        assert res["total_n"] == 128
        assert res["df"] == 126
        assert math.isclose(res["delta"], 2.828427, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.978971, abs_tol=1e-4)
        assert res["actual_power"] >= 0.80

    def test_mcp_a_priori_unbalanced_one_tailed(self):
        res = compute_a_priori_sample_size(
            d=0.5,
            power=0.80,
            alpha=0.05,
            tails=1,
            ratio=2.0,
        )
        assert res["status"] == "success"
        assert res["n1"] == 38
        assert res["n2"] == 76
        assert res["total_n"] == 114
        assert res["df"] == 112
        assert math.isclose(res["delta"], 2.516611, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.658573, abs_tol=1e-4)
        assert res["actual_power"] >= 0.80

    def test_mcp_a_priori_validation_error_negative_d(self):
        res = compute_a_priori_sample_size(
            d=-0.5,
            power=0.80,
        )
        assert res["status"] == "error"
        assert res["error_type"] == "ValidationError"
        assert "pozitif olmalıdır" in res["message"]

    def test_mcp_a_priori_validation_error_invalid_power(self):
        res = compute_a_priori_sample_size(
            d=0.5,
            power=1.5,
        )
        assert res["status"] == "error"
        assert res["error_type"] == "ValidationError"
        assert "aralığında olmalıdır" in res["message"]

    def test_mcp_post_hoc_standard_success(self):
        res = compute_post_hoc_power(
            d=0.5,
            n1=50,
            n2=50,
            alpha=0.05,
            tails=2,
        )
        assert res["status"] == "success"
        assert res["n1"] == 50
        assert res["n2"] == 50
        assert res["total_n"] == 100
        assert res["df"] == 98
        assert math.isclose(res["delta"], 2.500000, abs_tol=1e-4)
        assert math.isclose(res["critical_t"], 1.984467, abs_tol=1e-4)
        assert math.isclose(res["actual_power"], 0.696893, abs_tol=1e-4)

    def test_mcp_post_hoc_validation_error_small_sample(self):
        res = compute_post_hoc_power(
            d=0.5,
            n1=1,
            n2=50,
        )
        assert res["status"] == "error"
        assert res["error_type"] == "ValidationError"
        assert "en az 2" in res["message"]
