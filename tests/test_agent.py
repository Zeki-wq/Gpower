import asyncio
import json

from src.agent import GPowerAgent


def test_agent_without_llm_credentials_does_not_fabricate_or_calculate(tmp_path, monkeypatch):
    monkeypatch.delenv("GPOWER_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GPOWER_LLM_MODEL", raising=False)
    log_path = tmp_path / "agent_calls.jsonl"
    response = GPowerAgent(log_path=log_path).process_query("Kurgusal çalışma için d=0.5, güç=0.8")

    assert "GPOWER_LLM_API_KEY" in response
    assert "MCP çağrısı yapılmadı" in response
    record = json.loads(log_path.read_text(encoding="utf-8"))
    assert set(record) == {"ts", "question", "tool_input", "tool_output", "tokens_in", "tokens_out"}
    assert record["tool_input"] is None
    assert record["tool_output"]["status"] == "not_run"
    assert record["tokens_in"] is None and record["tokens_out"] is None


def test_agent_calls_real_mcp_stdio_server():
    agent = GPowerAgent()
    result = asyncio.run(agent._call_mcp({
        "test": "t2-indep", "mode": "a-priori", "tails": 2,
        "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0,
    }))
    assert result["status"] == "success"
    assert result["n1"] == 64 and result["n2"] == 64


def test_agent_mcp_returns_contract_error_for_unknown_family():
    result = asyncio.run(GPowerAgent()._call_mcp({
        "test": "not-a-test", "mode": "post-hoc",
    }))
    assert result["code"] == "UNSUPPORTED"
    assert result["field"] == "test"
    assert "error" in result


def test_agent_rejects_empty_or_oversized_questions(tmp_path):
    agent = GPowerAgent(log_path=tmp_path / "agent_calls.jsonl")
    assert "Lütfen" in agent.process_query("  ")
    assert "4000 karakter" in agent.process_query("x" * 4001)
    assert not (tmp_path / "agent_calls.jsonl").exists()


def test_agent_blocks_obvious_personal_data_before_llm_and_redacts_log(tmp_path, monkeypatch):
    agent = GPowerAgent(log_path=tmp_path / "agent_calls.jsonl")
    monkeypatch.setattr(agent, "_extract_with_llm", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("LLM must not be called")))
    private_question = "My patient has ID 12345 and can be reached at zeki@example.com"
    answer = agent.process_query(private_question)
    assert "kişisel" in answer.lower()
    record = json.loads((tmp_path / "agent_calls.jsonl").read_text(encoding="utf-8"))
    assert record["question"] == "[REDACTED: personal data request]"
    assert "zeki@example.com" not in json.dumps(record)
    assert record["tool_output"]["status"] == "refused"


def test_agent_detects_phone_number_pattern():
    assert GPowerAgent._contains_obvious_personal_data("İletişim numarası 0532 123 45 67")


def test_agent_carries_clarification_into_follow_up_then_calls_real_mcp(tmp_path, monkeypatch):
    agent = GPowerAgent(log_path=tmp_path / "agent_calls.jsonl")
    calls = []
    answers = [
        ({"tool_input": None, "clarification": "Hedef gücü belirtir misiniz?"}, 12, 8),
        ({"tool_input": {"test": "t2-indep", "mode": "a-priori", "tails": 1,
                         "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0},
          "clarification": None}, 18, 10),
    ]

    def parse(question, context=None):
        calls.append((question, context))
        return answers.pop(0)

    monkeypatch.setattr(agent, "_extract_with_llm", parse)
    first = agent.process_query("Kurgusal iki grup için örneklem sayısı")
    assert "Hedef gücü belirtir misiniz?" in first
    second = agent.process_query("0.95")
    assert "N1=88 ve N2=88" in second
    assert calls[0] == ("Kurgusal iki grup için örneklem sayısı", None)
    assert calls[1] == ("0.95", ("Kurgusal iki grup için örneklem sayısı", "Hedef gücü belirtir misiniz?"))
    logs = [json.loads(line) for line in (tmp_path / "agent_calls.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(logs) == 2
    assert logs[1]["tool_output"]["n1"] == logs[1]["tool_output"]["n2"] == 88
