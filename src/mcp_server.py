"""
G*Power Clone - Model Context Protocol (MCP) Server
Exposes G*Power statistical calculation tools via MCP protocol.
Uses src/calculator.py as the SINGLE source of truth.
"""

from typing import Dict, Any, Optional
from mcp.server.mcpserver import MCPServer
from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    ValidationError,
)

# Initialize MCP Server instance
app = MCPServer("gpower-clone-mcp")


@app.tool()
def compute_a_priori_sample_size(
    d: float,
    power: float,
    alpha: float = 0.05,
    tails: int = 2,
    ratio: float = 1.0,
) -> Dict[str, Any]:
    """
    Computes required sample size (A priori analysis) for two independent groups t-test.
    
    Args:
        d: Cohen's d effect size (> 0, e.g. 0.2 for small, 0.5 for medium, 0.8 for large).
        power: Target statistical power (1 - beta), e.g. 0.80 or 0.90.
        alpha: Significance level (Type I error prob, default: 0.05).
        tails: Number of tails, 1 (one-tailed) or 2 (two-tailed, default: 2).
        ratio: Allocation ratio N2/N1 (default: 1.0 for equal groups).
        
    Returns:
        Dictionary containing N1, N2, Total_N, df, delta, critical_t, and actual_power.
    """
    try:
        return compute_a_priori(
            tails=tails,
            d=d,
            alpha=alpha,
            power=power,
            ratio=ratio,
        )
    except ValidationError as ve:
        return {
            "status": "error",
            "error_type": "ValidationError",
            "message": str(ve),
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }


@app.tool()
def compute_post_hoc_power(
    d: float,
    n1: int,
    n2: int,
    alpha: float = 0.05,
    tails: int = 2,
) -> Dict[str, Any]:
    """
    Computes achieved statistical power (Post hoc analysis) for two independent groups t-test.
    
    Args:
        d: Cohen's d effect size (> 0).
        n1: Sample size of group 1 (integer >= 2).
        n2: Sample size of group 2 (integer >= 2).
        alpha: Significance level (default: 0.05).
        tails: Number of tails, 1 (one-tailed) or 2 (two-tailed, default: 2).
        
    Returns:
        Dictionary containing df, delta, critical_t, and achieved actual_power.
    """
    try:
        return compute_post_hoc(
            tails=tails,
            d=d,
            alpha=alpha,
            n1=n1,
            n2=n2,
        )
    except ValidationError as ve:
        return {
            "status": "error",
            "error_type": "ValidationError",
            "message": str(ve),
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }


def run_stdio() -> None:
    """Runs the MCP server over standard input/output (stdio transport)."""
    app.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
