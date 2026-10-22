"""
G*Power Clone - Natural Language AI Agent Module
Interacts with the user in natural language, extracts parameters,
calls MCP/calculator tools, explains statistical metrics,
and enforces strict safety/clinical disclaimers.
"""

import re
import sys
from typing import Dict, Any, Optional, Tuple, List
from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    ValidationError,
)

CLINICAL_DISCLAIMER = (
    "ÖNEMLİ BİLGİLENDİRME VE FERAGATNAME:\n"
    "Bu hesaplama sonuçları yalnızca akademik, istatistiksel planlama ve eğitim amaçlıdır. "
    "Klinik/tıbbi bir tavsiye, tanı, tedavi önerisi veya araştırma başarısı garantisi niteliği taşımaz. "
    "Klinik çalışma tasarımlarında ilgili etik kurul ve regülasyon kılavuzlarına başvurulmalıdır."
)


class GPowerAgent:
    """Natural Language Assistant for G*Power statistical power analysis."""

    def __init__(self) -> None:
        self.disclaimer = CLINICAL_DISCLAIMER

    def parse_query(self, text: str) -> Dict[str, Any]:
        """Extracts analysis mode and numerical parameters from natural language input."""
        cleaned = text.lower()
        extracted: Dict[str, Any] = {
            "mode": None,
            "tails": None,
            "d": None,
            "alpha": None,
            "power": None,
            "ratio": None,
            "n1": None,
            "n2": None,
            "assumptions": [],
        }

        # 1. Mode Detection
        if any(w in cleaned for w in ["a priori", "apriori", "örneklem büyüklüğü", "kaç denek", "kaç kişi", "kaç hasta", "gereklidir", "örneklem hesabı"]):
            extracted["mode"] = "a-priori"
        elif any(w in cleaned for w in ["post hoc", "posthoc", "gerçekleşen güç", "güç nedir", "gücü nedir", "gücü hesapla"]):
            extracted["mode"] = "post-hoc"

        # 2. Extract Tails
        if any(w in cleaned for w in ["tek kuyruk", "tek yönlü", "one-tail", "one tail"]):
            extracted["tails"] = 1
        elif any(w in cleaned for w in ["çift kuyruk", "iki kuyruk", "iki yönlü", "two-tail", "two tail"]):
            extracted["tails"] = 2

        # 3. Extract Effect Size (d)
        d_match = re.search(r"(?:d|etki\s*büyüklüğü|cohen['’]?s?\s*d)\s*[=:]?\s*([0-9]+(?:\.[0-9]+)?)", cleaned)
        if d_match:
            extracted["d"] = float(d_match.group(1))
        elif "küçük etki" in cleaned:
            extracted["d"] = 0.2
            extracted["assumptions"].append("Küçük etki büyüklüğü için Cohen's d = 0.2 kabul edildi.")
        elif "orta etki" in cleaned:
            extracted["d"] = 0.5
            extracted["assumptions"].append("Orta etki büyüklüğü için Cohen's d = 0.5 kabul edildi.")
        elif "büyük etki" in cleaned:
            extracted["d"] = 0.8
            extracted["assumptions"].append("Büyük etki büyüklüğü için Cohen's d = 0.8 kabul edildi.")

        # 4. Extract Alpha
        alpha_match = re.search(r"(?:alpha|alfa|anlamlılık(?:\s*düzeyi)?)\s*[=:]?\s*([0-9]+(?:\.[0-9]+)?)", cleaned)
        if alpha_match:
            extracted["alpha"] = float(alpha_match.group(1))
        elif "yüzde 5" in cleaned or "%5" in cleaned:
            extracted["alpha"] = 0.05
        elif "yüzde 1" in cleaned or "%1" in cleaned:
            extracted["alpha"] = 0.01

        # 5. Extract Power (1 - beta)
        power_match = re.search(r"(?:power|hedef\s*güç)\s*[=:]?\s*([0-9]+(?:\.[0-9]+)?)", cleaned)
        if power_match:
            val = float(power_match.group(1))
            extracted["power"] = val / 100.0 if val > 1.0 else val
        else:
            pct_match = re.search(r"(?:yüzde|%)\s*([0-9]+(?:\.[0-9]+)?)\s*güç", cleaned)
            if pct_match:
                extracted["power"] = float(pct_match.group(1)) / 100.0

        # 6. Extract Allocation Ratio (N2/N1)
        ratio_match = re.search(r"(?:oran|ratio|n2/n1|grup\s*oranı)\s*[=:]?\s*([0-9]+(?:\.[0-9]+)?)", cleaned)
        if ratio_match:
            extracted["ratio"] = float(ratio_match.group(1))
        elif "2:1" in cleaned or "2 kat" in cleaned:
            extracted["ratio"] = 2.0
            extracted["assumptions"].append("Grup oranı 2:1 (N2/N1 = 2.0) kabul edildi.")
        elif "eşit grup" in cleaned or "dengeli grup" in cleaned:
            extracted["ratio"] = 1.0

        # 7. Extract Sample Sizes (N1, N2)
        # Check specific drug/placebo or group 1/2 mentions first
        drug_match = re.search(r"(?:ilaç|deney|müdahale|tedavi)\s*(?:grubunda|grubunda\s*da|grubu)?\s*([0-9]+)", cleaned)
        placebo_match = re.search(r"(?:plasebo|kontrol)\s*(?:grubunda|grubunda\s*da|grubu)?\s*([0-9]+)", cleaned)
        n1_match = re.search(r"(?:n1|grup\s*1)\s*[=:]?\s*([0-9]+)", cleaned)
        n2_match = re.search(r"(?:n2|grup\s*2)\s*[=:]?\s*([0-9]+)", cleaned)

        if drug_match and placebo_match:
            extracted["n1"] = int(drug_match.group(1))
            extracted["n2"] = int(placebo_match.group(1))
        elif n1_match and n2_match:
            extracted["n1"] = int(n1_match.group(1))
            extracted["n2"] = int(n2_match.group(1))
        else:
            n_per_group = re.search(r"(?:grup\s*başına|her\s*(?:iki\s*)?grupta)\s*([0-9]+)", cleaned)
            n_each_match = re.search(r"([0-9]+)\s*['’]?(?:şer|sar|ser|er|ar)?\s*(?:kişi|denek|hasta|örneklem|katılımcı)", cleaned)
            if n_per_group:
                val = int(n_per_group.group(1))
                extracted["n1"] = val
                extracted["n2"] = val
            elif n_each_match:
                val = int(n_each_match.group(1))
                extracted["n1"] = val
                extracted["n2"] = val

        # Fallback Mode inference
        if extracted["mode"] is None:
            if extracted["n1"] is not None and extracted["n2"] is not None:
                extracted["mode"] = "post-hoc"
            elif extracted["power"] is not None:
                extracted["mode"] = "a-priori"

        return extracted

    def process_query(self, text: str) -> str:
        """Processes user natural language request, validates, computes, and explains."""
        params = self.parse_query(text)
        mode = params["mode"]

        if mode is None:
            return (
                "Hangi analiz türünü gerçekleştirmek istediğinizi tam anlayamadım.\n"
                "Lütfen analizinizi belirtin:\n"
                "1. **A Priori Analiz:** Belirli bir hedef güç için kaç deneğe/hastaya ihtiyaç olduğunu hesaplar.\n"
                "2. **Post Hoc Analiz:** Mevcut örneklem büyüklüğü ile çalışmanın ulaştığı gücü hesaplar.\n\n"
                f"{self.disclaimer}"
            )

        # A Priori Flow
        if mode == "a-priori":
            missing: List[str] = []
            if params["d"] is None:
                missing.append("- Etki Büyüklüğü (Cohen's d): Belirtilmedi. Örneğin küçük: 0.2, orta: 0.5, büyük: 0.8.")
            if params["power"] is None:
                missing.append("- Hedef Güç (Power): Belirtilmedi (örneğin %80 veya 0.80).")

            if missing:
                msg = ["A priori örneklem hesabı için eksik parametreler var:"]
                msg.extend(missing)
                msg.append("\nLütfen bu değerleri belirterek tekrar sorunuz (Eksik parametreler tahmin edilmemektedir).")
                msg.append(f"\n{self.disclaimer}")
                return "\n".join(msg)

            # Apply explicit defaults if not provided
            if params["alpha"] is None:
                params["alpha"] = 0.05
                params["assumptions"].append("Alfa anlamlılık düzeyi varsayılan 0.05 (%5) kabul edildi.")
            if params["tails"] is None:
                params["tails"] = 2
                params["assumptions"].append("Test yönü varsayılan olarak iki kuyruklu (two-tailed) kabul edildi.")
            if params["ratio"] is None:
                params["ratio"] = 1.0
                params["assumptions"].append("Grup tahsis oranı (N2/N1) varsayılan 1.0 (eşit gruplar) kabul edildi.")

            try:
                res = compute_a_priori(
                    tails=params["tails"],
                    d=params["d"],
                    alpha=params["alpha"],
                    power=params["power"],
                    ratio=params["ratio"],
                )
            except ValidationError as ve:
                return f"Parametre doğrulama hatası: {str(ve)}\n\n{self.disclaimer}"

            return self.format_a_priori_explanation(res, params["assumptions"])

        # Post Hoc Flow
        elif mode == "post-hoc":
            missing = []
            if params["d"] is None:
                missing.append("- Etki Büyüklüğü (Cohen's d): Belirtilmedi.")
            if params["n1"] is None or params["n2"] is None:
                missing.append("- Örneklem Büyüklükleri (N1 ve N2): Belirtilmedi (örneğin 'grup başına 50 kişi').")

            if missing:
                msg = ["Post hoc güç hesabı için eksik parametreler var:"]
                msg.extend(missing)
                msg.append("\nLütfen bu değerleri sağlayınız.")
                msg.append(f"\n{self.disclaimer}")
                return "\n".join(msg)

            if params["alpha"] is None:
                params["alpha"] = 0.05
                params["assumptions"].append("Alfa anlamlılık düzeyi varsayılan 0.05 (%5) kabul edildi.")
            if params["tails"] is None:
                params["tails"] = 2
                params["assumptions"].append("Test yönü varsayılan olarak iki kuyruklu (two-tailed) kabul edildi.")

            try:
                res = compute_post_hoc(
                    tails=params["tails"],
                    d=params["d"],
                    alpha=params["alpha"],
                    n1=params["n1"],
                    n2=params["n2"],
                )
            except ValidationError as ve:
                return f"Parametre doğrulama hatası: {str(ve)}\n\n{self.disclaimer}"

            return self.format_post_hoc_explanation(res, params["assumptions"])

        return f"Bilinmeyen mod.\n\n{self.disclaimer}"

    def format_a_priori_explanation(self, res: Dict[str, Any], assumptions: List[str]) -> str:
        lines = [
            "### G*Power İki Bağımsız Grup t-Testi: A Priori Örneklem Büyüklüğü Sonucu\n",
            "Hesaplama başarıyla tamamlandı. Belirtilen koşullar altında hedef istatistiksel gücü sağlayan en küçük tamsayı örneklem sayıları aşağıdadır:\n",
        ]
        if assumptions:
            lines.append("**Kullanılan Varsayımlar:**")
            for a in assumptions:
                lines.append(f"- {a}")
            lines.append("")

        lines.extend([
            "**Temel Parametreler ve Sonuçlar:**",
            f"- **Test Türü:** İki bağımsız grubun ortalamaları için Student t-testi (İlaç vs Plasebo)",
            f"- **Kuyruk Seçimi:** {res['tails']} kuyruklu ({'Tek kuyruk (one-tailed)' if res['tails'] == 1 else 'Çift kuyruk (two-tailed)'})",
            f"- **Etki Büyüklüğü (Cohen's d):** {res['d']}",
            f"- **Tip I Hata Oranı (Alfa):** {res['alpha']}",
            f"- **Hedef Güç (Target Power):** {res['target_power']}",
            f"- **Grup Tahsis Oranı (N2/N1):** {res['ratio']}",
            "--------------------------------------------------",
            f"- **Grup 1 Örneklem Büyüklüğü (N1):** **{res['n1']}** denek",
            f"- **Grup 2 Örneklem Büyüklüğü (N2):** **{res['n2']}** denek",
            f"- **Toplam Gereken Örneklem (Total N):** **{res['total_n']}** denek",
            f"- **Serbestlik Derecesi (df):** {res['df']}",
            f"- **Noncentrality Parameter (delta):** {res['delta']:.6f}",
            f"- **Kritik t Değeri (Critical t):** {res['critical_t']:.6f}",
            f"- **Gerçekleşen İstatistiksel Güç (Actual Power):** **{res['actual_power']:.6f}** (Hedef %{res['target_power']*100:.1f} sağlanmıştır)",
            "--------------------------------------------------",
            f"\n{self.disclaimer}",
        ])
        return "\n".join(lines)

    def format_post_hoc_explanation(self, res: Dict[str, Any], assumptions: List[str]) -> str:
        ratio = res["n2"] / res["n1"]
        lines = [
            "### G*Power İki Bağımsız Grup t-Testi: Post Hoc Güç Analizi Sonucu\n",
            "Hesaplama başarıyla tamamlandı. Mevcut çalışma parametrelerine göre gerçekleşen istatistiksel güç aşağıdadır:\n",
        ]
        if assumptions:
            lines.append("**Kullanılan Varsayımlar:**")
            for a in assumptions:
                lines.append(f"- {a}")
            lines.append("")

        lines.extend([
            "**Temel Parametreler ve Sonuçlar:**",
            f"- **Test Türü:** İki bağımsız grup t-testi (İlaç vs Plasebo)",
            f"- **Kuyruk Seçimi:** {res['tails']} kuyruklu ({'Tek kuyruk' if res['tails'] == 1 else 'Çift kuyruk'})",
            f"- **Etki Büyüklüğü (Cohen's d):** {res['d']}",
            f"- **Alfa Anlamlılık Düzeyi:** {res['alpha']}",
            f"- **Grup 1 Örneklemi (N1):** {res['n1']}",
            f"- **Grup 2 Örneklemi (N2):** {res['n2']}",
            f"- **Toplam Örneklem Büyüklüğü (Total N):** {res['total_n']}",
            f"- **Grup Oranı (N2/N1):** {ratio:.4f}",
            f"- **Serbestlik Derecesi (df):** {res['df']}",
            f"- **Noncentrality Parameter (delta):** {res['delta']:.6f}",
            f"- **Kritik t Değeri:** {res['critical_t']:.6f}",
            "--------------------------------------------------",
            f"- **Gerçekleşen İstatistiksel Güç (Achieved Power):** **%{res['actual_power']*100:.2f}** ({res['actual_power']:.6f})",
            "--------------------------------------------------",
            f"\n{self.disclaimer}",
        ])
        return "\n".join(lines)


def interactive_cli() -> None:
    """CLI REPL loop for the natural language agent."""
    agent = GPowerAgent()
    print("==================================================================")
    print("   G*Power Clone Doğal Dil Asistanı (GPower-Agent CLI)           ")
    print("   İlaç ve Plasebo İki Bağımsız Grup t-Testi Güç & Örneklem      ")
    print("   (Çıkmak için 'q', 'exit' veya 'quit' yazın)                   ")
    print("==================================================================\n")

    while True:
        try:
            query = input("GPower-Agent> ").strip()
            if not query:
                continue
            if query.lower() in ["q", "exit", "quit", "cikis", "çıkış"]:
                print("GPower-Agent kapatılıyor. İyi çalışmalar.")
                break
            response = agent.process_query(query)
            print("\n" + response + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGPower-Agent sonlandırıldı.")
            break


def main() -> None:
    """CLI entry point for gpower-agent supporting single-shot prompts and interactive mode."""
    import argparse
    parser = argparse.ArgumentParser(
        description="G*Power Clone Doğal Dil AI Ajanı - İki Bağımsız Grup t-Testi Güç ve Örneklem Analizi"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default=None,
        help="Analiz edilecek doğal dil sorgusu (örn: 'orta etki, %80 güç, 0.05 alfa için örneklem nedir?')"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Etkileşimli sohbet modunu başlatır."
    )
    args = parser.parse_args()

    agent = GPowerAgent()
    if args.prompt:
        response = agent.process_query(args.prompt)
        print(response)
    else:
        interactive_cli()


if __name__ == "__main__":
    main()


