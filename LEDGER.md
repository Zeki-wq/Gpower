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

### 3.1. Formüller
- **Serbestlik Derecesi ($df$):** `[DOK]`
  $$df = N_1 + N_2 - 2$$
- **Noncentrality Parameter ($\delta$):** `[DOK]` & `[REA]`
  $$\delta = d \cdot \sqrt{\frac{N_1 \cdot N_2}{N_1 + N_2}}$$
  Eşit gruplarda ($N_1 = N_2 = N/2$): $\delta = \frac{d}{2} \sqrt{N}$
- **Kritik t Değeri ($t_{crit}$):** `[DOK]` & `[REA]`
  - Çift kuyruklu: $t_{crit} = t_{df}^{-1}(1 - \alpha/2)$
  - Tek kuyruklu: $t_{crit} = t_{df}^{-1}(1 - \alpha)$
- **Gerçekleşen Güç ($1 - \beta$):** `[DOK]` & `[REA]`
  - Çift kuyruklu: $1 - \beta = 1 - F_{df, \delta}(t_{crit}) + F_{df, \delta}(-t_{crit})$
  - Tek kuyruklu: $1 - \beta = 1 - F_{df, \delta}(t_{crit})$

### 3.2. A Priori Örneklem Arama Algoritması
- **Durum:** `[REA]` & `[DOK]`
- G*Power, verilen $d, \alpha, \text{hedef güç}, r = N_2/N_1$ değerleri için $N_2 = \lceil r \cdot N_1 \rceil$ kuralını uygular.
- Gerçekleşen gücün hedef gücü sağladığı ($\text{power} \ge \text{target\_power}$) en küçük tamsayı $N_1$ aranır.
- Doğrulama: Standart ders kitabı senaryosunda ($d=0.5, \alpha=0.05, 1-\beta=0.80, r=1.0$, çift kuyruk):
  - $N_1 = 64, N_2 = 64, \text{Total } N = 128$
  - $df = 126$
  - $\delta = 2.828427$
  - $t_{crit} = 1.978971$
  - Gerçekleşen Güç $= 0.801460$ (Hedef %80'in hemen üzerinde).

---

## 4. Oracle Veri Seti

- **A Priori Vektörleri:** `oracle/vectors_a_priori.csv` (20 adet tam hassasiyetli vektör) `[REA]`
- **Post Hoc Vektörleri:** `oracle/vectors_post_hoc.csv` (20 adet tam hassasiyetli vektör) `[REA]`
- **Karşılaştırma Vektörleri:** `oracle/vectors_comparison_500.csv` (500 adet geniş aralıklı rastgele test vektörü) `[REA]`
