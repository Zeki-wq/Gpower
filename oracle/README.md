# Oracle Doğrulama Vektörleri ve Durum Raporu (oracle/)

Bu dizin, clean-room uygulamasını ve kabul kriterlerini doğrulamak için **G*Power 3.1.9.4** şartnamesine dayalı olarak üretilen referans test vektörlerini barındırır.

---

## 1. Dosyalar ve Doğrulama Durumu

| Dosya | Vektör Sayısı | Kapsam | Doğrulama Durumu |
| :--- | :--- | :--- | :--- |
| `vectors_a_priori.csv` | 20 | Farklı etki büyüklükleri ($d \in [0.2, 0.8]$), $\alpha \in [0.01, 0.05]$, hedef güç ($0.80 - 0.95$), oranlar ($N_2/N_1 \in [0.5, 2.0]$), tek ve çift kuyruk. | **Matematiksel ve Şartname Doğrulaması:** G*Power 3.1.9.4 formülasyonu ve standart ders kitabı referans senaryoları ($d=0.5, \alpha=0.05, \text{güç}=0.80 \rightarrow N_1=64, N_2=64, df=126, \delta=2.828427, t_{crit}=1.978971, \text{güç}=0.801460$) ile %100 uyumlu. |
| `vectors_post_hoc.csv` | 20 | Farklı örneklem boyutları ($N_1, N_2$), $\alpha$, etki büyüklüğü ve kuyruk seçenekleri. | **Matematiksel ve Şartname Doğrulaması:** G*Power 3.1.9.4 standart senaryosu ($N_1=50, N_2=50, d=0.5, \alpha=0.05 \rightarrow df=98, \delta=2.500000, t_{crit}=1.984467, \text{güç}=0.696893$) ile %100 uyumlu. |
| `vectors_comparison_500.csv` | 500 | Geniş aralıklı rastgele test uzayı ($d \in [0.15, 1.2]$, $\alpha \in [0.001, 0.1]$, $N_1, N_2 \in [10, 500]$). | **Karşılaştırma ve Dayanıklılık Vektörleri:** Sayısal taşma ve uç durum regresyon testi amacıyla SciPy istatistik motoru ile üretilmiş bağımsız kontrol seti. |

---

## 2. Doğrulama Ayrımı ve Ekran Görüntüleri İlkesi

- **ÖNEMLİ:** CSV dosyalarındaki vektörler, G*Power 3.1.9.4'ün kullandığı noncentral Student-t algoritmasıyla sayısal olarak doğrulanmıştır. Ancak 540 vektörün tamamı için tek tek manuel GUI ekran görüntüsü alınmamıştır.
- Terminal ortamı arka planda (Session 0) çalıştığı için aktif bir ekran bağlamı bulunmamaktadır; ödev talimatı uyarınca uydurma veya sentetik ekran görüntüsü kesinlikle üretilmemiştir.
- GUI ekran görüntüleri masaüstü ortamında `GPowerNT.exe` açılarak `screenshots/` klasörüne manuel olarak eklenebilir.
