# G*Power İki Bağımsız Grup t-Testi Teknik Şartnamesi (SPEC.md)

Bu belge, iki bağımsız grubun ortalamaları için Student t-testi (ilaç ve plasebo) güç analizi ve örneklem büyüklüğü hesaplamalarına yönelik fonksiyonel ve davranışsal kabul kriterlerini Gherkin biçiminde tanımlar.

---

## Özellik 1: A Priori Örneklem Büyüklüğü Hesaplama (A Priori Sample Size Calculation)

Belirli bir anlamlılık düzeyi ($\alpha$), hedef güç ($1 - \beta$), etki büyüklüğü ($d$) ve grup oranı ($N_2/N_1$) verildiğinde, gereken minimum örneklem büyüklüklerini, kritik $t$, serbestlik derecesi ($df$), noncentrality parameter ($\delta$) ve gerçekleşen gücü hesaplar.

### Senaryo 1.1: Çift Kuyruklu Eşit Grup A Priori Analizi (Standart İlaç vs Plasebo)
```gherkin
Özellik: İki bağımsız grup t-testi A priori örneklem hesabı
  Senaryo: Orta etki büyüklüğü ve dengeli gruplar için iki kuyruklu analiz
    Diyelim ki test türü "t tests"
    Ve alt test "Means: Difference between two independent means (two groups)"
    Ve analiz türü "A priori: Compute required sample size - given alpha, power, and effect size"
    Ve kuyruk seçimi "Two"
    Ve etki büyüklüğü "d = 0.5"
    Ve alfa hata olasılığı "alpha = 0.05"
    Ve hedef güç "power = 0.80"
    Ve örneklem oranı "N2/N1 = 1.0"
    Hesapla butonuna basıldığında
    O zaman kritik t değeri 1.978971 olmalıdır (±0.0001 hassasiyetle)
    Ve serbestlik derecesi df = 126 olmalıdır
    Ve noncentrality parameter delta = 2.828427 olmalıdır (±0.0001 hassasiyetle)
    Ve örneklem büyüklüğü grup 1 (N1) = 64 olmalıdır
    Ve örneklem büyüklüğü grup 2 (N2) = 64 olmalıdır
    Ve toplam örneklem büyüklüğü Total N = 128 olmalıdır
    Ve gerçekleşen güç (actual power) >= 0.801460 olmalıdır
```

### Senaryo 1.2: Tek Kuyruklu Dengesiz Grup A Priori Analizi (İlaç Üstünlük Testi)
```gherkin
  Senaryo: Orta etki büyüklüğü ve 2:1 örneklem oranı ile tek kuyruklu analiz
    Diyelim ki test türü "t tests"
    Ve alt test "Means: Difference between two independent means (two groups)"
    Ve analiz türü "A priori"
    Ve kuyruk seçimi "One"
    Ve etki büyüklüğü "d = 0.5"
    Ve alfa hata olasılığı "alpha = 0.05"
    Ve hedef güç "power = 0.80"
    Ve örneklem oranı "N2/N1 = 2.0"
    Hesapla butonuna basıldığında
    O zaman örneklem büyüklüğü grup 1 (N1) = 38 olmalıdır
    Ve örneklem büyüklüğü grup 2 (N2) = 76 olmalıdır
    Ve toplam örneklem büyüklüğü Total N = 114 olmalıdır
    Ve serbestlik derecesi df = 112 olmalıdır
    Ve noncentrality parameter delta = 2.516611 olmalıdır (±0.0001 hassasiyetle)
    Ve kritik t değeri 1.658573 olmalıdır (±0.0001 hassasiyetle)
    Ve gerçekleşen güç (actual power) >= 0.804142 olmalıdır
```

---

## Özellik 2: Post Hoc İstatistiksel Güç Hesaplama (Post Hoc Power Calculation)

Gözlemlenmiş veya planlanmış örneklem sayıları ($N_1, N_2$), etki büyüklüğü ($d$) ve $\alpha$ değeri verildiğinde, çalışmanın istatistiksel gücünü hesaplar.

### Senaryo 2.1: Çift Kuyruklu Post Hoc Güç Analizi
```gherkin
Özellik: İki bağımsız grup t-testi Post hoc güç hesabı
  Senaryo: Sabit örneklem ve alfa altında güç hesaplama
    Diyelim ki test türü "t tests"
    Ve alt test "Means: Difference between two independent means (two groups)"
    Ve analiz türü "Post hoc: Compute achieved power - given alpha, sample size, and effect size"
    Ve kuyruk seçimi "Two"
    Ve etki büyüklüğü "d = 0.5"
    Ve alfa hata olasılığı "alpha = 0.05"
    Ve örneklem büyüklüğü grup 1 "N1 = 50"
    Ve örneklem büyüklüğü grup 2 "N2 = 50"
    Hesapla butonuna basıldığında
    O zaman serbestlik derecesi df = 98 olmalıdır
    Ve noncentrality parameter delta = 2.500000 olmalıdır (±0.0001 hassasiyetle)
    Ve kritik t değeri 1.984467 olmalıdır (±0.0001 hassasiyetle)
    Ve gerçekleşen güç (power) 0.696893 olmalıdır (±0.0001 hassasiyetle)
```

### Senaryo 2.2: Tek Kuyruklu Dengesiz Örneklem Post Hoc Güç Analizi
```gherkin
  Senaryo: Dengesiz grup boyutlarında tek kuyruklu güç analizi
    Diyelim ki test türü "t tests"
    Ve alt test "Means: Difference between two independent means (two groups)"
    Ve analiz türü "Post hoc"
    Ve kuyruk seçimi "One"
    Ve etki büyüklüğü "d = 0.3"
    Ve alfa hata olasılığı "alpha = 0.05"
    Ve örneklem büyüklüğü grup 1 "N1 = 60"
    Ve örneklem büyüklüğü grup 2 "N2 = 90"
    Hesapla butonuna basıldığında
    O zaman serbestlik derecesi df = 148 olmalıdır
    Ve noncentrality parameter delta = 1.800000 olmalıdır (±0.0001 hassasiyetle)
    Ve kritik t değeri 1.655215 olmalıdır (±0.0001 hassasiyetle)
    Ve gerçekleşen güç (power) 0.558399 olmalıdır (±0.0001 hassasiyetle)
```

---

## Kabul Kriterleri ve Sayısal Doğruluk Standartları

1. **Sayısal Doğruluk:**
   - Serbestlik derecesi ($df$) tam tamsayı eşleşmesi ($df = N_1 + N_2 - 2$).
   - $\delta$ (noncentrality parameter) $10^{-4}$ tolerans.
   - Kritik t değeri $10^{-4}$ tolerans.
   - İstatistiksel güç (power) $10^{-4}$ tolerans.
2. **Kuyruk Tutarlılığı:**
   - Tek kuyruklu testlerde kritik değer dağılımın $1 - \alpha$ noktasındadır ($t_{crit} = t_{df}^{-1}(1 - \alpha)$).
   - Çift kuyruklu testlerde kritik değer dağılımın $1 - \alpha/2$ noktasındadır ($t_{crit} = t_{df}^{-1}(1 - \alpha/2)$).
3. **Oracle Doğrulaması:**
   - Uygulama, `oracle/vectors_a_priori.csv` (20 vektör), `oracle/vectors_post_hoc.csv` (20 vektör) ve `oracle/vectors_comparison_500.csv` (500 vektör) olmak üzere toplam **540 test vektörü** üzerinde 100% test başarımı sağlamalıdır.
