"""Contract-v1 CLI for the shared power-analysis engine."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from src import __version__
from src.calculator import ValidationError, compute_power_analysis

CONTRACT_VERSION = "1.0.0"
TEAM_NAME = "Zeki"


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        unknown = "unrecognized arguments" in message
        out = {"error": message, "code": "UNKNOWN_PARAM" if unknown else "INVALID_VALUE", "field": None}
        print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        raise SystemExit(2)


def create_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(prog="gpower-clone", add_help=True)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--test")
    parser.add_argument("--mode")
    parser.add_argument("--tails", type=int)
    for name in ("d", "dz", "f", "w", "f2", "alpha", "power", "ratio", "beta_alpha_ratio"):
        parser.add_argument(f"--{name}", type=float)
    for name in ("n1", "n2", "n_total", "groups", "df", "predictors"):
        parser.add_argument(f"--{name}", type=int)
    return parser


def _error(error: str, code: str, field: str | None) -> dict:
    return {"error": error, "code": code, "field": field}


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_error:
        return int(exit_error.code or 0)

    if args.version:
        print(json.dumps({
            "contract_version": CONTRACT_VERSION,
            "name": TEAM_NAME,
            "engine": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }, ensure_ascii=False, separators=(",", ":")))
        return 0

    if args.test is None:
        print(json.dumps(_error("--test alanı gereklidir.", "MISSING_PARAM", "test"), ensure_ascii=False, separators=(",", ":")))
        return 2
    if args.mode is None:
        print(json.dumps(_error("--mode alanı gereklidir.", "MISSING_PARAM", "mode"), ensure_ascii=False, separators=(",", ":")))
        return 2

    parameters = {}
    for name, value in vars(args).items():
        if name in {"test", "mode", "version", "help"} or value is None:
            continue
        parameters[name] = value
    try:
        result = compute_power_analysis(args.test, args.mode, **parameters)
    except ValidationError as error:
        print(json.dumps(_error(str(error), error.code, error.field), ensure_ascii=False, separators=(",", ":")))
        return 1 if error.code == "NO_SOLUTION" else 2
    except Exception as error:
        print(json.dumps(_error(str(error), "INTERNAL", None), ensure_ascii=False, separators=(",", ":")))
        return 1

    print(json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
