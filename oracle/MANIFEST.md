# G*Power 3.1.9.4 Oracle Doğrulama Manifesti (oracle/MANIFEST.md)

Bu belge, 20 A Priori ve 20 Post Hoc olmak üzere toplam 40 doğrulanmış referans vektörünün beklenen G*Power çıktıları ile klon motoru çıktılarının birebir karşılaştırmasını, tolerans uygunluğunu ve G*Power GUI sonuçlarını, klon karşılaştırmalarını ve örneklem yuvarlama denetimlerini sunar.

## Özet İstatistikler
- **Toplam Doğrulanan Vektör:** 40 adet
- **Örneklem Büyüklüğü Tam Eşleşme Oranı:** 40/40 (%100.0)
- **Sayısal Tolerans Uyum Oranı (df, delta, t_crit, power <= 1e-4):** 40/40 (%100.0)
- **A Priori N1−1 denetimi:** 17/20 sonuçta alt tahsis hedef gücün altında; AP_11, AP_12 ve AP_14’te daha küçük tam sayı tahsisi hedefi karşılıyor, ancak G*Power toplam örneklem yuvarlaması bir sonraki grupta biter.
- **Gerçek GUI senaryoları:** 40/40 farklı senaryo, G*Power 3.1.9.4 masaüstü arayüzünde çalıştırıldı (AP_04 pilotu tek kez sayıldı).
- **Geçerli gerçek GUI ekran görüntüsü:** 40 PNG; dosyalar açılabilir ve 554×630 boyutunda.
- **Taze klon çalıştırması:** 40/40 senaryo aynı girdilerle izole Python 3.12 ortamında çalıştırıldı.
- **GUI / klon karşılaştırması:** 40 senaryoda N1/N2/df tam eşleşti ve sayısal alanlar 1e-4 toleransında; AP_11, AP_12 ve AP_14 genel yuvarlama düzeltmesinden sonra eşleşti.


- **Otomatik testler:** `pytest -q -p no:cacheprovider` komutuyla 50 test geçti.
- **Yüksek çözünürlüklü ek yakalamalar:** `evidence/` altında 23 açılabilir 696×790 PNG (AP_01–AP_20 ve PH_01–PH_03); eski 40 görüntüyü korur.

## Detaylı Karşılaştırma Tablosu

| ID | Mod | Kuyruk | d | Alfa | Hedef Güç | Oran | N1 (Beklenen / Klon) | N2 (Beklenen / Klon) | Total N | df | delta | t_crit | Güç (Beklenen / Klon) | N Tam Eşleşme | Tolerans | Minimal N | Ekran Görüntüsü Yolu | GUI Kanıtı |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---:|
| AP_01 | A_priori | 2 | 0.2 | 0.05 | 0.8 | 1.0 | 394 / 394 | 394 / 394 | 788 | 786 | 2.807134 | 1.962987 | 0.800593 / 0.800593 | EVET | EVET | EVET | `screenshots/AP_01.png` | Doğrulandı |
| AP_02 | A_priori | 2 | 0.2 | 0.05 | 0.9 | 1.0 | 527 / 527 | 527 / 527 | 1054 | 1052 | 3.246537 | 1.962222 | 0.900360 / 0.900360 | EVET | EVET | EVET | `screenshots/AP_02.png` | Doğrulandı |
| AP_03 | A_priori | 2 | 0.2 | 0.01 | 0.8 | 1.0 | 586 / 586 | 586 / 586 | 1172 | 1170 | 3.423449 | 2.580038 | 0.800320 / 0.800320 | EVET | EVET | EVET | `screenshots/AP_03.png` | Doğrulandı |
| AP_04 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 1.0 | 64 / 64 | 64 / 64 | 128 | 126 | 2.828427 | 1.978971 | 0.801460 / 0.801460 | EVET | EVET | EVET | `screenshots/gui_pilot_001.png` | Doğrulandı |
| AP_05 | A_priori | 2 | 0.5 | 0.05 | 0.9 | 1.0 | 86 / 86 | 86 / 86 | 172 | 170 | 3.278719 | 1.974017 | 0.903230 / 0.903230 | EVET | EVET | EVET | `screenshots/AP_05.png` | Doğrulandı |
| AP_06 | A_priori | 2 | 0.5 | 0.01 | 0.8 | 1.0 | 96 / 96 | 96 / 96 | 192 | 190 | 3.464102 | 2.601952 | 0.804547 / 0.804547 | EVET | EVET | EVET | `screenshots/AP_06.png` | Doğrulandı |
| AP_07 | A_priori | 2 | 0.5 | 0.01 | 0.95 | 1.0 | 145 / 145 | 145 / 145 | 290 | 288 | 4.257347 | 2.593008 | 0.951234 / 0.951234 | EVET | EVET | EVET | `screenshots/AP_07.png` | Doğrulandı |
| AP_08 | A_priori | 2 | 0.8 | 0.05 | 0.8 | 1.0 | 26 / 26 | 26 / 26 | 52 | 50 | 2.884441 | 2.008559 | 0.807487 / 0.807487 | EVET | EVET | EVET | `screenshots/AP_08.png` | Doğrulandı |
| AP_09 | A_priori | 2 | 0.8 | 0.05 | 0.95 | 1.0 | 42 / 42 | 42 / 42 | 84 | 82 | 3.666061 | 1.989319 | 0.951827 / 0.951827 | EVET | EVET | EVET | `screenshots/AP_09.png` | Doğrulandı |
| AP_10 | A_priori | 2 | 0.8 | 0.01 | 0.9 | 1.0 | 49 / 49 | 49 / 49 | 98 | 96 | 3.959798 | 2.628016 | 0.905774 / 0.905774 | EVET | EVET | EVET | `screenshots/AP_10.png` | Doğrulandı |
| AP_11 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 0.5 | 96 / 96 | 48 / 48 | 144 | 142 | 2.828427 | 1.976811 | 0.802140 / 0.802140 | EVET | EVET | HAYIR (N1−1 tahsisi hedefi karşılıyor) | `screenshots/AP_11.png` | Doğrulandı; yeniden karşılaştırıldı |
| AP_12 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 1.5 | 54 / 54 | 80 / 80 | 134 | 132 | 2.838961 | 1.978099 | 0.804633 / 0.804633 | EVET | EVET | HAYIR (N1−1 tahsisi hedefi karşılıyor) | `screenshots/AP_12.png` | Doğrulandı; yeniden karşılaştırıldı |
| AP_13 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 2.0 | 48 / 48 | 96 / 96 | 144 | 142 | 2.828427 | 1.976811 | 0.802140 / 0.802140 | EVET | EVET | EVET | `screenshots/AP_13.png` | Doğrulandı |
| AP_14 | A_priori | 2 | 0.3 | 0.05 | 0.85 | 1.2 | 185 / 185 | 221 / 221 | 406 | 404 | 3.010511 | 1.965853 | 0.851615 / 0.851615 | EVET | EVET | HAYIR (N1−1 tahsisi hedefi karşılıyor) | `screenshots/AP_14.png` | Doğrulandı; yeniden karşılaştırıldı |
| AP_15 | A_priori | 1 | 0.2 | 0.05 | 0.8 | 1.0 | 310 / 310 | 310 / 310 | 620 | 618 | 2.489980 | 1.647323 | 0.800218 / 0.800218 | EVET | EVET | EVET | `screenshots/AP_15.png` | Doğrulandı |
| AP_16 | A_priori | 1 | 0.5 | 0.05 | 0.8 | 1.0 | 51 / 51 | 51 / 51 | 102 | 100 | 2.524876 | 1.660234 | 0.805899 / 0.805899 | EVET | EVET | EVET | `screenshots/AP_16.png` | Doğrulandı |
| AP_17 | A_priori | 1 | 0.5 | 0.01 | 0.9 | 1.0 | 106 / 106 | 106 / 106 | 212 | 210 | 3.640055 | 2.344236 | 0.901509 / 0.901509 | EVET | EVET | EVET | `screenshots/AP_17.png` | Doğrulandı |
| AP_18 | A_priori | 1 | 0.8 | 0.05 | 0.8 | 1.0 | 21 / 21 | 21 / 21 | 42 | 40 | 2.592296 | 1.683851 | 0.816788 / 0.816788 | EVET | EVET | EVET | `screenshots/AP_18.png` | Doğrulandı |
| AP_19 | A_priori | 1 | 0.5 | 0.05 | 0.8 | 2.0 | 38 / 38 | 76 / 76 | 114 | 112 | 2.516611 | 1.658573 | 0.804142 / 0.804142 | EVET | EVET | EVET | `screenshots/AP_19.png` | Doğrulandı |
| AP_20 | A_priori | 1 | 0.4 | 0.025 | 0.9 | 1.0 | 133 / 133 | 133 / 133 | 266 | 264 | 3.261901 | 1.968990 | 0.901483 / 0.901483 | EVET | EVET | EVET | `screenshots/AP_20.png` | Doğrulandı |
| PH_01 | Post_hoc | 2 | 0.2 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 1.000000 | 1.984467 | 0.167675 / 0.167675 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_01.png` | Doğrulandı |
| PH_02 | Post_hoc | 2 | 0.2 | 0.05 | N/A | 1.0000 | 100 / 100 | 100 / 100 | 200 | 198 | 1.414214 | 1.972017 | 0.290646 / 0.290646 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_02.png` | Doğrulandı |
| PH_03 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 1.936492 | 2.001717 | 0.477897 / 0.477897 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_03.png` | Doğrulandı |
| PH_04 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 1.984467 | 0.696893 / 0.696893 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_04.png` | Doğrulandı |
| PH_05 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 64 / 64 | 64 / 64 | 128 | 126 | 2.828427 | 1.978971 | 0.801460 / 0.801460 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_05.png` | Doğrulandı |
| PH_06 | Post_hoc | 2 | 0.5 | 0.01 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 2.626931 | 0.452992 / 0.452992 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_06.png` | Doğrulandı |
| PH_07 | Post_hoc | 2 | 0.8 | 0.05 | N/A | 1.0000 | 20 / 20 | 20 / 20 | 40 | 38 | 2.529822 | 2.024394 | 0.693404 / 0.693404 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_07.png` | Doğrulandı |
| PH_08 | Post_hoc | 2 | 0.8 | 0.05 | N/A | 1.0000 | 26 / 26 | 26 / 26 | 52 | 50 | 2.884441 | 2.008559 | 0.807487 / 0.807487 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_08.png` | Doğrulandı |
| PH_09 | Post_hoc | 2 | 0.8 | 0.01 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 3.098387 | 2.663287 | 0.667756 / 0.667756 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_09.png` | Doğrulandı |
| PH_10 | Post_hoc | 2 | 0.3 | 0.05 | N/A | 1.5000 | 40 / 40 | 60 / 60 | 100 | 98 | 1.469694 | 1.984467 | 0.307217 / 0.307217 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_10.png` | Doğrulandı |
| PH_11 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 2.0000 | 40 / 40 | 80 / 80 | 120 | 118 | 2.581989 | 1.980272 | 0.726070 / 0.726070 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_11.png` | Doğrulandı |
| PH_12 | Post_hoc | 2 | 0.6 | 0.05 | N/A | 2.0000 | 25 / 25 | 50 / 50 | 75 | 73 | 2.449490 | 1.992997 | 0.676242 / 0.676241 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_12.png` | Doğrulandı |
| PH_13 | Post_hoc | 2 | 0.4 | 0.01 | N/A | 1.5000 | 80 / 80 | 120 / 120 | 200 | 198 | 2.771281 | 2.600887 | 0.568372 / 0.568372 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_13.png` | Doğrulandı |
| PH_14 | Post_hoc | 1 | 0.2 | 0.05 | N/A | 1.0000 | 100 / 100 | 100 / 100 | 200 | 198 | 1.414214 | 1.652586 | 0.406921 / 0.406921 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_14.png` | Doğrulandı |
| PH_15 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 1.936492 | 1.671553 | 0.606025 / 0.606025 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_15.png` | Doğrulandı |
| PH_16 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 1.660551 | 0.798936 / 0.798936 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_16.png` | Doğrulandı |
| PH_17 | Post_hoc | 1 | 0.5 | 0.01 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 2.365002 | 0.555319 / 0.555319 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_17.png` | Doğrulandı |
| PH_18 | Post_hoc | 1 | 0.8 | 0.05 | N/A | 1.0000 | 20 / 20 | 20 / 20 | 40 | 38 | 2.529822 | 1.685954 | 0.799408 / 0.799408 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_18.png` | Doğrulandı |
| PH_19 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 2.0000 | 40 / 40 | 80 / 80 | 120 | 118 | 2.581989 | 1.657870 | 0.821810 / 0.821810 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_19.png` | Doğrulandı |
| PH_20 | Post_hoc | 1 | 0.3 | 0.05 | N/A | 1.5000 | 60 / 60 | 90 / 90 | 150 | 148 | 1.800000 | 1.655215 | 0.558399 / 0.558399 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_20.png` | Doğrulandı |
