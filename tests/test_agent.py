"""
Tests for Natural Language AI Agent (src/agent.py).
"""

from src.agent import GPowerAgent, CLINICAL_DISCLAIMER


class TestGPowerAgent:
    """Verifies natural language parsing, tool execution, explanations, and disclaimers."""

    def setup_method(self):
        self.agent = GPowerAgent()

    def test_complete_a_priori_query(self):
        query = "İlaç ve plasebo karşılaştırmasında d=0.5, yüzde 80 güç ve 0.05 alfa için iki kuyruklu kaç denek gerekir?"
        response = self.agent.process_query(query)

        # Must report key fields
        assert "64" in response  # N1 and N2
        assert "128" in response  # Total N
        assert "0.801460" in response or "0.80" in response  # Power
        assert "126" in response  # df
        # Must include clinical disclaimer
        assert "FERAGATNAME" in response
        assert "klinik/tıbbi bir tavsiye" in response.lower()

    def test_complete_post_hoc_query(self):
        query = "İki grupta 50'şer hasta var, d=0.5 ve alfa=0.05 altında gerçekleşen güç nedir?"
        response = self.agent.process_query(query)

        assert "50" in response
        assert "100" in response
        assert "98" in response  # df
        assert "69.69" in response or "0.696893" in response
        assert "FERAGATNAME" in response

    def test_missing_parameters_triggers_clarification(self):
        # Query missing effect size d and power
        query = "Yeni bir ilaç çalışması planlıyorum, kaç hasta almalıyım?"
        response = self.agent.process_query(query)

        # Must ask for missing parameters rather than fabricating them
        assert "Etki Büyüklüğü" in response
        assert "Hedef Güç" in response
        assert "tahmin edilmemektedir" in response or "eksik parametreler" in response
        assert "FERAGATNAME" in response

    def test_qualitative_effect_size_mapping(self):
        query = "Orta etki büyüklüğü ile %90 güç ve çift kuyruk için örneklem büyüklüğü nedir?"
        response = self.agent.process_query(query)

        # 'orta etki' must map to d = 0.5
        assert "0.5" in response
        assert "86" in response  # N1 = 86 for power = 0.90, d = 0.5
        assert "172" in response  # Total N = 172
        assert "FERAGATNAME" in response

    def test_explicit_assumptions_reported(self):
        query = "d=0.8 ve %80 güç için örneklem hesabı yap."
        response = self.agent.process_query(query)

        # Defaulted assumptions must be explicitly reported
        assert "Kullanılan Varsayımlar" in response
        assert "0.05" in response  # alpha assumed 0.05
        assert "iki kuyruklu" in response or "çift kuyruk" in response  # tails assumed 2
        assert "26" in response  # N1 = 26 for d = 0.8
        assert "52" in response  # Total N = 52
        assert "FERAGATNAME" in response

    def test_post_hoc_drug_and_placebo_named_groups(self):
        query = "İlaç grubunda 50 hasta, plasebo grubunda 50 hasta var. Etki büyüklüğü 0.5 ve alfa 0.05 ise gücümüz nedir?"
        response = self.agent.process_query(query)

        assert "50" in response
        assert "100" in response
        assert "69.69" in response or "0.696893" in response
        assert "FERAGATNAME" in response

    def test_unknown_query_mode_clarification(self):
        query = "Merhaba, bu çalışma için bana yardımcı olur musun?"
        response = self.agent.process_query(query)

        assert "Hangi analiz türünü gerçekleştirmek istediğinizi tam anlayamadım" in response
        assert "A Priori" in response
        assert "Post Hoc" in response
        assert "FERAGATNAME" in response

