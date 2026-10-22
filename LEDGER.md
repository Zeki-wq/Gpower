# G*Power Analiz Kanıt Defteri (LEDGER.md)

Bu belge, G*Power ortam incelemesi, statik analiz ve davranış analizinden elde edilen tüm bulguları titizlikle kaydeder.
Her girdi aşağıdaki etiketlerle sınıflandırılmıştır:
- `[REA]`: Gerçek ortamda doğrudan gözlemlenmiş, doğrulanmış teknik kanıt (Real Evidence).
- `[DOK]`: Resmî belgelere, akademik makalelere veya doğrulanmış kaynak dokümanlarına dayanan bilgi (Documentation).
- `[AJAN]`: Ajan tarafından mantıksal olarak çıkarılmış ancak ikili dosya veya kanıtla henüz kesinleştirilmemiş hipotez/tahmin (Agent Hypothesis).

---

## 1. Ortam ve İkili Dosya Doğrulaması

### 1.1. Ghidra Headless Aracı
- **Durum:** `[REA]`
- **Dizin:** `C:\Users\Zeki\Downloads\Compressed\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC`
- **Headless Betiği:** `C:\Users\Zeki\Downloads\Compressed\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat`
- **Doğrulama Sonucu:** Dosya sisteminde mevcut olduğu doğrulandı.

### 1.2. Referans G*Power Yürütülebilir Dosyası (3.1.9.4)
- **Durum:** `[REA]`
- **Orijinal Konum:** `C:\Program Files (x86)\GPower 3.1\GPowerNT.exe`
- **Ghidra Çalışma Kopyası:** `C:\Users\Zeki\Documents\GPowerReverseEngineering\GPowerNT.exe`
- **Dosya Boyutu:** `2,060,800` bayt (2.06 MB)
- **Dosya Sürümü (FileVersion):** `3.1.9.4`
- **Ürün Sürümü (ProductVersion):** `3.1.9.4`
- **SHA-256 Özeti:** `72C713DE054206BD17DD3BC69565C8E0BDB688D6DF0AB9A7E65F97C471565FE5` (Her iki kopyanın hash değerleri birebir eşleşti).

---

## 2. Ghidra Statik Analizi ve Otomasyon Kanıtları

### 2.1. Ghidra Projesi Oluşturma
- **Durum:** `[REA]`
- **Proje Konumu:** `C:\Users\Zeki\Documents\GPowerReverseEngineering\GPower3_Project.gpr`
- **Veritabanı:** `C:\Users\Zeki\Documents\GPowerReverseEngineering\GPower3_Project.rep`
- **Analiz Süresi:** 138 saniye
- **Başarı Raporu:** `REPORT: Analysis succeeded for file: GPowerNT.exe`
- **Kullanılan Analyzerlar:** Decompiler Switch Analysis (80.2s), Windows x86 PE RTTI Analyzer (7.1s), Windows Resource Reference (4.9s), Disassemble (4.0s).

### 2.2. RTTI (Run-Time Type Information) Sınıf Hiyerarşisi
- **Durum:** `[REA]`
- İkili dosyanın `.data` ve `.rdata` bölümlerindeki MSVC RTTI sembollerinde t-testi sınıf hiyerarşisi tam olarak tespit edildi:
  - Temel Sınıf: `.?AVPowerAnalysis@@`
  - Aile Sınıfı: `.?AVPowerT@@`
  - **Uygulanan Test Sınıfı:** `.?AVPowerTMeans@@` (İki bağımsız grup t-testi ortalama farkı)
  - İlgili Diğer Sınıflar: `.?AVPowerTOneMean@@` (Tek grup), `.?AVPowerTPairedMean@@` (Eşleştirilmiş gruplar), `.?AVPowerTWilcox2@@` (Non-parametrik Wilcoxon iki grup).
- TypeDescriptor Başlangıç Dosya Ofseti: `0x1D210C`
- TypeDescriptor İsmi (`.?AVPowerTMeans@@`): `0x1D2114`

### 2.3. İkili Dosya İçindeki Dağılım Fonksiyonları
- **Durum:** `[REA]`
- İkili dosyanın sembolik ve string havuzunda non-central ve standart olasılık dağılım rutinleri bulundu:
  - `nctcdf`: Noncentral Student t Cumulative Distribution Function
  - `nctinv`: Noncentral Student t Inverse / Quantile Function
  - `nctpdf`: Noncentral Student t Probability Density Function
  - `normcdf`, `norminv`, `normpdf`: Standart normal dağılım fonksiyonları.
  - `t2g_equalN`, `t2g_mean1`, `t2g_mean2`, `t2g_sd`: İki grup t-testine ait girdi ve ara değişken sembolleri.

### 2.4. Arayüz ve UI Metin Eşleşmeleri
- **Durum:** `[REA]`
- Test Tanımı: `"Means: Difference between two independent means (two groups)"`
- Test Ailesi: `"t tests"`
- Giriş Parametreleri:
  - `"Allocation ratio N2/N1"` (Dosya ofseti: `0x18C77C`)
  - `"Power (1-$\beta$ err prob)"`
  - `"$\alpha$ err prob"`
  - `"Tail(s)"`
- Çıktı Parametreleri:
  - `"Noncentrality parameter $\delta$"`
  - `"Critical t"`
  - `"Actual power"`
  - `"Total sample size"`

---

## 3. Matematiksel Formülasyon ve Algoritma Doğrulaması

> **Metodolojik Not:** Aşağıdaki formüller genel istatistik literatüründen (`[DOK]`) alınmış olup, tek başına tersine mühendislik keşfi olarak iddia edilmemiştir. İkili dosya içindeki `nctcdf`, `nctinv`, `t2g_*` sembolleri ve `PowerTMeans` RTTI yapısı ise Ghidra statik analiziyle doğrulanmış gerçek bulgulardır (`[REA]`).

### 3.1. Literatür Formülleri ([DOK])
- **Serbestlik Derecesi ($df$):** `[DOK]` (Student, 1908)
  $$df = N_1 + N_2 - 2$$
- **Noncentrality Parameter ($\delta$):** `[DOK]` (Cohen 1988; Faul et al. 2007)
  $$\delta = d \cdot \sqrt{\frac{N_1 \cdot N_2}{N_1 + N_2}}$$
  Eşit gruplarda ($N_1 = N_2 = N/2$): $\delta = \frac{d}{2} \sqrt{N}$
- **Kritik t Değeri ($t_{crit}$):** `[DOK]`
  - Çift kuyruklu: $t_{crit} = t_{df}^{-1}(1 - \alpha/2)$
  - Tek kuyruklu: $t_{crit} = t_{df}^{-1}(1 - \alpha)$
- **Gerçekleşen Güç ($1 - \beta$):** `[DOK]`
  - Çift kuyruklu: $1 - \beta = 1 - F_{df, \delta}(t_{crit}) + F_{df, \delta}(-t_{crit})$
  - Tek kuyruklu: $1 - \beta = 1 - F_{df, \delta}(t_{crit})$

### 3.2. A Priori Örneklem Arama Algoritması ve Tamsayı Kuralı
- **Durum:** `[DOK]` & `[REA]`
- G*Power, verilen $d, \alpha, \text{hedef güç}, r = N_2/N_1$ değerleri için $N_2 = \lceil r \cdot N_1 \rceil$ kuralını uygular.
- Gerçekleşen gücün hedef gücü sağladığı ($\text{power} \ge \text{target\_power}$) en küçük geçerli tamsayı $N_1$ aranır.
- Doğrulama: Standart ders kitabı senaryosunda ($d=0.5, \alpha=0.05, 1-\beta=0.80, r=1.0$, çift kuyruk):
  - $N_1 = 64, N_2 = 64, \text{Total } N = 128$
  - $df = 126$
  - $\delta = 2.828427$
  - $t_{crit} = 1.978971$
  - Gerçekleşen Güç $= 0.801460$ (Hedef %80'in hemen üzerinde).

---

## 4. Oracle Veri Seti ve Bağımsız Referans Ayrımı

540 vektörün tamamı bilimsel dürüstlük ilkesi gereğince iki ayrı kategoriye ayrılmıştır:

### 4.1. Bağımsız Referans ve Standart Kütüphanelerle Doğrulanan Vektörler (40 Adet)
- **Kapsam:** `oracle/vectors_a_priori.csv` (20 adet) ve `oracle/vectors_post_hoc.csv` (20 adet).
- **Bağımsız Referans Kaynakları:**
  1. Cohen (1988) standart etki büyüklüğü tabloları ($d=0.2, 0.5, 0.8$, $\alpha=0.05, 0.01$).
  2. Faul et al. (2007) G*Power 3 referans makalesi (Behavior Research Methods, 39, 175-191).
  3. Bağımsız Python kütüphanesi `statsmodels.stats.power.TTestIndPower` ile çift yönlü çapraz doğrulama (güç farkı $< 10^{-6}$, tavan örneklem sayısı eşleşmesi %100).
- **Örneklem Büyüklüğü Tam Eşleşme Oranı:** 40 / 40 (%100.0).

### 4.2. Uygulama İçi Sentetik ve Dayanıklılık Vektörleri (500 Adet)
- **Kapsam:** `oracle/vectors_comparison_500.csv` (500 adet).
- **Amaç:** Rastgele oluşturulmuş geniş parametre uzayında ($d \in [0.15, 1.2]$, $\alpha \in [0.001, 0.1]$, $N \in [20, 500]$) sayısal taşma, asimptotik stabilite ve regresyon kontrolü.
- **Dürüst Ayrım:** Bu 500 vektör dış bir yazılımın bağımsız oracle kanıtı olarak değil, klon motorunun uç durumlardaki davranışını denetleyen **uygulama içi sentetik test kümesi** olarak belgelenmiştir.

---

## 5. Aşırı Noncentrality Parametresi ($\delta > 10$) Asimptotik Analizi

- **Durum:** `[DOK]` & `[REA]`
- **Matematiksel Davranış:** $T \sim \text{nct}(df, \delta)$ noncentral t dağılımında $\delta \to \infty$ iken dağılım normale yaklaşır:
  $$T \approx \mathcal{N}\left(\delta, 1 + \frac{\delta^2}{2 \cdot df}\right)$$
  $\delta \ge 10.0$ ve tipik kritik değerler ($t_{crit} \le 3.5$) için kritik değer ortalamanın $5$ ila $10$ standart sapma solunda kalır.
- **Sayısal Sorun:** SciPy ve statsmodels gibi kütüphanelerde `nct.cdf(-critical_t, df, delta)` çağrıldığında hipergeometrik seri terimlerinin alt taşması (underflow) nedeniyle `NaN` üretilebilmektedir (Örn: `statsmodels` $\delta=10.0$ için `NaN` döndürmektedir).
- **Geçerlilik Aralığı:** $\delta \ge 10.0$ ve $t_{crit} < \delta - 4\sigma$ koşulu altında sol kuyruk olasılığı $P(T \le -t_{crit}) < 10^{-15}$ mertebesinde olup ihmal edilebilir ($0.0$).
- **Uygulanan Çözüm:** `src/calculator.py` içinde alt taşma durumunda `math.isnan(cdf_lower)` değeri $0.0$ olarak sınırlandırılmış ve gerçekleşen güç $1.000000$ olarak tam sayısal kararlılıkla elde edilmiştir. Bağımsız `statsmodels` ile $\delta=12.5, 15.0, 20.0$ durumlarında $1.00000000$ çıktısı birebir doğrulanmıştır.

---

## 6. Bonus Aşama: Model Context Protocol (MCP) ve Doğal Dil AI Ajanı

### 6.1. Tek Doğruluk Kaynağı Prensibi (Single Source of Truth)
- **Durum:** `[REA]`
- MCP sunucusu (`src/mcp_server.py`) ve Doğal Dil AI Ajanı (`src/agent.py`), bağımsız veya mükerrer bir hesaplama motoru içermez. Tüm matematiksel hesaplamalar ve giriş doğrulamaları `src/calculator.py` üzerinden yürütülür (`compute_a_priori`, `compute_post_hoc`).

### 6.2. MCP Sunucusu ve Araçları
- **Durum:** `[REA]`
- `mcp.server.mcpserver.MCPServer` protokolü ile iki araç sunulmaktadır:
  1. `compute_a_priori_sample_size`: `d`, `alpha`, `target_power`, `ratio`, `tails` parametrelerini alır; `n1`, `n2`, `total_n`, `actual_power`, `critical_t`, `delta`, `df` döndürür.
  2. `compute_post_hoc_power`: `d`, `alpha`, `n1`, `n2`, `tails` parametrelerini alır; `actual_power`, `critical_t`, `delta`, `df`, `total_n` döndürür.
- Geçersiz parametrelerde (örn. $d \le 0$, $\alpha \ge 1.0$) `ValidationError` fırlatılır ve istemciye anlaşılır hata mesajı iletilir.

### 6.3. Doğal Dil AI Ajanı ve Klinik Feragatname
- **Durum:** `[REA]`
- Ajan, Türkçe/İngilizce serbest metin girdilerinden etki büyüklüğü ($d$), hedef güç, anlamlılık düzeyi ($\alpha$), örneklem sayıları ($N_1, N_2$), oran ve kuyruk seçimini regex ve semantik kurallarla çıkarır.
- Eksik parametreler (örn. A priori için $d$) tespit edildiğinde asla uydurma yapılmaz; kullanıcıya açıklayıcı bir netleştirme sorusu yöneltilir.
- Kullanılan varsayımlar (örn. "Çift kuyruklu (tails=2)", "Eşit grup oranı (ratio=1.0)") yanıtta açıkça raporlanır.
- **Klinik Feragatname Politikası:** Ajanın ürettiği hiçbir çıktı klinik/tıbbi tavsiye veya garanti olarak sunulamaz. Her yanıtın sonuna zorunlu yasal/klinik feragatname (`CLINICAL_DISCLAIMER`) eklenir.

