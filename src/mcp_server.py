"""Contract-v1 MCP stdio server exposing only the canonical power_analysis tool."""

from typing import Any, Optional

from mcp.server.mcpserver import MCPServer

from src.calculator import ValidationError, compute_power_analysis

app = MCPServer("gpower-clone-mcp")


@app.tool()
def power_analysis(
    test: str,
    mode: str,
    tails: Optional[int] = None,
    d: Optional[float] = None,
    dz: Optional[float] = None,
    f: Optional[float] = None,
    w: Optional[float] = None,
    f2: Optional[float] = None,
    alpha: Optional[float] = None,
    power: Optional[float] = None,
    ratio: Optional[float] = None,
    n1: Optional[int] = None,
    n2: Optional[int] = None,
    n_total: Optional[int] = None,
    groups: Optional[int] = None,
    df: Optional[int] = None,
    predictors: Optional[int] = None,
    beta_alpha_ratio: Optional[float] = None,
) -> dict[str, Any]:
    """Run the shared calculation dispatcher and return contract-shaped JSON."""
    parameters = {
        name: value for name, value in locals().items()
        if name not in {"test", "mode"} and value is not None
    }
    try:
        return compute_power_analysis(test, mode, **parameters)
    except ValidationError as error:
        return {"error": str(error), "code": error.code, "field": error.field}
    except Exception as error:
        return {"error": str(error), "code": "INTERNAL", "field": None}


def run_stdio() -> None:
    """Run the MCP server over stdio transport."""
    app.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
