"""
G*Power Clean-Room Re-implementation
Module: Two Independent Groups Mean Difference t-Test Calculator
Reference: G*Power 3.1.9.4 specification (SPEC.md)
"""

import math
from typing import Dict, Any, Union
from scipy import stats


class ValidationError(ValueError):
    """Raised when input parameters violate statistical domain constraints."""

    def __init__(self, message: str, code: str = "INVALID_VALUE", field: str | None = None):
        super().__init__(message)
        self.code = code
        self.field = field


def validate_parameters(
    mode: str,
    tails: int,
    d: float,
    alpha: float,
    power: Union[float, None] = None,
    ratio: Union[float, None] = None,
    n1: Union[int, None] = None,
    n2: Union[int, None] = None,
) -> None:
    """Validates parameters according to SPEC.md domain constraints."""
    if mode not in ("a-priori", "post-hoc"):
        raise ValidationError(f"Geçersiz analiz modu: '{mode}'. 'a-priori' veya 'post-hoc' olmalıdır.")

    if not isinstance(tails, int) or isinstance(tails, bool) or tails not in (1, 2):
        raise ValidationError(f"Geçersiz kuyruk sayısı: {tails}. 1 veya 2 olmalıdır.")

    if not isinstance(d, (int, float)) or isinstance(d, bool) or not math.isfinite(d):
        raise ValidationError("Etki büyüklüğü (d) geçerli bir sayı olmalıdır.")
    if d <= 0:
        raise ValidationError(f"Etki büyüklüğü (d) pozitif olmalıdır (> 0). Girilen: {d}")

    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not math.isfinite(alpha):
        raise ValidationError("Alfa (alpha) geçerli bir sayı olmalıdır.")
    if not (0 < alpha < 1):
        raise ValidationError(f"Alfa (alpha) (0, 1) aralığında olmalıdır. Girilen: {alpha}")

    if mode == "a-priori":
        if power is None or not isinstance(power, (int, float)) or isinstance(power, bool) or not math.isfinite(power):
            raise ValidationError("A priori analiz için hedef güç (power) belirtilmelidir.")
        if not (0 < power < 1):
            raise ValidationError(f"Hedef güç (power) (0, 1) aralığında olmalıdır. Girilen: {power}")

        if ratio is None or not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not math.isfinite(ratio):
            raise ValidationError("Grup tahsis oranı (ratio = N2/N1) belirtilmelidir.")
        if ratio <= 0:
            raise ValidationError(f"Grup tahsis oranı (N2/N1) pozitif olmalıdır (> 0). Girilen: {ratio}")

    elif mode == "post-hoc":
        if n1 is None or not isinstance(n1, int) or isinstance(n1, bool) or n1 < 2:
            raise ValidationError(f"Grup 1 örneklem büyüklüğü (n1) en az 2 olmalıdır. Girilen: {n1}")
        if n2 is None or not isinstance(n2, int) or isinstance(n2, bool) or n2 < 2:
            raise ValidationError(f"Grup 2 örneklem büyüklüğü (n2) en az 2 olmalıdır. Girilen: {n2}")


def compute_post_hoc(
    tails: int,
    d: float,
    alpha: float,
    n1: int,
    n2: int,
) -> Dict[str, Any]:
    """
    Computes achieved statistical power for two independent groups t-test.
    
    Formula:
        df = n1 + n2 - 2
        delta = d * sqrt((n1 * n2) / (n1 + n2))
        t_crit = t.ppf(1 - alpha / tails, df)
        power:
            tails == 2: 1 - nct.cdf(t_crit, df, delta) + nct.cdf(-t_crit, df, delta)
            tails == 1: 1 - nct.cdf(t_crit, df, delta)
    """
    validate_parameters(mode="post-hoc", tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)

    df = n1 + n2 - 2
    delta = float(d * math.sqrt((n1 * n2) / (n1 + n2)))

    if tails == 2:
        critical_t = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    else:
        critical_t = float(stats.t.ppf(1.0 - alpha, df))

    # Robust non-central t CDF evaluations avoiding numerical underflow/NaN for large delta
    try:
        cdf_upper = stats.nct.cdf(critical_t, df, delta)
        if math.isnan(cdf_upper):
            cdf_upper = 0.0 if delta > 0 else 1.0
    except Exception:
        cdf_upper = 0.0 if delta > 0 else 1.0

    if tails == 2:
        try:
            cdf_lower = stats.nct.cdf(-critical_t, df, delta)
            if math.isnan(cdf_lower):
                cdf_lower = 0.0
        except Exception:
            cdf_lower = 0.0
        actual_power = float(1.0 - cdf_upper + cdf_lower)
    else:
        actual_power = float(1.0 - cdf_upper)

    # Bound power to [0.0, 1.0] due to floating point precision
    actual_power = max(0.0, min(1.0, actual_power))

    return {
        "status": "success",
        "test": "t2-indep",
        "mode": "post-hoc",
        "tails": tails,
        "d": float(d),
        "alpha": float(alpha),
        "n1": n1,
        "n2": n2,
        "total_n": n1 + n2,
        "df": df,
        "delta": round(delta, 6),
        "critical_t": round(critical_t, 6),
        "actual_power": round(actual_power, 6),
    }


def compute_a_priori(
    tails: int,
    d: float,
    alpha: float,
    power: float,
    ratio: float = 1.0,
) -> Dict[str, Any]:
    """
    Computes required sample size for two independent groups t-test given target power.

    G*Power's a-priori procedure solves for the continuous total sample size at
    the requested allocation ratio, rounds that total upward, derives N1 from
    that rounded total, and rounds N2 upward from the continuous allocation.
    This differs from searching all integer N1 values with
    N2=ceil(N1*ratio): that search can find a smaller feasible pair than
    G*Power reports for an uneven ratio.
    """
    validate_parameters(mode="a-priori", tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)

    z_alpha = stats.norm.ppf(1.0 - alpha / tails)
    z_beta = stats.norm.ppf(power)

    # Initial approximation
    approx_n1 = max(2, math.ceil(((z_alpha + z_beta) ** 2 * (1.0 + 1.0 / ratio)) / (d ** 2)))
    
    def power_for(n1: float, n2: float) -> float:
        df = n1 + n2 - 2.0
        delta = d * math.sqrt((n1 * n2) / (n1 + n2))
        critical_t = stats.t.ppf(1.0 - alpha / tails, df)
        upper = stats.nct.cdf(critical_t, df, delta)
        if math.isnan(upper):
            upper = 0.0 if delta > 0 else 1.0
        if tails == 2:
            lower = stats.nct.cdf(-critical_t, df, delta)
            if math.isnan(lower):
                lower = 0.0
            return float(max(0.0, min(1.0, 1.0 - upper + lower)))
        return float(max(0.0, min(1.0, 1.0 - upper)))

    def continuous_power(n1: float) -> float:
        return power_for(n1, n1 * ratio)

    # Find the continuous N1 at the requested ratio. The normal approximation
    # is a useful starting point, but the final root uses the noncentral t.
    low_n1 = 2.0
    high_n1 = float(max(approx_n1, 3))
    max_search_n1 = high_n1
    while continuous_power(high_n1) < power:
        high_n1 *= 2.0
        max_search_n1 = high_n1
        if high_n1 > 10_000_000:
            raise RuntimeError(
                f"Hedef güç ({power}) makul arama sınırında ({max_search_n1}) sağlanamadı."
            )

    for _ in range(100):
        mid_n1 = (low_n1 + high_n1) / 2.0
        if continuous_power(mid_n1) >= power:
            high_n1 = mid_n1
        else:
            low_n1 = mid_n1
    continuous_total_n = high_n1 * (1.0 + ratio)

    # G*Power rounds the total sample size up, derives N1 from that total, and
    # rounds N2 upward from the continuous allocation at the target ratio.
    total_for_allocation = math.ceil(continuous_total_n - 1e-12)
    candidate_n1 = max(2, math.ceil(total_for_allocation / (1.0 + ratio) - 1e-12))
    candidate_n2 = max(2, math.ceil(high_n1 * ratio - 1e-12))

    # The integer allocation can move slightly from the continuous ratio.
    # Preserve G*Power's threshold guarantee if that rounding lands below it.
    while True:
        res = compute_post_hoc(
            tails=tails,
            d=d,
            alpha=alpha,
            n1=candidate_n1,
            n2=candidate_n2,
        )
        if power_for(candidate_n1, candidate_n2) >= power:
            return {
                "status": "success",
                "test": "t2-indep",
                "mode": "a-priori",
                "tails": tails,
                "d": float(d),
                "alpha": float(alpha),
                "target_power": float(power),
                "ratio": float(ratio),
                "n1": candidate_n1,
                "n2": candidate_n2,
                "total_n": candidate_n1 + candidate_n2,
                "df": res["df"],
                "delta": res["delta"],
                "critical_t": res["critical_t"],
                "actual_power": res["actual_power"],
            }
        total_for_allocation += 1
        candidate_n1 = max(2, math.ceil(total_for_allocation / (1.0 + ratio) - 1e-12))
        candidate_n2 = max(2, math.ceil(high_n1 * ratio - 1e-12))


SUPPORTED_TESTS = {"t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2"}
SUPPORTED_MODES = {"a-priori", "post-hoc", "compromise", "criterion", "sensitivity"}


def _unrounded_independent_t_power(tails: int, d: float, alpha: float, n1: int, n2: int) -> tuple[float, float, int, float]:
    """Return power, critical t, df, and noncentrality without output rounding."""
    df = n1 + n2 - 2
    delta = d * math.sqrt((n1 * n2) / (n1 + n2))
    critical_t = float(stats.t.ppf(1.0 - alpha / tails, df))
    upper = float(stats.nct.cdf(critical_t, df, delta))
    if tails == 2:
        lower = float(stats.nct.cdf(-critical_t, df, delta))
        power = 1.0 - upper + lower
    else:
        power = 1.0 - upper
    return max(0.0, min(1.0, power)), critical_t, df, delta


def _bisect_increasing(function, target: float, low: float, high: float, *, iterations: int = 100) -> float:
    """Find the first x in [low, high] for a monotone increasing function."""
    if function(low) > target or function(high) < target:
        raise ValidationError("Hedef değer verilen parametre aralığında sağlanamıyor.")
    for _ in range(iterations):
        mid = (low + high) / 2.0
        if function(mid) >= target:
            high = mid
        else:
            low = mid
    return high


def compute_sensitivity(
    tails: int,
    alpha: float,
    power: float,
    n1: int,
    n2: int,
) -> Dict[str, Any]:
    """Find the smallest positive Cohen's d that reaches target power."""
    if not isinstance(tails, int) or isinstance(tails, bool) or tails not in (1, 2):
        raise ValidationError("Kuyruk sayısı 1 veya 2 olmalıdır.")
    if not isinstance(n1, int) or isinstance(n1, bool) or n1 < 2 or not isinstance(n2, int) or isinstance(n2, bool) or n2 < 2:
        raise ValidationError("n1 ve n2 en az 2 olan tamsayılar olmalıdır.")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValidationError("Alfa (alpha) (0, 1) aralığında olmalıdır.")
    if not isinstance(power, (int, float)) or isinstance(power, bool) or not math.isfinite(power) or not 0 < power < 1:
        raise ValidationError("Hedef güç (power) (0, 1) aralığında olmalıdır.")

    effect = _bisect_increasing(lambda d: _unrounded_independent_t_power(tails, d, alpha, n1, n2)[0], float(power), 0.0, 1000.0)
    actual, critical_t, df, delta = _unrounded_independent_t_power(tails, effect, alpha, n1, n2)
    return {
        "status": "success", "test": "t2-indep", "mode": "sensitivity", "tails": tails,
        "alpha": float(alpha), "target_power": float(power), "d": round(effect, 6),
        "n1": n1, "n2": n2, "total_n": n1 + n2, "df": df,
        "delta": round(delta, 6), "critical_t": round(critical_t, 6), "actual_power": round(actual, 6),
    }


def compute_criterion(
    tails: int,
    d: float,
    power: float,
    n1: int,
    n2: int,
) -> Dict[str, Any]:
    """Find the significance level that reaches target power for fixed d and N."""
    if not isinstance(tails, int) or isinstance(tails, bool) or tails not in (1, 2):
        raise ValidationError("Kuyruk sayısı 1 veya 2 olmalıdır.")
    if not isinstance(d, (int, float)) or isinstance(d, bool) or not math.isfinite(d) or d <= 0:
        raise ValidationError("Etki büyüklüğü d pozitif ve sonlu olmalıdır.")
    if not isinstance(n1, int) or isinstance(n1, bool) or n1 < 2 or not isinstance(n2, int) or isinstance(n2, bool) or n2 < 2:
        raise ValidationError("n1 ve n2 en az 2 olan tamsayılar olmalıdır.")
    if not isinstance(power, (int, float)) or isinstance(power, bool) or not math.isfinite(power) or not 0 < power < 1:
        raise ValidationError("Hedef güç (power) (0, 1) aralığında olmalıdır.")

    alpha = _bisect_increasing(lambda a: _unrounded_independent_t_power(tails, d, a, n1, n2)[0], float(power), 1e-12, 1.0 - 1e-12)
    actual, critical_t, df, delta = _unrounded_independent_t_power(tails, d, alpha, n1, n2)
    return {
        "status": "success", "test": "t2-indep", "mode": "criterion", "tails": tails,
        "alpha": round(alpha, 6), "target_power": float(power), "d": float(d),
        "n1": n1, "n2": n2, "total_n": n1 + n2, "df": df,
        "delta": round(delta, 6), "critical_t": round(critical_t, 6), "actual_power": round(actual, 6),
    }


def compute_compromise(
    tails: int,
    d: float,
    n1: int,
    n2: int,
    beta_alpha_ratio: float = 1.0,
) -> Dict[str, Any]:
    """Find alpha and beta for fixed N and effect at a beta/alpha ratio."""
    if not isinstance(tails, int) or isinstance(tails, bool) or tails not in (1, 2):
        raise ValidationError("Kuyruk sayısı 1 veya 2 olmalıdır.")
    if not isinstance(d, (int, float)) or isinstance(d, bool) or not math.isfinite(d) or d <= 0:
        raise ValidationError("Etki büyüklüğü d pozitif ve sonlu olmalıdır.")
    if not isinstance(n1, int) or isinstance(n1, bool) or n1 < 2 or not isinstance(n2, int) or isinstance(n2, bool) or n2 < 2:
        raise ValidationError("n1 ve n2 en az 2 olan tamsayılar olmalıdır.")
    if not isinstance(beta_alpha_ratio, (int, float)) or isinstance(beta_alpha_ratio, bool) or not math.isfinite(beta_alpha_ratio) or beta_alpha_ratio <= 0:
        raise ValidationError("beta_alpha_ratio pozitif ve sonlu olmalıdır.")

    upper = 1.0 / (1.0 + beta_alpha_ratio)
    def balance(alpha: float) -> float:
        actual = _unrounded_independent_t_power(tails, d, alpha, n1, n2)[0]
        return actual - (1.0 - beta_alpha_ratio * alpha)

    low, high = 1e-12, upper - 1e-12
    if balance(low) > 0 or balance(high) < 0:
        raise ValidationError("Bu beta/alpha oranı için geçerli uzlaşma çözümü bulunamadı.")
    for _ in range(100):
        mid = (low + high) / 2.0
        if balance(mid) >= 0:
            high = mid
        else:
            low = mid
    alpha = high
    actual, critical_t, df, delta = _unrounded_independent_t_power(tails, d, alpha, n1, n2)
    beta = 1.0 - actual
    return {
        "status": "success", "test": "t2-indep", "mode": "compromise", "tails": tails,
        "alpha": round(alpha, 6), "beta": round(beta, 6), "beta_alpha_ratio": float(beta_alpha_ratio),
        "d": float(d), "n1": n1, "n2": n2, "total_n": n1 + n2, "df": df,
        "delta": round(delta, 6), "critical_t": round(critical_t, 6), "actual_power": round(actual, 6),
    }


FAMILY_EFFECT = {
    "t2-indep": "d", "t-paired": "dz", "anova-oneway": "f",
    "chi2-contingency": "w", "multireg-r2": "f2",
}
FAMILY_SIZE = {
    "t2-indep": {"n1", "n2"}, "t-paired": {"n_total"},
    "anova-oneway": {"n_total", "groups"},
    "chi2-contingency": {"n_total", "df"},
    "multireg-r2": {"n_total", "predictors"},
}
MODE_COMMON = {
    "a-priori": {"alpha", "power"},
    "post-hoc": {"alpha"},
    "compromise": {"beta_alpha_ratio"},
    "criterion": {"power"},
    "sensitivity": {"alpha", "power"},
}


def _family_fields(test: str, mode: str) -> set[str]:
    fields = set(MODE_COMMON[mode])
    if mode != "a-priori":
        fields |= set(FAMILY_SIZE[test])
    elif test == "anova-oneway":
        fields.add("groups")
    elif test == "chi2-contingency":
        fields.add("df")
    elif test == "multireg-r2":
        fields.add("predictors")
    if mode != "sensitivity":
        fields.add(FAMILY_EFFECT[test])
    if mode == "a-priori" and test == "t2-indep":
        fields.add("ratio")
    if test in {"t2-indep", "t-paired"}:
        fields.add("tails")
    return fields


def _sample_floor(test: str, p: dict[str, Any]) -> int:
    if test == "t-paired":
        return 2
    if test == "anova-oneway":
        return p["groups"] + 1
    if test == "chi2-contingency":
        return 2
    if test == "multireg-r2":
        return p["predictors"] + 2
    return 4


def _power_components(test: str, p: dict[str, Any], effect: float, alpha: float, size: dict[str, int]) -> dict[str, float | int]:
    """Calculate noncentrality, critical value, degrees of freedom and power."""
    if test == "t2-indep":
        n1, n2 = size["n1"], size["n2"]
        df = n1 + n2 - 2
        ncp = effect * math.sqrt((n1 * n2) / (n1 + n2))
        tails = p["tails"]
        critical = float(stats.t.ppf(1.0 - alpha / tails, df))
        power = float(stats.nct.sf(critical, df, ncp))
        if tails == 2:
            power += float(stats.nct.cdf(-critical, df, ncp))
        return {"ncp": ncp, "critical_t": critical, "df": df, "power": max(0.0, min(1.0, power))}
    if test == "t-paired":
        n = size["n_total"]
        df = n - 1
        ncp = effect * math.sqrt(n)
        tails = p["tails"]
        critical = float(stats.t.ppf(1.0 - alpha / tails, df))
        power = float(stats.nct.sf(critical, df, ncp))
        if tails == 2:
            power += float(stats.nct.cdf(-critical, df, ncp))
        return {"ncp": ncp, "critical_t": critical, "df": df, "power": max(0.0, min(1.0, power))}
    if test == "anova-oneway":
        n = size["n_total"]
        df1, df2 = p["groups"] - 1, n - p["groups"]
        ncp = effect * effect * n
        critical = float(stats.f.ppf(1.0 - alpha, df1, df2))
        return {"ncp": ncp, "critical_f": critical, "df1": df1, "df2": df2,
                "power": float(stats.ncf.sf(critical, df1, df2, ncp))}
    if test == "chi2-contingency":
        ncp = effect * effect * size["n_total"]
        critical = float(stats.chi2.ppf(1.0 - alpha, p["df"]))
        return {"ncp": ncp, "critical_chi2": critical, "df": p["df"],
                "power": float(stats.ncx2.sf(critical, p["df"], ncp))}
    n = size["n_total"]
    df1, df2 = p["predictors"], n - p["predictors"] - 1
    ncp = effect * n
    critical = float(stats.f.ppf(1.0 - alpha, df1, df2))
    return {"ncp": ncp, "critical_f": critical, "df1": df1, "df2": df2,
            "power": float(stats.ncf.sf(critical, df1, df2, ncp))}


def _size_from_parameters(test: str, p: dict[str, Any]) -> dict[str, int]:
    if test == "t2-indep":
        return {"n1": p["n1"], "n2": p["n2"]}
    return {"n_total": p["n_total"]}


def _normalized_result(test: str, mode: str, p: dict[str, Any], size: dict[str, int],
                       components: dict[str, float | int], effect: float, alpha: float,
                       power: float) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "success", "test": test, "mode": mode,
        "ncp": float(components["ncp"]), **{k: v for k, v in components.items() if k != "ncp"},
    }
    if "df" in result:
        result["df"] = int(result["df"])
    if "df1" in result:
        result["df1"], result["df2"] = int(result["df1"]), int(result["df2"])
    if test in {"t2-indep", "t-paired"}:
        result["tails"] = p["tails"]
    result[FAMILY_EFFECT[test]] = float(effect)
    result.update({k: v for k, v in p.items() if k not in {FAMILY_EFFECT[test]}})
    if test == "t2-indep":
        result.update(n1=int(size["n1"]), n2=int(size["n2"]), n_total=int(size["n1"] + size["n2"]))
        result["delta"] = result["ncp"]
        result["total_n"] = result["n_total"]
    else:
        result["n_total"] = int(size["n_total"])
        if test in {"t-paired", "anova-oneway", "chi2-contingency", "multireg-r2"}:
            result["total_n"] = result["n_total"]
        if test == "t-paired":
            result["delta"] = result["ncp"]
    result["alpha"] = float(alpha)
    if mode == "a-priori":
        result["actual_power"] = float(power)
    elif mode == "post-hoc":
        result["power"] = float(power)
        result["actual_power"] = float(power)
    elif mode == "compromise":
        result["power"] = float(power)
        result["beta"] = float(1.0 - power)
        result["actual_power"] = float(power)
    elif mode == "criterion":
        result["alpha"] = float(alpha)
        result["actual_power"] = float(power)
    else:
        result[FAMILY_EFFECT[test]] = float(effect)
    return result


def _validate_dispatch(test: str, mode: str, parameters: dict[str, Any]) -> dict[str, Any]:
    if test not in SUPPORTED_TESTS:
        raise ValidationError(f"Bilinmeyen test ailesi: {test}.", "UNSUPPORTED", "test")
    if mode not in SUPPORTED_MODES:
        raise ValidationError(f"Bilinmeyen analiz modu: {mode}.", "UNSUPPORTED", "mode")
    required = _family_fields(test, mode)
    extra = set(parameters) - required
    if extra:
        field = sorted(extra)[0]
        raise ValidationError(f"ilgisiz parametre veya tanınmayan alan: {field}.", "UNKNOWN_PARAM", field)
    missing = required - set(parameters)
    if missing:
        field = sorted(missing)[0]
        raise ValidationError(f"Gerekli parametre eksik: {field}.", "MISSING_PARAM", field)

    integer_fields = FAMILY_SIZE[test] | ({"tails"} if test in {"t2-indep", "t-paired"} else set())
    for field, value in parameters.items():
        if field in integer_fields:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValidationError(f"{field} tam sayı olmalıdır.", "INVALID_VALUE", field)
        elif not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValidationError(f"{field} sonlu bir sayı olmalıdır.", "INVALID_VALUE", field)

    if test in {"t2-indep", "t-paired"} and parameters["tails"] not in (1, 2):
        raise ValidationError("tails 1 veya 2 olmalıdır.", "OUT_OF_RANGE", "tails")
    for field in ("alpha", "power"):
        if field in parameters and not 0 < parameters[field] < 1:
            raise ValidationError(f"{field} 0 ile 1 arasında olmalıdır.", "OUT_OF_RANGE", field)
    for field in (FAMILY_EFFECT[test], "ratio", "beta_alpha_ratio"):
        if field in parameters and parameters[field] <= 0:
            raise ValidationError(f"{field} pozitif olmalıdır.", "OUT_OF_RANGE", field)
    for field in ("n1", "n2", "n_total", "groups"):
        if field in parameters and parameters[field] < 2:
            raise ValidationError(f"{field} en az 2 olmalıdır.", "OUT_OF_RANGE", field)
    for field in ("df", "predictors"):
        if field in parameters and parameters[field] < 1:
            raise ValidationError(f"{field} en az 1 olmalıdır.", "OUT_OF_RANGE", field)
    if "power" in parameters and "alpha" in parameters and parameters["power"] <= parameters["alpha"]:
        raise ValidationError("Power, alpha değerinden büyük olmalı.", "INCONSISTENT", "power")
    if test == "anova-oneway" and mode != "a-priori" and parameters["n_total"] <= parameters["groups"]:
        raise ValidationError("n_total groups değerinden büyük olmalı.", "INCONSISTENT", "n_total")
    if test == "multireg-r2" and mode != "a-priori" and parameters["n_total"] <= parameters["predictors"] + 1:
        raise ValidationError("n_total predictors + 1 değerinden büyük olmalı.", "INCONSISTENT", "n_total")
    return dict(parameters)


def compute_power_analysis(test: str, mode: str, **parameters: Any) -> Dict[str, Any]:
    """Contract v1 dispatcher shared by CLI, MCP, agent, and UI."""
    p = _validate_dispatch(test, mode, parameters)
    effect_name = FAMILY_EFFECT[test]
    if mode == "a-priori":
        target = float(p["power"])
        if test == "t2-indep":
            legacy = compute_a_priori(p["tails"], p["d"], p["alpha"], p["power"], p["ratio"])
            size = {"n1": legacy["n1"], "n2": legacy["n2"]}
            effect = float(p["d"])
            components = _power_components(test, p, effect, float(p["alpha"]), size)
            return _normalized_result(test, mode, p, size, components, effect, float(p["alpha"]), float(components["power"]))
        effect = float(p[effect_name])
        step = p["groups"] if test == "anova-oneway" else 1
        minimum = _sample_floor(test, p)
        high = math.ceil(minimum / step) * step
        low = high - step
        def power_for_n(n: int) -> float:
            return float(_power_components(test, p, effect, float(p["alpha"]), {"n_total": n})["power"])
        while power_for_n(high) < target:
            high = math.ceil((high * 2) / step) * step
            if high > 10_000_000:
                raise ValidationError("Arama sınırında hedef güce ulaşılamadı.", "NO_SOLUTION", "power")
        while low + step < high:
            mid = low + (((high - low) // step) // 2) * step
            if power_for_n(mid) >= target:
                high = mid
            else:
                low = mid
        size = {"n_total": high}
        components = _power_components(test, p, effect, float(p["alpha"]), size)
        return _normalized_result(test, mode, p, size, components, effect, float(p["alpha"]), float(components["power"]))

    if mode == "post-hoc":
        size = _size_from_parameters(test, p)
        components = _power_components(test, p, float(p[effect_name]), float(p["alpha"]), size)
        return _normalized_result(test, mode, p, size, components, float(p[effect_name]), float(p["alpha"]), float(components["power"]))

    size = _size_from_parameters(test, p)
    ratio = float(p["beta_alpha_ratio"]) if mode == "compromise" else None
    target = float(p["power"]) if mode in {"criterion", "sensitivity"} else None
    fixed_effect = None if mode == "sensitivity" else float(p[effect_name])
    if mode == "criterion":
        alpha = _bisect_increasing(lambda a: float(_power_components(test, p, fixed_effect, a, size)["power"]), target, 1e-12, 1.0 - 1e-12)
    elif mode == "compromise":
        upper = 1.0 / (1.0 + ratio)
        def balance(a: float) -> float:
            achieved = float(_power_components(test, p, fixed_effect, a, size)["power"])
            return achieved - (1.0 - ratio * a)
        low, high = 1e-12, upper - 1e-12
        if balance(low) > 0 or balance(high) < 0:
            raise ValidationError("Uzlaşma çözümü bulunamadı.", "NO_SOLUTION", "beta_alpha_ratio")
        for _ in range(100):
            mid = (low + high) / 2.0
            if balance(mid) >= 0:
                high = mid
            else:
                low = mid
        alpha = high
    else:
        alpha = float(p["alpha"])

    if mode == "sensitivity":
        effect = _bisect_increasing(lambda e: float(_power_components(test, p, e, alpha, size)["power"]), target, 0.0, 1000.0)
    else:
        effect = fixed_effect
    components = _power_components(test, p, effect, alpha, size)
    return _normalized_result(test, mode, p, size, components, float(effect), alpha, float(components["power"]))
