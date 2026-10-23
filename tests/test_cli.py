import json

from src.cli import main


def parse_stdout(capsys):
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    return json.loads(captured.out)


def test_cli_a_priori_success_and_contract_fields(capsys):
    code = main(["--test", "t2-indep", "--mode", "a-priori", "--tails", "1", "--d", "0.5",
                 "--alpha", "0.05", "--power", "0.95", "--ratio", "1"])
    assert code == 0
    result = parse_stdout(capsys)
    assert result["n1"] == result["n2"] == 88
    assert result["n_total"] == 176
    assert type(result["df"]) is int


def test_cli_compact_post_hoc_json(capsys):
    assert main(["--test", "t2-indep", "--mode", "post-hoc", "--tails", "2", "--d", "0.5",
                 "--alpha", "0.05", "--n1", "50", "--n2", "50"]) == 0
    result = parse_stdout(capsys)
    assert result["df"] == 98 and result["power"] > 0.69


def test_cli_version_matches_contract_schema(capsys):
    assert main(["--version"]) == 0
    result = parse_stdout(capsys)
    assert result["contract_version"] == "1.0.0"
    assert result["name"] == "Zeki"
    assert result["engine"].startswith("Python ")
    assert set(result) == {"contract_version", "name", "engine"}


def test_cli_missing_required_field_uses_contract_error(capsys):
    assert main(["--test", "t2-indep", "--mode", "a-priori", "--tails", "1", "--d", "0.5"]) == 2
    result = parse_stdout(capsys)
    assert result["code"] == "MISSING_PARAM" and result["field"] == "alpha"


def test_cli_unknown_or_irrelevant_param_uses_contract_error(capsys):
    assert main(["--test", "t2-indep", "--mode", "post-hoc", "--tails", "1", "--d", "0.5",
                 "--alpha", "0.05", "--n1", "30", "--n2", "30", "--power", "0.8"]) == 2
    result = parse_stdout(capsys)
    assert result["code"] == "UNKNOWN_PARAM" and result["field"] == "power"


def test_cli_unknown_family_is_unsupported(capsys):
    assert main(["--test", "not-a-test", "--mode", "post-hoc"]) == 2
    result = parse_stdout(capsys)
    assert result["code"] == "UNSUPPORTED" and result["field"] == "test"


def test_cli_out_of_range_is_exit_two(capsys):
    assert main(["--test", "t2-indep", "--mode", "a-priori", "--tails", "2", "--d", "-0.5",
                 "--alpha", "0.05", "--power", "0.8", "--ratio", "1"]) == 2
    result = parse_stdout(capsys)
    assert result["code"] == "OUT_OF_RANGE" and result["field"] == "d"


def test_cli_integer_decimal_rejected_as_invalid(capsys):
    assert main(["--test", "t-paired", "--mode", "post-hoc", "--dz", "0.5", "--alpha", "0.05",
                 "--n_total", "20.5"]) == 2
    result = parse_stdout(capsys)
    assert result["code"] == "INVALID_VALUE"
