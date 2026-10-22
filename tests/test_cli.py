"""
Tests for the CLI interface (src/cli.py).
"""

import json
from io import StringIO
import pytest
from src.cli import main


class TestCLIInvocations:
    """Verifies CLI argument handling, exit codes, and JSON outputs."""

    def test_cli_a_priori_success(self, monkeypatch, capsys):
        args = [
            "--test", "t2-indep",
            "--mode", "a-priori",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--power", "0.80",
            "--ratio", "1.0",
        ]
        exit_code = main(args)
        assert exit_code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "success"
        assert data["n1"] == 64
        assert data["n2"] == 64
        assert data["total_n"] == 128
        assert data["df"] == 126
        assert data["actual_power"] >= 0.80

    def test_cli_post_hoc_success(self, capsys):
        args = [
            "--test", "t2-indep",
            "--mode", "post-hoc",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--n1", "50",
            "--n2", "50",
        ]
        exit_code = main(args)
        assert exit_code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "success"
        assert data["df"] == 98
        assert data["delta"] == 2.5
        assert data["critical_t"] == 1.984467

    def test_cli_text_format(self, capsys):
        args = [
            "--mode", "post-hoc",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--n1", "50",
            "--n2", "50",
            "--format", "text",
        ]
        exit_code = main(args)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "G*POWER CLONE - HESAPLAMA SONUÇLARI" in captured.out
        assert "Gerçekleşen Güç:" in captured.out

    def test_cli_validation_error_negative_d(self, capsys):
        args = [
            "--mode", "a-priori",
            "--tails", "2",
            "--d", "-0.5",
            "--alpha", "0.05",
            "--power", "0.80",
        ]
        exit_code = main(args)
        assert exit_code == 1
        captured = capsys.readouterr()
        data = json.loads(captured.err)
        assert data["status"] == "error"
        assert data["error_type"] == "ValidationError"

    def test_cli_missing_required_power_in_a_priori(self, capsys):
        args = [
            "--mode", "a-priori",
            "--d", "0.5",
            "--alpha", "0.05",
        ]
        exit_code = main(args)
        assert exit_code == 1
        captured = capsys.readouterr()
        data = json.loads(captured.err)
        assert data["status"] == "error"
        assert "zorunludur" in data["message"]
