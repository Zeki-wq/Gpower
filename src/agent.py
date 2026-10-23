"""LLM-backed natural-language agent that delegates calculations to MCP."""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CLINICAL_DISCLAIMER = (
    "Eğitim ve istatistiksel planlama amaçlıdır; klinik tavsiye veya tedavi önerisi değildir. "
    "Gerçek kişilere ait sağlık verisi girmeyin."
)
SENSITIVE_INPUT_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:T\.C\.?\s*kimlik|TC\s*kimlik)\s*(?:no(?:su)?\s*)?[:=]?\s*\d{11}\b", re.IGNORECASE),
    re.compile(r"(?<!\d)(?:\+?90[\s().-]?)?0?5\d{2}(?:[\s.-]?\d{3})(?:[\s.-]?\d{2}){2}(?!\d)"),
    re.compile(r"\b(?:my patient|my client|hastam|hastanın|gerçek hasta|patient id)\b", re.IGNORECASE),
)
SYSTEM_PROMPT = """You convert a hypothetical research question into one power_analysis MCP input.
Return only a JSON object with either {"tool_input": {...}, "clarification": null} or
{"tool_input": null, "clarification": "..."}. Never calculate statistics.
Never invent missing numeric inputs. Ask for a Cohen effect size when only qualitative
labels such as small/medium/large are given; do not silently map those labels. The tool
schema accepts test, mode, tails, d, dz, f, w, f2, alpha, power, ratio, n1, n2,
n_total, groups, df, predictors, beta_alpha_ratio. Supported families are t2-indep,
t-paired, anova-oneway, chi2-contingency, and multireg-r2. Select the family matching
the question and include only fields valid for that family and mode.
Supported modes are a-priori, post-hoc, sensitivity, criterion, compromise.
Ask for missing required inputs. Requests involving real patients, identifiable people,
diagnosis, treatment, or clinical decisions must be declined. Do not include personal or
clinical information in tool_input."""


class AgentConfigurationError(RuntimeError):
    pass


class GPowerAgent:
    """Natural-language orchestration. A configured LLM parses; MCP computes."""

    def __init__(self, log_path: str | Path | None = None):
        project_root = Path(__file__).resolve().parent.parent
        self.log_path = Path(log_path) if log_path else project_root / "logs" / "agent_calls.jsonl"
        self.api_key = os.environ.get("GPOWER_LLM_API_KEY", "").strip()
        self.api_url = os.environ.get("GPOWER_LLM_API_URL", "https://api.openai.com/v1/chat/completions").strip()
        self.model = os.environ.get("GPOWER_LLM_MODEL", "").strip()
        self.pending_question: str | None = None
        self.pending_clarification: str | None = None

    def _log(self, question: str, tool_input: dict | None, tool_output: dict, tokens_in: int | None, tokens_out: int | None) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _contains_obvious_personal_data(question: str) -> bool:
        return any(pattern.search(question) for pattern in SENSITIVE_INPUT_PATTERNS)

    @staticmethod
    def _explain_result(result: dict[str, Any]) -> str:
        family = {
            "t2-indep": "iki bağımsız grup t testi",
            "t-paired": "eşleştirilmiş ölçümler t testi",
            "anova-oneway": "tek yönlü ANOVA",
            "chi2-contingency": "ki-kare uygunluk testi",
            "multireg-r2": "çoklu regresyon R² testi",
        }.get(result.get("test"), result.get("test", "istatistiksel test"))
        mode = result.get("mode")
        if mode == "a-priori":
            count = (f"N1={result['n1']} ve N2={result['n2']} (toplam {result['n_total']})"
                     if "n1" in result else f"toplam N={result['n_total']}")
            return f"{family} için hedef güç sağlandı: {count}; gerçekleşen güç {result['actual_power']:.6f}."
        if mode == "post-hoc":
            return f"Verilen örneklemle gerçekleşen güç {result['power']:.6f} (toplam N={result['n_total']})."
        if mode == "criterion":
            return f"Belirtilen hedef güce ulaşmak için gereken alfa {result['alpha']:.6f}."
        if mode == "sensitivity":
            effect = next(k for k in ("d", "dz", "f", "w", "f2") if k in result)
            return f"Belirtilen tasarımda hedef güce ulaşan en küçük {effect} etki büyüklüğü {result[effect]:.6f}."
        return (f"Uzlaşma çözümü: alfa={result['alpha']:.6f}, beta={result['beta']:.6f}, "
                f"güç={result['power']:.6f} (hedef oran beta/alfa={result['beta_alpha_ratio']:.6f}).")

    def _extract_with_llm(self, question: str, context: tuple[str, str] | None = None) -> tuple[dict[str, Any], int | None, int | None]:
        if not self.api_key or not self.model:
            raise AgentConfigurationError(
                "Gerçek agent için GPOWER_LLM_API_KEY ve GPOWER_LLM_MODEL ayarlayın. "
                "LLM yapılandırılmadığı için MCP çağrısı yapılmadı ve hesaplama üretilmedi."
            )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context:
            original_question, prior_clarification = context
            messages.extend([
                {"role": "user", "content": original_question},
                {"role": "assistant", "content": json.dumps({"tool_input": None, "clarification": prior_clarification})},
                {"role": "user", "content": question},
            ])
        else:
            messages.append({"role": "user", "content": question})
        body = json.dumps({
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": messages,
        }).encode("utf-8")
        request = urllib.request.Request(
            self.api_url,
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"LLM sağlayıcısı HTTP {error.code} hatası döndürdü.") from None
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(f"LLM sağlayıcısına erişilemedi: {error}") from None
        message = payload.get("choices", [{}])[0].get("message", {}).get("content")
        if not isinstance(message, str):
            raise RuntimeError("LLM yanıtında JSON içerik bulunamadı.")
        parsed = json.loads(message)
        if not isinstance(parsed, dict):
            raise RuntimeError("LLM yanıtı JSON nesnesi değil.")
        usage = payload.get("usage") or {}
        return parsed, usage.get("prompt_tokens"), usage.get("completion_tokens")

    async def _call_mcp(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src.mcp_server"],
            env=os.environ.copy(),
        )
        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.call_tool("power_analysis", arguments=tool_input)
        if getattr(response, "isError", getattr(response, "is_error", False)):
            raise RuntimeError("MCP power_analysis aracı başarısız oldu.")
        structured = getattr(response, "structuredContent", getattr(response, "structured_content", None))
        if structured is not None:
            value = dict(structured)
            if set(value) == {"result"} and isinstance(value["result"], dict):
                return value["result"]
            return value
        for item in response.content:
            if getattr(item, "type", None) == "text":
                parsed = json.loads(item.text)
                if isinstance(parsed, dict):
                    return parsed
        raise RuntimeError("MCP yanıtında okunabilir sonuç bulunamadı.")

    async def _process(self, question: str) -> str:
        context = None
        if self.pending_question and self.pending_clarification:
            context = (self.pending_question, self.pending_clarification)
        parsed, tokens_in, tokens_out = self._extract_with_llm(question, context)
        clarification = parsed.get("clarification")
        tool_input = parsed.get("tool_input")
        if clarification:
            self.pending_question = context[0] if context else question
            self.pending_clarification = str(clarification)
            output = {"status": "needs_clarification", "message": str(clarification)}
            self._log(question, None, output, tokens_in, tokens_out)
            return f"{clarification}\n\n{CLINICAL_DISCLAIMER}"
        if not isinstance(tool_input, dict):
            raise RuntimeError("LLM gerekli tool_input veya clarification alanını döndürmedi.")
        self.pending_question = None
        self.pending_clarification = None
        allowed = {"test", "mode", "tails", "d", "dz", "f", "w", "f2", "alpha", "power",
                   "ratio", "n1", "n2", "n_total", "groups", "df", "predictors", "beta_alpha_ratio"}
        if set(tool_input) - allowed or "test" not in tool_input or "mode" not in tool_input:
            raise RuntimeError("LLM tool_input şeması beklenen alanlarla uyuşmuyor.")
        tool_output = await self._call_mcp(tool_input)
        self._log(question, tool_input, tool_output, tokens_in, tokens_out)
        if tool_output.get("status") != "success":
            message = tool_output.get("error") or tool_output.get("message") or "Bilinmeyen araç hatası"
            return f"MCP hesaplaması başarısız: {message}\n\n{CLINICAL_DISCLAIMER}"
        explanation = self._explain_result(tool_output)
        return explanation + "\n\nMCP power_analysis ham sonucu:\n" + json.dumps(tool_output, ensure_ascii=False, indent=2) + f"\n\n{CLINICAL_DISCLAIMER}"

    def process_query(self, text: str) -> str:
        question = text.strip()
        if not question:
            return "Lütfen kurgusal/eğitim amaçlı bir araştırma sorusu yazın."
        if len(question) > 4000:
            return "Soru 4000 karakterden kısa olmalıdır. Gerçek kişi veya klinik veri girmeyin."
        if self._contains_obvious_personal_data(question):
            refusal = "Kişisel veya gerçek hasta bilgisi içeren istekler işlenmez. Lütfen yalnızca kurgusal araştırma girdileri kullanın."
            self._log("[REDACTED: personal data request]", None,
                      {"status": "refused", "message": "obvious_personal_data"}, None, None)
            return f"{refusal}\n\n{CLINICAL_DISCLAIMER}"
        try:
            return asyncio.run(self._process(question))
        except AgentConfigurationError as error:
            output = {"status": "not_run", "message": str(error)}
            self._log(question, None, output, None, None)
            return f"{error}\n\n{CLINICAL_DISCLAIMER}"
        except Exception as error:
            output = {"status": "error", "error_type": type(error).__name__, "message": str(error)}
            self._log(question, None, output, None, None)
            return f"Agent işlemi başarısız oldu: {error}\n\n{CLINICAL_DISCLAIMER}"


def interactive_cli() -> None:
    agent = GPowerAgent()
    print("G*Power Clone Agent — kurgusal/eğitim amaçlı senaryolar; gerçek kişi verisi girmeyin.")
    while True:
        try:
            question = input("GPower-Agent> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAgent kapatıldı.")
            return
        if question.lower() in {"q", "quit", "exit", "çıkış", "cikis"}:
            return
        print(agent.process_query(question) + "\n")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="LLM + MCP G*Power analiz agent'ı")
    parser.add_argument("--prompt", "-p")
    parser.add_argument("--interactive", "-i", action="store_true")
    args = parser.parse_args()
    if args.prompt:
        print(GPowerAgent().process_query(args.prompt))
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
