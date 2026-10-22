# G*Power Clone — İki Bağımsız Grup t-Testi İstatistiksel Güç Motoru ve CLI

Bu proje, Heinrich Heine Üniversitesi Düsseldorf tarafından geliştirilen **G*Power 3.1.9.4** yazılımının "İki bağımsız grubun ortalamaları için t-testi (ilaç ve plasebo)" davranışlarının analiz edilmesi, teknik şartnamesinin ([SPEC.md](SPEC.md)) çıkarılması ve **clean-room prensipleriyle** sıfırdan bağımsız olarak yeniden uygulanmasını içerir.

> **ÖNEMLİ YASAL UYARI:**  
> Bu yazılım bağımsız bir eğitim/ödev projesidir. Heinrich Heine University Düsseldorf veya resmî G*Power geliştiricileri ile doğrudan bir bağlantısı veya resmî sponsorluğu yoktur. Orijinal ikili dosyalar veya tescilli kodlar bu depoda barındırılmaz.

---

## 1. Proje Yapısı

```text
Gpower/
├── src/                                # Clean-room hesaplama motoru ve CLI
│   ├── __init__.py
│   ├── calculator.py                  # SciPy tabanlı matematiksel t-test motoru
│   └── cli.py                         # gpower-clone komut satırı arayüzü
├── tests/                              # Kapsamlı test takımı (24 test, 540 vektör)
│   ├── __init__.py
│   ├── test_calculator.py             # Birim, sınır ve monotonluk testleri
│   ├── test_cli.py                    # CLI argüman ve JSON hata testleri
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
├── requirements.txt                    # Python bağımlılıkları
├── setup.py                            # Paket ve CLI kurulum tanımlayıcısı
├── gpower-clone.bat                    # Windows doğrudan çalıştırma betiği
├── LICENSE                             # MIT Lisansı ve bilimsel atıf
└── README.md                           # Proje dokümantasyonu
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

## 6. Test Takımı ve Doğrulama Sonuçları

Testler `pytest` ile çalıştırılır:

```bash
python -m pytest -v
```

**Test Sonuçları:**
- **Toplam Test:** 24/24 BAŞARILI (%100 Başarım Oranı).
- **Doğrulanan Vektörler:**
  - 20 A Priori Vektörü ([oracle/vectors_a_priori.csv](oracle/vectors_a_priori.csv))
  - 20 Post Hoc Vektörü ([oracle/vectors_post_hoc.csv](oracle/vectors_post_hoc.csv))
  - 500 Karşılaştırma ve Dayanıklılık Vektörü ([oracle/vectors_comparison_500.csv](oracle/vectors_comparison_500.csv))
- **Hassasiyet Toleransları:** Serbestlik derecesi ve örneklem sayıları tam tamsayı eşleşmesi ($df=N_1+N_2-2$); kritik $t$, $\delta$ ve güç için $\pm 10^{-4}$ tolerans.

---

## 7. Lisans ve Bilimsel Atıf

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Bilimsel referans:
> Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods*, 39, 175-191.
