import math

from src.mcp_server import power_analysis


def test_canonical_mcp_a_priori_result_uses_contract_names():
    result = power_analysis(test="t2-indep", mode="a-priori", tails=2, d=0.5,
                            alpha=0.05, power=0.8, ratio=1.0)
    assert result["n1"] == result["n2"] == 64
    assert result["n_total"] == 128 and result["df"] == 126
    assert math.isclose(result["ncp"], 2.8284271247461903)
    assert result["actual_power"] >= 0.8


def test_canonical_mcp_supports_all_families():
    cases = [
        {"test": "t2-indep", "mode": "post-hoc", "tails": 1, "d": 0.5, "alpha": 0.05, "n1": 88, "n2": 88},
        {"test": "t-paired", "mode": "post-hoc", "tails": 1, "dz": 0.5, "alpha": 0.05, "n_total": 45},
        {"test": "anova-oneway", "mode": "post-hoc", "f": 0.25, "alpha": 0.05, "n_total": 100, "groups": 5},
        {"test": "chi2-contingency", "mode": "post-hoc", "w": 0.3, "alpha": 0.05, "n_total": 100, "df": 5},
        {"test": "multireg-r2", "mode": "post-hoc", "f2": 0.15, "alpha": 0.05, "n_total": 100, "predictors": 2},
    ]
    assert all(power_analysis(**case)["status"] == "success" for case in cases)


def test_canonical_mcp_error_shape_matches_contract():
    result = power_analysis(test="t-paired", mode="post-hoc")
    assert set(result) == {"error", "code", "field"}
    assert result["code"] == "MISSING_PARAM"
    assert result["field"] == "alpha"


def test_canonical_mcp_rejects_unknown_and_irrelevant_params():
    unknown = power_analysis(test="unknown", mode="post-hoc")
    assert unknown["code"] == "UNSUPPORTED"
    irrelevant = power_analysis(test="t2-indep", mode="post-hoc", tails=1, d=0.5,
                                alpha=0.05, n1=20, n2=20, power=0.8)
    assert irrelevant["code"] == "UNKNOWN_PARAM"
    assert irrelevant["field"] == "power"
