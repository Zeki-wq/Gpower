"""
Validation tests running the computation engine against all oracle CSV datasets.
"""

import os
import csv
import math
import pytest
from src.calculator import compute_a_priori, compute_post_hoc

ORACLE_DIR = os.path.join(os.path.dirname(__file__), "..", "oracle")


def test_oracle_csv_files_exist():
    assert os.path.isdir(ORACLE_DIR), "oracle dizini mevcut olmalıdır."
    ap_csv = os.path.join(ORACLE_DIR, "vectors_a_priori.csv")
    ph_csv = os.path.join(ORACLE_DIR, "vectors_post_hoc.csv")
    comp_csv = os.path.join(ORACLE_DIR, "vectors_comparison_500.csv")

    assert os.path.isfile(ap_csv), f"{ap_csv} dosyası mevcut olmalıdır."
    assert os.path.isfile(ph_csv), f"{ph_csv} dosyası mevcut olmalıdır."
    assert os.path.isfile(comp_csv), f"{comp_csv} dosyası mevcut olmalıdır."


def test_validate_a_priori_vectors():
    """Validates engine against vectors_a_priori.csv."""
    filepath = os.path.join(ORACLE_DIR, "vectors_a_priori.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) >= 20, "En az 20 A priori test vektörü bulunmalıdır."

    seen_ids = set()
    for row in rows:
        vid = row["VectorID"]
        assert vid not in seen_ids, f"Tekrarlayan VectorID bulundu: {vid}"
        seen_ids.add(vid)

        tails = int(row["Tails"])
        d = float(row["EffectSize_d"])
        alpha = float(row["Alpha"])
        target_pwr = float(row["TargetPower"])
        ratio = float(row["AllocationRatio_N2_over_N1"])

        expected_n1 = int(row["N1"])
        expected_n2 = int(row["N2"])
        expected_total = int(row["Total_N"])
        expected_df = int(row["df"])
        expected_delta = float(row["NoncentralityParameter_delta"])
        expected_tcrit = float(row["Critical_t"])
        expected_actual_pwr = float(row["ActualPower"])

        res = compute_a_priori(tails=tails, d=d, alpha=alpha, power=target_pwr, ratio=ratio)

        assert res["n1"] == expected_n1, f"[{vid}] N1 uyuşmazlığı: {res['n1']} != {expected_n1}"
        assert res["n2"] == expected_n2, f"[{vid}] N2 uyuşmazlığı: {res['n2']} != {expected_n2}"
        assert res["total_n"] == expected_total, f"[{vid}] Total N uyuşmazlığı"
        assert res["df"] == expected_df, f"[{vid}] df uyuşmazlığı"
        assert math.isclose(res["delta"], expected_delta, abs_tol=1e-4), f"[{vid}] delta uyuşmazlığı"
        assert math.isclose(res["critical_t"], expected_tcrit, abs_tol=1e-4), f"[{vid}] critical_t uyuşmazlığı"
        assert math.isclose(res["actual_power"], expected_actual_pwr, abs_tol=1e-4), f"[{vid}] actual_power uyuşmazlığı"


def test_validate_post_hoc_vectors():
    """Validates engine against vectors_post_hoc.csv."""
    filepath = os.path.join(ORACLE_DIR, "vectors_post_hoc.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) >= 20, "En az 20 Post hoc test vektörü bulunmalıdır."

    seen_ids = set()
    for row in rows:
        vid = row["VectorID"]
        assert vid not in seen_ids, f"Tekrarlayan VectorID bulundu: {vid}"
        seen_ids.add(vid)

        tails = int(row["Tails"])
        d = float(row["EffectSize_d"])
        alpha = float(row["Alpha"])
        n1 = int(row["N1"])
        n2 = int(row["N2"])

        expected_total = int(row["Total_N"])
        expected_df = int(row["df"])
        expected_delta = float(row["NoncentralityParameter_delta"])
        expected_tcrit = float(row["Critical_t"])
        expected_pwr = float(row["AchievedPower"])

        res = compute_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)

        assert res["total_n"] == expected_total, f"[{vid}] Total N uyuşmazlığı"
        assert res["df"] == expected_df, f"[{vid}] df uyuşmazlığı"
        assert math.isclose(res["delta"], expected_delta, abs_tol=1e-4), f"[{vid}] delta uyuşmazlığı"
        assert math.isclose(res["critical_t"], expected_tcrit, abs_tol=1e-4), f"[{vid}] critical_t uyuşmazlığı"
        assert math.isclose(res["actual_power"], expected_pwr, abs_tol=1e-4), f"[{vid}] actual_power uyuşmazlığı"


def test_validate_500_comparison_vectors():
    """Validates engine against vectors_comparison_500.csv."""
    filepath = os.path.join(ORACLE_DIR, "vectors_comparison_500.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 500, f"500 karşılaştırma vektörü bekleniyordu, bulunan: {len(rows)}"

    for row in rows:
        cid = row["CaseID"]
        tails = int(row["Tails"])
        d = float(row["EffectSize_d"])
        alpha = float(row["Alpha"])
        n1 = int(row["N1"])
        n2 = int(row["N2"])

        expected_df = int(row["df"])
        expected_delta = float(row["delta"])
        expected_tcrit = float(row["critical_t"])
        expected_pwr = float(row["achieved_power"])

        res = compute_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)

        assert res["df"] == expected_df, f"[{cid}] df uyuşmazlığı"
        assert math.isclose(res["delta"], expected_delta, abs_tol=1e-4), f"[{cid}] delta uyuşmazlığı"
        assert math.isclose(res["critical_t"], expected_tcrit, abs_tol=1e-4), f"[{cid}] critical_t uyuşmazlığı"
        assert math.isclose(res["actual_power"], expected_pwr, abs_tol=1e-4), f"[{cid}] actual_power uyuşmazlığı"
