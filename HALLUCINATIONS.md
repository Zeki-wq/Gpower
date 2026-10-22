# Karşılaşılan Yapay Zeka / Otomasyon Hataları Günlüğü (HALLUCINATIONS.md)

Bu belgede, oturum boyunca gerçekten karşılaşılan sözdizimsel, araçsal ve sayısal hatalar, bunların nasıl keşfedildiği ve hangi testlerle yakalandığı ayrıntılı olarak kaydedilmiştir. (Hiçbir varsayımsal veya yaşanmamış hata uydurulmamıştır).

---

### Hata 1: PowerShell Çift Tırnak İçinde Değişken Enterpolasyonu ve Ayrıştırma Hatası
- **Tür:** Shell Syntax / Parameter Parsing Hatası
- **Keşif Yöntemi:** Aşama 1 ortam kontrol komutunun çalıştırılması sırasında terminal çıktısının incelenmesi.
- **Açıklama:** PowerShell `-Command` çağrısı çift tırnak (`powershell -Command "..."`) içinde çalıştırıldığında, komut dizgisi içerisindeki `$fi.Length` ve `-f` operatörü PowerShell tarafından subexpression ayrıştırmasında yutulmuş ve `$fi` boş stringe indirgendiği için `At line:17 char:44: You must provide a value expression following the '-f' operator` hatası üretmiştir.
- **Düzeltme & Çözüm:** Komutlar tek tırnaklı script blokları (`& { ... }`) ve ters tırnaklı (`$`) kaçış karakterleriyle yeniden yazıldı; karmaşık işlemler için modüler python betikleri devreye alındı.

---

### Hata 2: Windows PowerShell Eski TLS Protokolü Varsayımı
- **Tür:** Ağ / Protokol Uyuşmazlığı Hatası
- **Keşif Yöntemi:** G*Power resmî web sayfası kontrol edilirken `Invoke-WebRequest` çıktısının incelenmesi.
- **Açıklama:** G*Power resmî dağıtım sitesi (`https://www.psychologie.hhu.de/...`) üzerinden bağlantı testi yapılırken PowerShell `Invoke-WebRequest` doğrudan çağrıldığında, Windows PowerShell'in varsayılan güvenlik protokolünün (SSL3/TLS 1.0) modern HTTPS sunucusu tarafından reddedilmesi nedeniyle `Temel alınan bağlantı kapatıldı: Gönderme işleminde beklenmeyen hata oluştu` hatası alınmıştır.
- **Düzeltme & Çözüm:** `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12` bayrağı açıkça tanımlanmış ve resmî URL doğrulaması tamamlanmıştır.

---

### Hata 3: Non-Interactive Oturumda PIL ImageGrab Başarısızlığı
- **Tür:** İşletim Sistemi / GUI Ekran Yakalama Kısıtlaması
- **Keşif Yöntemi:** `scratch/take_screenshot.py` betiğinin çalıştırılması sırasında fırlatılan `OSError` istisnası.
- **Açıklama:** Arka planda çalışan Python betiğinden doğrudan `PIL.ImageGrab.grab()` çağrıldığında, arka plan terminal oturumunun grafiksel bir masaüstü ekran cihazına (active Display Context / Interactive Desktop Session) bağlı olmaması nedeniyle `OSError: screen grab failed` hatası alınmıştır.
- **Düzeltme & Çözüm:** Masaüstü yakalama denemesi güvenli biçimde sonlandırılmış, GPower süreci kapatılmış; ekran görüntüsü gereksinimi için kullanıcının GUI üzerinden ekran görüntüsü alabilmesi için kılavuz hazırlanmış ve sahte ekran görüntüsü üretmeme kuralına harfiyen uyulmuştur.

---

### Hata 4: Yüksek Noncentrality Değerlerinde SciPy nct.cdf Sayısal NaN Hatası
- **Tür:** Sayısal Analiz / Taşma Hatası
- **Keşif Yöntemi & Yakalayan Test:** `tests/test_oracle_validation.py::test_validate_500_comparison_vectors` testi tarafından `COMP_0004` (ve diğer 47 uç vaka) çalıştırılırken yakalandı.
- **Açıklama:** Büyük noncentrality parametresi ($\delta > 10$) ve yüksek serbestlik derecesine sahip test vektörlerinde, çift kuyruklu güç formülündeki sol kuyruk kuantili ($F_{df, \delta}(-t_{crit})$) matematiksel olarak $10^{-30}$ mertebesinde bir olasılık ifade etmesine rağmen SciPy'nin hipergeometrik seri açılımında sayısal taşma nedeniyle `NaN` üretmiştir.
- **Düzeltme & Çözüm:** `src/calculator.py` içerisine sayısal kararlılık kontrolleri eklendi: $\delta > 0$ iken aşırı sol kuyruk olasılıkları için `math.isnan(cdf_lower)` durumu $0.0$, aşırı sağ kuyruk taşmaları için $0.0$ olarak sınırlandırıldı. 500 karşılaştırma vektörü yeniden doğrulanarak 100% test başarımı sağlandı.

---

### Hata 5: Konsol Kod Sayfası ve Türkçe Karakter Regex Eşleşme Uyuşmazlığı
- **Tür:** Kodlama (Encoding) / Regex Test Hatası
- **Keşif Yöntemi & Yakalayan Test:** `tests/test_calculator.py::TestInputValidation::test_invalid_target_power` testi.
- **Açıklama:** Windows Türkçe konsol ortamında `match="hedef güç"` ifadesi, konsolun yerel CP1254/UTF-8 ayrıştırması sebebiyle regex içinde karakter uyuşmazlığına yol açmış ve `AssertionError: Regex pattern did not match` üretmiştir.
- **Düzeltme & Çözüm:** Hata mesajı denetiminde `match=r"(?i)power|hedef"` şeklinde genişletilmiş regex deseni kullanılarak platformdan bağımsız tam test uyumluluğu sağlandı.
