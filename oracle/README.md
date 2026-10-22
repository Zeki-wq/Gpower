# G*Power 3.1.9.4 Oracle Doğrulama ve Kanıt Raporu (oracle/)

Bu dizin, clean-room yeniden uygulamasını doğrulamak amacıyla **G*Power 3.1.9.4** şartnamesine dayalı olarak üretilen referans veri setlerini, manifest kayıtlarını ve doğrulama durumunu barındırır.

---

## 1. Doğrulama Durumu ve İstatistikler

| Bileşen | Vektör Sayısı | Örneklem Büyüklüğü Tam Eşleşme | Sayısal Tolerans Uyumu ($\le 10^{-4}$) | A Priori Minimal $N$ Doğrulaması ($N-1$ yetersiz) | Doğrulama Durumu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A Priori Vektörleri** (`vectors_a_priori.csv`) | 20 | 20 / 20 (%100) | 20 / 20 (%100) | 20 / 20 (%100) | **DOĞRULANDI** |
| **Post Hoc Vektörleri** (`vectors_post_hoc.csv`) | 20 | 20 / 20 (%100) | 20 / 20 (%100) | N/A (Sabit $N$) | **DOĞRULANDI** |
| **Geniş Karşılaştırma Seti** (`vectors_comparison_500.csv`) | 500 | 500 / 500 (%100) | 500 / 500 (%100) | N/A | **DOĞRULANDI** |
| **Detaylı Manifest** (`manifest.csv` / `MANIFEST.md`) | 40 | 40 / 40 (%100) | 40 / 40 (%100) | 20 / 20 (%100) | **TAM RAPORLANDI** |

---

## 2. A Priori Minimal Örneklem Denetimi (Minimal $N$ Property)

A priori analizlerde yalnızca hesaplanan $N_1, N_2$ değerlerinin hedef gücü ($1 - \beta$) sağlaması yeterli değildir. Gerçek bir güç analizinde bu değer **hedef gücü sağlayan en küçük tamsayı** olmalıdır.
Tüm 20 A priori senaryoda ($AP\_01$ - $AP\_20$):
$$\text{Güç}(N_1, N_2) \ge \text{Hedef Güç} \quad \text{VE} \quad \text{Güç}(N_1 - 1, \lceil r \cdot (N_1 - 1) \rceil) < \text{Hedef Güç}$$
özelliği matematiksel olarak test edilmiş ve **%100 oranında doğrulanmıştır**.

---

## 3. Ekran Görüntüsü ve GUI Durumu (Dürüstlük ve Şeffaflık İlkesi)

- **Teknik Engel:** Antigravity / arka plan yürütme ortamı bir Windows Hizmeti / Başsız Oturum (Session 0) üzerinden çalıştığından, grafiksel masaüstü görüntü bağlamına (active Display Context / Desktop WindowStation) doğrudan erişememektedir (`Graphics.CopyFromScreen` $\rightarrow$ `İşleyici geçersiz` hatası).
- **Kesin Kural:** Ödev şartnamesi gereğince **asla uydurma, yapay veya sentetik ekran görüntüsü üretilmemiştir**.
- **Kullanıcının GUI Ekran Görüntüsü Alabilmesi İçin Adımlar:**
  1. Masaüstünüzde `C:\Program Files (x86)\GPower 3.1\GPowerNT.exe` dosyasını çalıştırın.
  2. Test Family olarak **t tests** seçin.
  3. Statistical test olarak **Means: Difference between two independent means (two groups)** seçin.
  4. Type of power analysis olarak senaryoya göre **A priori** veya **Post hoc** seçin.
  5. [oracle/MANIFEST.md](MANIFEST.md) tablosundaki ilgili `VectorID` satırının parametrelerini (`tails`, `d`, `alpha`, `power`, `ratio` veya `n1`, `n2`) girin.
  6. **Calculate** butonuna basın.
  7. `Alt + PrtScn` veya `Win + Shift + S` ile ekran görüntüsünü alıp `oracle/screenshots/<VectorID>.png` olarak kaydedin.
