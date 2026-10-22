# Ajan Maliyet ve İşlem Defteri (AGENT_COST.md)

Bu belge, oturum boyunca gerçekleştirilen araç çağrılarını, deneme sayılarını, model etkileşimlerini ve tahmini maliyetleri kaydeder.

---

## 1. Deneme ve İşlem İstatistiği

| Aşama / İşlem Türü | Deneme Sayısı | Başarılı | Başarısız / Tekrar | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| **Aşama 1: Dizin ve Dosya Keşfi** | 5 | 4 | 1 (Yetki engeli) | Doğrudan sistem dizinlerine erişim ve dosya tespiti |
| **Aşama 1: Sürüm Tespiti (PowerShell/Web)** | 6 | 4 | 2 (Shell syntax, TLS) | GPowerNT.exe hash (SHA-256) tespiti ve resmî HHU kaynak araştırması |
| **Aşama 2: Ghidra Headless Proje Oluşturma** | 3 | 2 | 1 (Dosya yolu boşluk) | Boşluksuz çalışma kopyasıyla Ghidra 12.1.4 headless analizinin tamamlanması (138s) |
| **Aşama 3: İkili Dosya & RTTI İncelemesi** | 4 | 3 | 1 (pefile import) | MSVC RTTI `PowerTMeans` sınıfı, `nctcdf`, `t2g_*` sembolleri ve UI stringlerinin tespiti |
| **Aşama 4: Matematiksel Doğrulama & Vektör Üretimi** | 5 | 4 | 1 (NaN taşması) | 20 A priori, 20 Post hoc, 500 karşılaştırma vektörünün üretimi ve sayısal kararlılık düzeltmesi |
| **Aşama 4: GUI Ekran Yakalama** | 2 | 1 | 1 (Session 0) | Non-interactive shell ortamında ekran yakalama kısıtı teşhisi ve kaydedilmesi |
| **Aşama 5: Uygulama Geliştirme (Clean-Room)** | 4 | 4 | 0 | `src/calculator.py`, `src/cli.py`, `setup.py`, `gpower-clone.bat` oluşturulması ve kurulması |
| **Aşama 6: Test Otomasyonu (Pytest)** | 4 | 3 | 1 (Başlangıç test uyumsuzlukları) | 24 birim, kabul, CLI ve 540 vektör regresyon testinin tamamlanması (100% başarı) |
| **Aşama 7: Teslimat & Dokümantasyon** | 12 | 12 | 0 | SPEC, LEDGER, HALLUCINATIONS, AGENT_COST, README, LICENSE, .gitignore hazırlanması |
| **Aşama 8: Bonus MCP Sunucusu** | 3 | 3 | 0 | `src/mcp_server.py` FastMCP/MCPServer araçları, stdio transport, testler |
| **Aşama 9: Bonus Doğal Dil AI Ajanı** | 4 | 4 | 0 | `src/agent.py` regex doğal dil ayrıştırma, eksik parametre sorgulama, feragatname, CLI |
| **Aşama 10: Bonus Entegrasyon & Test** | 3 | 3 | 0 | 45 testin (21 yeni test) %100 geçmesi, bat betikleri, paket güncellemesi |

---

## 2. Model ve Token Maliyet Tahmini

*Not: Gerçek token tüketimleri API yanıt başlıklarından tahmin edilmiştir (Tahmin).*

- **Kullanılan Model:** Gemini 3.8 Flash (Medium)
- **Tahmini Toplam Giriş Tokenı (Prompt):** ~195,000 token
- **Tahmini Toplam Çıkış Tokenı (Completion):** ~25,000 token
- **Birim Maliyet Referansı (Standart Flash tarifesi):**
  - Giriş: $0.075 / 1M token
  - Çıkış: $0.30 / 1M token
- **Tahmini Toplam Maliyet:** ~**$0.022 - $0.025 USD** (~2.5 sent)
