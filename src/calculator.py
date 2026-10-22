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
    pass


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

    if tails not in (1, 2):
        raise ValidationError(f"Geçersiz kuyruk sayısı: {tails}. 1 veya 2 olmalıdır.")

    if not isinstance(d, (int, float)) or math.isnan(d) or math.isinf(d):
        raise ValidationError("Etki büyüklüğü (d) geçerli bir sayı olmalıdır.")
    if d <= 0:
        raise ValidationError(f"Etki büyüklüğü (d) pozitif olmalıdır (> 0). Girilen: {d}")

    if not isinstance(alpha, (int, float)) or math.isnan(alpha) or math.isinf(alpha):
        raise ValidationError("Alfa (alpha) geçerli bir sayı olmalıdır.")
    if not (0 < alpha < 1):
        raise ValidationError(f"Alfa (alpha) (0, 1) aralığında olmalıdır. Girilen: {alpha}")

    if mode == "a-priori":
        if power is None or not isinstance(power, (int, float)) or math.isnan(power) or math.isinf(power):
            raise ValidationError("A priori analiz için hedef güç (power) belirtilmelidir.")
        if not (0 < power < 1):
            raise ValidationError(f"Hedef güç (power) (0, 1) aralığında olmalıdır. Girilen: {power}")

        if ratio is None or not isinstance(ratio, (int, float)) or math.isnan(ratio) or math.isinf(ratio):
            raise ValidationError("Grup tahsis oranı (ratio = N2/N1) belirtilmelidir.")
        if ratio <= 0:
            raise ValidationError(f"Grup tahsis oranı (N2/N1) pozitif olmalıdır (> 0). Girilen: {ratio}")

    elif mode == "post-hoc":
        if n1 is None or not isinstance(n1, int) or n1 < 2:
            raise ValidationError(f"Grup 1 örneklem büyüklüğü (n1) en az 2 olmalıdır. Girilen: {n1}")
        if n2 is None or not isinstance(n2, int) or n2 < 2:
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
