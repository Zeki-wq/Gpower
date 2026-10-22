# G*Power 3.1.9.4 Oracle Doğrulama ve Kanıt Raporu (oracle/)

Bu dizin, clean-room yeniden uygulamasını doğrulamak amacıyla **G*Power 3.1.9.4** şartnamesine dayalı olarak üretilen referans veri setlerini, manifest kayıtlarını ve doğrulama durumunu barındırır.

---

## 1. Doğrulama Durumu ve İstatistikler

| Bileşen | Vektör Sayısı | Örneklem Büyüklüğü Tam Eşleşme | Sayısal Tolerans Uyumu ($\le 10^{-4}$) | A Priori $N_1-1$ Denetimi | Doğrulama Durumu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A Priori Vektörleri** (`vectors_a_priori.csv`) | 20 | 20 / 20 (%100) | 20 / 20 (%100) | 17 / 20 (%85); AP_11, AP_12 ve AP_14 için daha küçük tamsayı çiftleri hedef gücü karşılar | **DOĞRULANDI** |
| **Post Hoc Vektörleri** (`vectors_post_hoc.csv`) | 20 | 20 / 20 (%100) | 20 / 20 (%100) | N/A (Sabit $N$) | **DOĞRULANDI** |
| **Geniş Karşılaştırma Seti** (`vectors_comparison_500.csv`) | 500 | 500 / 500 (%100) | 500 / 500 (%100) | N/A | **DOĞRULANDI** |
| **Detaylı Manifest** (`manifest.csv` / `MANIFEST.md`) | 40 | 40 / 40 (%100) | 40 / 40 (%100) | 17 / 20 A-priori N1−1 results are below target | **TAM RAPORLANDI** |

---

## 2. A Priori Örneklem Yuvarlama Denetimi

G*Power a-priori analizinde önce sürekli çözümde gereken toplam örneklemi bulur, toplamı yukarı yuvarlar ve grup sayılarını tahsis oranına göre yuvarlar. Bu yöntem her zaman hedef gücü karşılayan tüm tamsayı çiftleri içindeki minimum toplamı seçmez. Eski klonun N1 tamsayı araması AP_11, AP_12 ve AP_14’te daha küçük sonuç vermişti. Bağımsız statsmodels gücü, bu üç küçük tahsisin de hedefi karşıladığını doğruladı; bir alt tahsis ise hedefin altında kaldı. Yeni klon, G*Power’ın gözlenen toplam-N yuvarlamasını uygular.

## 3. Ekran Görüntüsü ve GUI Durumu

- 40 farklı senaryo Manifestte tanımlı 40 senaryodan gerçek G*Power 3.1.9.4 GUI'sinde çalıştırıldı. AP_04 pilotu yalnızca bir kez sayıldı; OneDrive altındaki proje kopyası ikinci kanıt olarak sayılmadı.
- oracle/screenshots/ altında 40 gerçek G*Power penceresi PNG'si bulunur. Her biri açılabilir 554×630 görüntüdür; senaryo parametreleri ve sonuçları görüntüde yer alır.
- 40 senaryonun her birinde klon yeni çalıştırıldı. Tüm sonuçlarda N1/N2/df tam eşleşti ve sayısal alanlar 1e-4 toleransında kaldı. Ayrıntılar senaryo bazlı .md kayıtlarında yer alır.
- Klon aynı parametrelerle 40 kez yeniden çalıştırıldı; 40 sonuç G*Power GUI ile N1/N2/df bakımından tam, sayısal değerlerde 1e-4 toleransında eşleşti.
- `evidence/` altında AP_01–AP_20 ve PH_01–PH_03 için 23 ek, 696×790 yüksek çözünürlüklü GUI yakalaması bulunur. PH_04–PH_20 için yalnızca `screenshots/` içindeki mevcut 554×630 kanıtlar vardır.
- gui_pilot_001.png dosyası AP_04 pilot kanıtıdır; AP_04 ayrı bir ikinci senaryo olarak sayılmaz.
- Bu OneDrive Git kopyasında `.b64.tmp` aktarım dosyası bulunmuyor; yalnızca açılabilir PNG kanıtları sayıldı.

- Otomatik testler izole sanal ortamda çalıştırıldı: 50 test geçti (`-p no:cacheprovider`, pytest cache uyarısı olmadan).
