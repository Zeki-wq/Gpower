# Clean-Room Uygulama Oturumu İstemi (Implementation Session Prompt)

> **DİKKAT (CLEAN-ROOM PRENSİBİ):** 
> Bu oturum, tersine mühendislik aşamasından kesin olarak yalıtılmıştır. Uygulayıcı ajan veya geliştirici, Ghidra decompilation çıktılarını, ikili dosya analizlerini, `LEDGER.md` dosyasını veya orijinal tersine mühendislik konuşma kayıtlarını **göremez ve kullanamaz**. Geliştirmenin tek yasal ve teknik girdisi onaylanmış `SPEC.md` şartnamesidir.

```markdown
# GÖREV: İki Bağımsız Grup t-Testi İstatistiksel Güç ve Örneklem Hesaplama Modülü (Clean-Room Yeniden Uygulama)

Sen clean-room prensibine göre bağımsız çalışan bir kıdemli yazılım mühendisisin.
Görevin, `SPEC.md` dosyasında Gherkin formatında tanımlanmış olan şartnameyi eksiksiz karşılayan, bağımsız ve temiz bir Python kütüphanesi ve CLI geliştirmektir.

## Girdi Kaynakları
- YALNIZCA `SPEC.md` dosyasını kullanabilirsin.
- Herhangi bir tersine mühendislik logu, disassembly/decompilation çıktısı veya dekompile edilmiş kaynak kodu kullanman KESİNLİKLE YASAKTIR.

## Kapsam
1. **Test Ailesi:** İki bağımsız grubun ortalamaları için t-testi (Student's two-sample independent t-test / Welch's değil; eşit varyans varsayımı).
2. **Analiz Türleri:**
   - **A priori:** Belirli bir alfa, hedef güç, etki büyüklüğü (Cohen's d) ve grup oranı (N2/N1) verildiğinde gerekli örneklem büyüklüğü hesabı.
   - **Post hoc:** Belirli örneklem büyüklükleri (N1, N2), alfa ve etki büyüklüğü d verildiğinde gerçekleşen istatistiksel güç (1 - beta) hesabı.
3. **Parametreler & Çıktılar:**
   - Kuyruk seçimi: Tek kuyruklu (one-tailed) ve çift kuyruklu (two-tailed).
   - Çıktılar: Kritik t değeri (critical t), serbestlik derecesi (df), noncentrality parameter (δ), gerçekleşen güç (actual power), grup 1 örneklemi (N1), grup 2 örneklemi (N2), toplam örneklem (Total N).

## Doğrulama
- Geliştirilen fonksiyonlar `oracle/` klasöründeki doğrulanmış referans veri setleri ve `tests/` birim testleri ile çalıştırılacak.
- Sayısal hassasiyet, standart `scipy.stats` non-central t dağılımı fonksiyonları (`nct.cdf`, `nct.ppf`) veya denk matematiksel formülasyonlarla doğrulanacaktır.
```
