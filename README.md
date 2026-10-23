# G*Power Clone — İstatistiksel Güç Motoru, CLI, MCP, AI Agent ve UI

Bu proje, Heinrich Heine Üniversitesi Düsseldorf tarafından geliştirilen **G*Power 3.1.9.4** yazılımının istatistiksel güç analizi davranışlarının analiz edilmesi, teknik şartnamesinin ([SPEC.md](SPEC.md)) çıkarılması ve **clean-room prensipleriyle** bağımsız olarak uygulanmasını içerir.

> **ÖNEMLİ YASAL UYARI:**  
> Bu yazılım bağımsız bir eğitim ve akademik planlama projesidir. Heinrich Heine University Düsseldorf veya resmî G*Power geliştiricileri ile doğrudan bir bağlantısı veya resmî sponsorluğu yoktur. Orijinal ikili dosyalar veya tescilli kodlar bu depoda barındırılmaz.

---

## 1. Proje Yapısı

```text
Gpower/
├── src/                                # Clean-room hesaplama motoru, CLI, MCP, AI Ajanı ve UI
│   ├── __init__.py
│   ├── calculator.py                  # SciPy tabanlı matematiksel güç motoru (Tek Doğruluk Kaynağı)
│   ├── cli.py                         # gpower-clone komut satırı arayüzü
│   ├── mcp_server.py                  # Model Context Protocol (MCP) sunucusu
│   ├── agent.py                       # Doğal dil AI analiz ajanı (gpower-agent)
│   └── ui.py                          # Tkinter masaüstü grafiksel kullanıcı arayüzü
├── tests/                              # Kapsamlı test takımı (94 doğrulanmış test)
│   ├── __init__.py
│   ├── test_calculator.py             # Hesaplama motoru, sınır durum ve çapraz doğrulama testleri
│   ├── test_cli.py                    # CLI argüman, format ve hata testleri
│   ├── test_mcp_server.py             # MCP araç ve şema testleri
│   ├── test_agent.py                  # AI ajan, PII engelleme ve netleştirme testleri
│   ├── test_integration.py            # 25 public sözleşme vektörü ve canlı stdio MCP testleri
│   ├── test_oracle_validation.py      # Oracle veri seti regresyon testleri
│   └── test_ui.py                     # UI doğrulama, dinamik alanlar, hata mesajları ve grafik testleri
├── oracle/                             # Referans test verileri ve kanıtlar
│   ├── README.md                      # Veri doğrulama raporu
│   ├── MANIFEST.md                    # Vektör detayları ve minimal N tablosu
│   ├── public_vectors.jsonl           # 25 public test vektörü
│   ├── manifest.csv                   # Doğrulama manifesti
│   ├── vectors_a_priori.csv           # A priori test vektörleri
│   ├── vectors_post_hoc.csv           # Post hoc test vektörleri
│   ├── vectors_comparison_500.csv     # 500 karşılaştırma vektörü
│   └── screenshots/                   # Arayüz doğrulama ekran görüntüleri
├── prompts/                            # Clean-room oturum ayrım belgeleri
├── CONTRACT.md                         # Temel doğruluk kaynağı sözleşme dokümanı (v1.0.0)
├── DELIVERY_REPORT.md                  # Güncel teslimat ve doğrulama raporu
├── SPEC.md                             # Teknik şartname
├── LEDGER.md                           # Kanıt ve araştırma defteri
├── HALLUCINATIONS.md                   # Oturumda tespit edilen ve çözülen hatalar
├── requirements.txt                    # Python bağımlılıkları
├── setup.py                            # Paket ve CLI kurulum tanımlayıcısı
├── gpower-ui.bat                       # Windows UI çalıştırma betiği
├── gpower-clone.bat                    # Windows CLI çalıştırma betiği
├── gpower-agent.bat                    # Windows Ajan çalıştırma betiği
├── gpower-mcp.bat                      # Windows MCP Sunucusu başlatma betiği
└── LICENSE                             # MIT Lisansı ve bilimsel atıf
```

---

## 2. Desteklenen Test Aileleri ve Analiz Modları

Uygulama, `src/calculator.py` içindeki ortak hesaplama motoru üzerinden 5 test ailesini ve 5 analiz modunu eksiksiz destekler:

### 2.1. Test Aileleri
1. **`t2-indep`**: İki bağımsız grup ortalama farkı için Student t-testi (eşit varyans).
2. **`t-paired`**: İki bağımlı/eşleştirilmiş grup ortalama farkı için t-testi.
3. **`anova-oneway`**: Tek yönlü varyans analizi (One-way ANOVA, $F$-testi).
4. **`chi2-contingency`**: Kontenjans tablosu Ki-kare ($\chi^2$) testi.
5. **`multireg-r2`**: Çoklu regresyon ($R^2$ artışı, $F$-testi).

### 2.2. Analiz Modları
- **`a-priori`**: Hedef güç, anlamlılık düzeyi ($\alpha$) ve etki büyüklüğü için gereken minimum örneklem büyüklüğü ($N$).
- **`post-hoc`**: Verilen örneklem büyüklüğü, $\alpha$ ve etki büyüklüğü için gerçekleşen istatistiksel güç ($1-\beta$).
- **`sensitivity`**: Belirli örneklem büyüklüğü, $\alpha$ ve güç için tespit edilebilecek minimum etki büyüklüğü.
- **`criterion`**: Sabit örneklem ve hedef güç için gereken anlamlılık düzeyi ($\alpha$).
- **`compromise`**: Belirlenen $\beta/\alpha$ hata oranı doğrultusunda uzlaşık $\alpha$ ve $\beta$ değerleri.

---

## 3. Sistem Gereksinimleri ve Kurulum

- **Python Sürümü:** Python 3.10 veya üzeri (Doğrulanan geliştirme ortamı: Python 3.12.14, Tk 8.6.12)
- **Temel Bağımlılıklar:** `scipy >= 1.14.0`, `numpy >= 2.0.0`, `pytest >= 8.0.0`, `statsmodels >= 0.14.0`, `mcp >= 2.0.0`

### Kurulum Adımları

```bash
# 1. Depo dizininde sanal ortamı oluşturun ve aktif edin
python -m venv .venv
.\.venv\Scripts\activate   # Windows

# 2. Bağımlılıkları kurun
pip install -r requirements.txt

# 3. Paketi geliştirici modunda kurun (CLI komutları için)
pip install -e .
```

> **ÖNEMLİ KURULUM NOTU:**
> Mevcut `.venv` ortamı geliştirme makinesinde harici bir Python yorumlayıcısına bağlı yapılandırılmış olabilir. Sıfırdan temiz bir ortamda paketleme ve bağımsız kurulum testi bu aşamada henüz ayrıca doğrulanmamıştır. Uygulamayı projenin kendi `.venv` yorumlayıcısıyla doğrudan (`.\.venv\Scripts\python`) çalıştırmanız önerilir.

---

## 4. Kullanım ve Arayüzler

Bütün arayüzler (CLI, MCP, Agent ve Masaüstü UI) arka planda **aynı ortak hesaplama motorunu** (`src.calculator.compute_power_analysis`) kullanır.

### 4.1. Masaüstü Kullanıcı Arayüzü (GUI)
Uygulamayı sanal ortam yorumlayıcısıyla başlatın:

```powershell
.\.venv\Scripts\python -m src.ui
# veya Windows kısayol betiği ile:
gpower-ui.bat
```

- **Özellikler:** 5 test ailesi ve 5 analiz modunun tamamı için dinamik girdi alanları, anlık doğrulama, alan adlı Türkçe hata mesajları.
- **Sonuç ve Grafik:** Gerçek motor sonuçlarından üretilen sayısal eksenli dağılım grafiği (H0/H1 yoğunluk eğrileri, kritik eşik çizgileri, $\alpha$ ve $\beta$ gölgelendirmeleri ve etiketleri).
- **Yeniden Boyutlandırma:** Dinamik pencere boyutlandırmasında grafik canvas üzerinde otomatik yeniden ölçeklenir.

### 4.2. Komut Satırı Arayüzü (CLI)
`gpower-clone` veya `python -m src.cli` üzerinden çalışır:

```bash
# Sürüm ve sözleşme bilgisi:
python -m src.cli --version

# Örnek: t2-indep A Priori analizi (JSON çıktısı)
python -m src.cli --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.80 --ratio 1.0

# Örnek: anova-oneway Post Hoc analizi
python -m src.cli --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --groups 5 --n_total 100
```

### 4.3. Model Context Protocol (MCP) Sunucusu
Harici yapay zeka istemcileri (Claude Desktop, Cursor vb.) için stdio tabanlı MCP sunucusu (`src/mcp_server.py`):

```bash
python -m src.mcp_server
# veya:
gpower-mcp.bat
```
- **Sunulan Araç:** `power_analysis` (CLI ile birebir aynı parametre ve JSON çıktısı).

### 4.4. Doğal Dil AI Ajanı (`gpower-agent`)
Kullanıcıların doğal dilde ilettiği istekleri işleyip MCP aracına yönlendirir:

```bash
python -m src.agent --prompt "İki bağımsız grup için d=0.5 etki büyüklüğünde, %80 güç ve 0.05 alfa ile kaç katılımcı gerekir?"
# veya etkileşimli mod:
python -m src.agent --interactive
```

- **Çalışma İlkeleri:** Sayısal parametre uydurmaz, eksik veride kullanıcıdan açıklama ister, kişisel ve klinik verileri reddeder.
- **CANLI LLM AKIŞI SINIRLAMASI:** Canlı LLM çağrısı `GPOWER_LLM_API_KEY` ve `GPOWER_LLM_MODEL` ortam değişkenlerini gerektirir. Gerçek harici API anahtarı tanımlanmadığı için canlı LLM akışı test edilmemiştir; testlerde ajan akışı yerel ve LLM'siz olarak doğrulanmıştır.

---

## 5. Test Takımı ve Doğrulama

Testler `pytest` ile çalıştırılır. Windows geçici klasör izin sorunlarından etkilenmemek ve `.mains` klasöründeki yedeklerin testlere karışmaması için `--basetemp` ve `--ignore` bayrakları kullanılır:

```powershell
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp --ignore=.mains
```

**Doğrulama Sonuçları:**
- **Toplam Test:** **94 passed** (%100 Başarı).
  - **Sözleşme Doğrulaması:** 25 public test vektörünün tamamı tam tamsayı ve $10^{-6}$ ondalık toleransla CLI ve yerel MCP üzerinde doğrulanmıştır.
  - **Test Dağılımı:**
    - `test_calculator.py`: Hesaplama motoru, sınır durumlar, monotonluk ve cross-validation testleri.
    - `test_cli.py`: CLI format, argüman ve hata testleri.
    - `test_mcp_server.py`: MCP şema ve araç testleri.
    - `test_agent.py`: Ajan netleştirme, güvenlik ve PII engelleme testleri.
    - `test_integration.py`: 25 public sözleşme vektörü ve canlı stdio MCP entegrasyonu.
    - `test_oracle_validation.py`: Referans vektör regresyon testleri.
    - `test_ui.py`: UI hesaplama motoru entegrasyonu, alan ayrıştırma, hata mesajları ve grafik koordinat/etiket testleri.
  - **Canlı GUI Testi:** Gerçek Tk penceresinde 25 kombinasyon, hatalı girdi kurtarma ve piksel düzeyinde grafik doğrulaması (`logs/verify/gui_check.py`, 117 kontrol) başarıyla tamamlanmıştır.

---

## 6. Lisans ve Bilimsel Atıf

Bu proje [MIT Lisansı](LICENSE) altında sunulmuştur. Bilimsel referans:
> Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods*, 39, 175-191.
