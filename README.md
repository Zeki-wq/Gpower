# G*Power Clone — İki Bağımsız Grup t-Testi İstatistiksel Güç Motoru ve CLI

Bu proje, Heinrich Heine Üniversitesi Düsseldorf tarafından geliştirilen **G*Power 3.1.9.4** yazılımının "İki bağımsız grubun ortalamaları için t-testi (ilaç ve plasebo)" davranışlarının analiz edilmesi, teknik şartnamesinin ([SPEC.md](SPEC.md)) çıkarılması ve **clean-room prensipleriyle** sıfırdan bağımsız olarak yeniden uygulanmasını içerir.

> **ÖNEMLİ YASAL UYARI:**  
> Bu yazılım bağımsız bir eğitim/ödev projesidir. Heinrich Heine University Düsseldorf veya resmî G*Power geliştiricileri ile doğrudan bir bağlantısı veya resmî sponsorluğu yoktur. Orijinal ikili dosyalar veya tescilli kodlar bu depoda barındırılmaz.

---

## 1. Proje Yapısı

```text
Gpower/
├── src/                                # Clean-room hesaplama motoru, CLI, MCP ve AI Ajanı
│   ├── __init__.py
│   ├── calculator.py                  # SciPy tabanlı matematiksel t-test motoru (Tek Doğruluk Kaynağı)
│   ├── cli.py                         # gpower-clone komut satırı arayüzü
│   ├── mcp_server.py                  # Model Context Protocol (MCP) sunucusu
│   └── agent.py                       # Doğal dil AI analiz ajanı (gpower-agent)
├── tests/                              # Kapsamlı test takımı (47 test, 540 vektör)
│   ├── __init__.py
│   ├── test_calculator.py             # Birim, sınır ve monotonluk testleri
│   ├── test_cli.py                    # CLI argüman ve JSON hata testleri
│   ├── test_mcp_server.py             # MCP araç ve doğrulama testleri
│   ├── test_agent.py                  # Doğal dil ajanı, netleştirme ve feragatname testleri
│   └── test_oracle_validation.py      # Oracle veri seti regresyon testleri
├── oracle/                             # Referans test verileri
│   ├── README.md                      # Veri doğrulama raporu
│   ├── MANIFEST.md                    # 40 vektörün detaylı karşılaştırma ve minimal N tablosu
│   ├── manifest.csv                   # Makine tarafından okunabilir doğrulama manifesti
│   ├── vectors_a_priori.csv           # 20 adet A priori test vektörü
│   ├── vectors_post_hoc.csv           # 20 adet Post hoc test vektörü
│   ├── vectors_comparison_500.csv     # 500 adet karşılaştırma vektörü
│   └── screenshots/                   # Arayüz ekran görüntüleri kılavuzu
├── prompts/                            # Clean-room oturum ayrım belgeleri
│   ├── inspection_session.md          # Analiz oturumu istemi
│   └── implementation_session.md      # Yalnızca SPEC girdili uygulama istemi
├── SPEC.md                             # Gherkin formatında teknik şartname
├── LEDGER.md                           # [REA], [DOK], [AJAN] kanıt defteri
├── HALLUCINATIONS.md                   # Oturumda yaşanan gerçek hatalar ve çözümler
├── AGENT_COST.md                       # Deneme sayıları, token ve maliyet analizi
├── requirements.txt                    # Python bağımlılıkları (mcp, scipy, statsmodels vb.)
├── setup.py                            # Paket ve CLI kurulum tanımlayıcısı (gpower-clone, gpower-agent, gpower-mcp)
├── gpower-clone.bat                    # Windows CLI çalıştırma betiği
├── gpower-agent.bat                    # Windows Doğal Dil Ajanı çalıştırma betiği
├── gpower-mcp.bat                      # Windows MCP Sunucusu başlatma betiği
├── LICENSE                             # MIT Lisansı ve bilimsel atıf
└── README.md                           # Kapsamlı proje ve kullanım dokümantasyonu
```

---

## 2. Clean-Room Metodolojisi

Bu proje, telif haklarına ve tersine mühendislik etik kurallarına tam uyum sağlamak amacıyla **Clean-Room (Temiz Oda)** yaklaşımıyla yürütülmüştür:

1. **İnceleme Ajanı (Inspection Phase):** Ghidra 12.1.4 ile G*Power 3.1.9.4 ikili dosyasını statik olarak analiz etmiş, RTTI sınıf yapısını (`PowerTMeans`) ve sembolleri tespit ederek tüm bulguları [LEDGER.md](LEDGER.md) ve davranış şartnamesini [SPEC.md](SPEC.md) belgesine kaydetmiştir.
2. **Uygulama Ajanı (Implementation Phase):** Uygulama geliştirme aşamasında Ghidra çıktıları, dekompilasyon kodları veya analiz konuşma geçmişi kesinlikle kullanılmamıştır. Uygulayıcı yalnızca [SPEC.md](SPEC.md) ve [prompts/implementation_session.md](prompts/implementation_session.md) girdilerini kullanarak bağımsız Python kodunu yazmıştır.

---

## 3. Sistem Gereksinimleri ve Kurulum

- **Python Sürümü:** Python 3.10 veya üzeri (Geliştirme ortamı: Python 3.12.6, Windows 11)
- **Temel Bağımlılıklar:** `scipy >= 1.14.0`, `numpy >= 2.0.0`, `pytest >= 8.0.0`

### Kurulum Adımları

```bash
# 1. Depoyu klonlayın veya çalışma dizinine gidin
git clone https://github.com/Zeki-wq/Gpower.git
cd Gpower

# 2. Bağımlılıkları kurun
python -m pip install -r requirements.txt

# 3. gpower-clone CLI aracını sisteme kurun
python -m pip install -e .
```

---

## 4. Kullanım ve Komut Satırı Arayüzü (CLI)

`gpower-clone` aracı hem doğrudan CLI komutu olarak hem de Python modülü (`python -m src.cli`) olarak çalıştırılabilir.

### 4.1. A Priori Analiz (Gereken Örneklem Büyüklüğü)

Hedef güç, anlamlılık düzeyi $\alpha$, etki büyüklüğü $d$ ve grup oranı $N_2/N_1$ verildiğinde gereken minimum tamsayı örneklemini hesaplar:

```bash
gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.80 --ratio 1.0
```

**Doğrulanmış JSON Çıktısı:**
```json
{
  "status": "success",
  "test": "t2-indep",
  "mode": "a-priori",
  "tails": 2,
  "d": 0.5,
  "alpha": 0.05,
  "target_power": 0.8,
  "ratio": 1.0,
  "n1": 64,
  "n2": 64,
  "total_n": 128,
  "df": 126,
  "delta": 2.828427,
  "critical_t": 1.978971,
  "actual_power": 0.80146
}
```

### 4.2. Post Hoc Analiz (Gerçekleşen İstatistiksel Güç)

Belirli örneklem büyüklükleri ($N_1, N_2$), $\alpha$ ve etki büyüklüğü $d$ verildiğinde gerçekleşen istatistiksel gücü hesaplar:

```bash
gpower-clone --test t2-indep --mode post-hoc --tails 2 --d 0.5 --alpha 0.05 --n1 50 --n2 50
```

**Doğrulanmış JSON Çıktısı:**
```json
{
  "status": "success",
  "test": "t2-indep",
  "mode": "post-hoc",
  "tails": 2,
  "d": 0.5,
  "alpha": 0.05,
  "n1": 50,
  "n2": 50,
  "total_n": 100,
  "df": 98,
  "delta": 2.5,
  "critical_t": 1.984467,
  "actual_power": 0.696893
}
```

### 4.3. Metin (Human-Readable) Formatı

```bash
gpower-clone --mode post-hoc --tails 2 --d 0.5 --alpha 0.05 --n1 50 --n2 50 --format text
```

---

## 5. Desteklenen ve Desteklenmeyen Modlar

- **Desteklenen Test:** `t2-indep` (İki bağımsız grup ortalama farkı için Student t-testi, eşit varyans varsayımı).
- **Desteklenen Analiz Türleri:** `a-priori` (minimum tamsayı örneklem arama) ve `post-hoc` (gerçekleşen güç).
- **Kuyruk Seçenekleri:** Tek kuyruklu (`--tails 1`) ve çift kuyruklu (`--tails 2`).
- **Açıkça Desteklenmeyen Modlar:** Eşleştirilmiş grup t-testi (paired means), Welch t-testi (unequal variances), tek grup t-testi, ANOVA/MANOVA, Ki-kare testleri ve regresyon analizleri bu ödev kapsamı dışındadır ve sahte başarı iddiasında bulunulmadan açıkça hariç tutulmuştur.

---

## 6. Model Context Protocol (MCP) Sunucusu (Bonus Aşama)

Bu proje, Anthropic Model Context Protocol (MCP) standardına uygun bir araç sunucusu (`src/mcp_server.py`) barındırır. MCP sunucusu, harici yapay zeka istemcilerinin (Claude Desktop, Cursor, Continue vb.) G*Power hesaplama yeteneklerini doğrudan araç (tool call) olarak çağırmasını sağlar.

### 6.1. Tek Doğruluk Kaynağı (Single Source of Truth)
MCP sunucusu ikinci bir hesaplama motoru oluşturmaz. CLI ile birebir aynı fonksiyonları (`src/calculator.py` içindeki `compute_a_priori` ve `compute_post_hoc`) çağırır. Böylece matematiksel tutarlılık ve doğruluk garanti altına alınmıştır.

### 6.2. Sunulan MCP Araçları (Tools)

1. **`compute_a_priori_sample_size`**:
   - İki bağımsız grup t-testi için hedef gücü sağlayan minimum tamsayı örneklem büyüklüğünü ($N_1, N_2, \text{Total } N$) hesaplar.
   - **Girdiler:**
     - `d` (float): Cohen's d etki büyüklüğü ($d > 0$)
     - `alpha` (float): Anlamlılık düzeyi ($0 < \alpha < 1$, varsayılan: `0.05`)
     - `target_power` (float): Hedef istatistiksel güç ($0 < 1-\beta < 1$, varsayılan: `0.80`)
     - `ratio` (float): Grup oranı $N_2 / N_1$ ($\text{ratio} > 0$, varsayılan: `1.0`)
     - `tails` (int): Kuyruk sayısı (`1` veya `2`, varsayılan: `2`)
   - **Çıktı (JSON):** `status`, `n1`, `n2`, `total_n`, `actual_power`, `critical_t`, `delta`, `df`.

2. **`compute_post_hoc_power`**:
   - Belirlenmiş örneklem büyüklükleri için gerçekleşen istatistiksel gücü ($1-\beta$) hesaplar.
   - **Girdiler:**
     - `d` (float): Cohen's d etki büyüklüğü ($d > 0$)
     - `alpha` (float): Anlamlılık düzeyi ($0 < \alpha < 1$, varsayılan: `0.05`)
     - `n1` (int): 1. Grup örneklem büyüklüğü ($N_1 \ge 2$)
     - `n2` (int): 2. Grup örneklem büyüklüğü ($N_2 \ge 2$)
     - `tails` (int): Kuyruk sayısı (`1` veya `2`, varsayılan: `2`)
   - **Çıktı (JSON):** `status`, `actual_power`, `critical_t`, `delta`, `df`, `n1`, `n2`, `total_n`.

### 6.3. Parametre Doğrulama ve Hata Yönetimi
Tüm parametreler tür ve aralık açısından `src/calculator.py` doğrulamalarından geçirilir. Hatalı girdilerde (örn. $d \le 0$, $\alpha \ge 1.0$, $N_1 < 2$) sunucu çökmez; açıklayıcı `ValidationError` JSON yanıtı döndürür:
```json
{
  "status": "error",
  "error_type": "ValidationError",
  "message": "Effect size d must be positive (got -0.5)"
}
```

### 6.4. MCP Sunucusunu Başlatma

```bash
# Standart stdio üzerinden MCP sunucusunu çalıştırma
python -m src.mcp_server

# veya Windows kısayol betiği ile:
gpower-mcp.bat
```

### 6.5. Claude Desktop / Cursor / VSCode Konfigürasyonu
MCP sunucusunu LLM istemcilerine bağlamak için istemcinin `claude_desktop_config.json` veya benzeri yapılandırma dosyasına şu bloğu ekleyebilirsiniz:

```json
{
  "mcpServers": {
    "gpower-clone": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:\\Users\\Zeki\\OneDrive\\Masaüstü\\Test\\Gpower"
    }
  }
}
```

---

## 7. Doğal Dil AI Ajanı (`gpower-agent`) (Bonus Aşama)

Doğal dil AI ajanı (`src/agent.py`), araştırmacıların veya kullanıcıların serbest dilde (Türkçe veya İngilizce) ifade ettiği güç analizi isteklerini anlar, analiz türünü ve parametreleri çıkarır, arka planda MCP/hesaplama araçlarını çalıştırır ve sonuçları detaylı bir şekilde yorumlar.

### 7.1. Davranış İlkeleri ve Güvenilirlik
- **Parametre Uydurmaz:** Eksik parametre olduğunda (özelikle A priori analizi için etki büyüklüğü verilmediğinde) tahminde bulunmaz veya varsayım uydurmaz; kullanıcıdan netleştirme ister.
- **Varsayımları Açıkça Belirtir:** Varsayılan değerler kullanıldığında (örneğin kuyruk sayısı belirtilmediğinde "Çift kuyruklu (tails=2)", oran belirtilmediğinde "Eşit grup oranı (ratio=1.0)") bunu yanıtta açıkça raporlar.
- **Nitel İfadeleri Eşler:** "orta etki" ($d=0.5$), "küçük etki" ($d=0.2$), "büyük etki" ($d=0.8$) gibi bilimsel standart Cohen eşiklerini otomatik tanır.
- **Eksiksiz Metrik Açıklaması:** Sonuçla birlikte $N_1$, $N_2$, toplam $N$, $\alpha$, hedef/gerçek güç, etki büyüklüğü, serbestlik derecesi ($df$), kritik $t$, kuyruk seçimi ve grup oranını maddeler halinde açıklar.
- **Zorunlu Klinik ve Tıbbi Feragatname:** Hesaplama sonuçları hiçbir zaman klinik tavsiye, tedavi garantisi veya tıbbi yönlendirme olarak sunulmaz. Her yanıtın sonuna yasal feragatname eklenir.

### 7.2. Kullanım ve Komutlar

#### Tekli İstem (Single-Shot Prompt):
```bash
# A Priori Analizi
gpower-agent --prompt "İki bağımsız grup için orta etki büyüklüğünde, %80 güç ve 0.05 alfa ile kaç hasta gerekir?"

# Post Hoc Analizi
gpower-agent --prompt "İlaç grubunda 50, plasebo grubunda 50 kişi var. Etki büyüklüğü 0.5 ve alfa 0.05 ise elde edilen güç nedir?"
```

#### Etkileşimli Sohbet Modu (Interactive REPL):
```bash
gpower-agent --interactive
# veya Windows kısayol betiği ile:
gpower-agent.bat
```

#### Örnek Ajan Yanıtı:
```text
Soru: İki bağımsız grup için orta etki büyüklüğünde, %80 güç ve 0.05 alfa ile kaç hasta gerekir?

Çözümleme & Sonuç:
A priori örneklem analizi gerçekleştirildi.

Kullanılan Varsayımlar:
  * Kuyruk sayısı: Çift kuyruklu (tails = 2)
  * Grup oranı (N2/N1): Eşit gruplar (ratio = 1.0)
  * Nitel etki büyüklüğü 'orta' -> d = 0.50 olarak kabul edildi

Hesaplama Sonuçları:
  * 1. Grup Örneklem Büyüklüğü (N1): 64
  * 2. Grup Örneklem Büyüklüğü (N2): 64
  * Toplam Örneklem Büyüklüğü (N): 128
  * Hedef Güç (1 - beta): 0.8000
  * Gerçekleşen Güç (Actual Power): 0.8015 (%80.15)
  * Anlamlılık Düzeyi (alpha): 0.0500
  * Etki Büyüklüğü (Cohen's d): 0.5000
  * Serbestlik Derecesi (df): 126
  * Kritik t Değeri: 1.9790
  * Noncentrality Parametresi (delta): 2.8284

YORUM: Her iki gruba en az 64'er hasta (toplam 128 hasta) dahil edildiğinde, %80 hedef güce (%80.15) ulaşılmaktadır.

[ÖNEMLİ YASAL VE KLİNİK FERAGATNAME]
Bu hesaplama motoru ve yapay zeka ajanı tarafından üretilen istatistiksel güç ve örneklem analizi sonuçları yalnızca metodolojik, akademik ve istatistiksel planlama amaçlıdır.
Elde edilen sonuçlar hiçbir koşulda tıbbi tavsiye, klinik teşhis, tedavi rehberi veya hasta güvenliği garantisi niteliği taşımaz.
Klinik araştırmalarda nihai örneklem ve protokol kararları etik kurul onayları, araştırmacı hekimler ve yetkili biyoistatistik uzmanlarının değerlendirmesine tabidir.
```

---

## 8. Test Takımı ve Doğrulama Sonuçları

Testler `pytest` ile çalıştırılır:

```bash
python -m pytest -v
```

**Test Sonuçları:**
- **Toplam Test:** 47/47 BAŞARILI (%100 Başarım Oranı).
  - **Hesaplama Motoru & Sınırlar (`test_calculator.py`):** 25 test (Uç durumlar, $\delta \ge 10$ asimptotiği, monotonluk, statsmodels çapraz doğrulaması).
  - **Komut Satırı Arayüzü (`test_cli.py`):** 5 test (A priori, Post hoc, metin/JSON formatları, hata durumları).
  - **Model Context Protocol Sunucusu (`test_mcp_server.py`):** 6 test (Araç çağrıları, dönüş şemaları, `ValidationError` yakalama).
  - **Doğal Dil AI Ajanı (`test_agent.py`):** 7 test (Doğal dil regex ayrıştırma, eksik parametre sorgulama, Cohen etki haritalama, klinik feragatname garantisi).
  - **Oracle Regresyon Testleri (`test_oracle_validation.py`):** 4 test (540 referans vektör doğrulaması).
- **Doğrulanan Vektörler:**
  - 20 A Priori Vektörü ([oracle/vectors_a_priori.csv](oracle/vectors_a_priori.csv))
  - 20 Post Hoc Vektörü ([oracle/vectors_post_hoc.csv](oracle/vectors_post_hoc.csv))
  - 500 Karşılaştırma ve Dayanıklılık Vektörü ([oracle/vectors_comparison_500.csv](oracle/vectors_comparison_500.csv))
- **Hassasiyet Toleransları:** Serbestlik derecesi ve örneklem sayıları tam tamsayı eşleşmesi ($df=N_1+N_2-2$); kritik $t$, $\delta$ ve güç için $\pm 10^{-4}$ tolerans.

---

## 9. Lisans ve Bilimsel Atıf

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Bilimsel referans:
> Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods*, 39, 175-191.

