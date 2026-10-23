import asyncio
import json
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.cli import main
from src.ui import fields_for

VECTORS = [json.loads(line) for line in Path("oracle/public_vectors.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]


def cli_call(inputs):
    args = []
    for key, value in inputs.items():
        args.extend((f"--{key}", str(value)))
    output = StringIO()
    with redirect_stdout(output):
        exit_code = main(args)
    assert exit_code == 0
    assert len(output.getvalue().splitlines()) == 1
    return json.loads(output.getvalue())


def response_result(response):
    structured = getattr(response, "structuredContent", getattr(response, "structured_content", None))
    if structured is not None:
        result = dict(structured)
        if set(result) == {"result"} and isinstance(result["result"], dict):
            return result["result"]
        return result
    for item in response.content:
        if getattr(item, "type", None) == "text":
            return json.loads(item.text)
    raise AssertionError("MCP tool returned no JSON result")


def test_all_contract_public_vectors_match_and_have_integer_fields():
    assert len(VECTORS) == 25
    for vector in VECTORS:
        result = cli_call(vector["input"])
        expected = vector["expected"]
        for field, value in expected.items():
            actual = result[field]
            if isinstance(value, int):
                assert type(actual) is int and actual == value, (vector["id"], field, actual, value)
            else:
                assert abs(actual - value) <= 1e-6, (vector["id"], field, actual, value)
        assert set(fields_for(vector["input"]["test"], vector["input"]["mode"])) >= set(vector["input"]) - {"test", "mode"}


def test_real_mcp_stdio_exposes_one_tool_and_matches_cli_for_all_vectors():
    async def run_vectors():
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src.mcp_server"],
            env=os.environ.copy(),
        )
        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert [tool.name for tool in tools.tools] == ["power_analysis"]
                for vector in VECTORS:
                    response = await session.call_tool("power_analysis", arguments=vector["input"])
                    assert not getattr(response, "isError", getattr(response, "is_error", False)), vector["id"]
                    assert response_result(response) == cli_call(vector["input"]), vector["id"]

    asyncio.run(run_vectors())
