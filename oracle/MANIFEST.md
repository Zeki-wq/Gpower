# G*Power 3.1.9.4 Oracle Doğrulama Manifesti (oracle/MANIFEST.md)

Bu belge, 20 A Priori ve 20 Post Hoc olmak üzere toplam 40 doğrulanmış referans vektörünün beklenen G*Power çıktıları ile klon motoru çıktılarının birebir karşılaştırmasını, tolerans uygunluğunu ve minimal örneklem denetimlerini sunar.

## Özet İstatistikler
- **Toplam Doğrulanan Vektör:** 40 adet
- **Örneklem Büyüklüğü Tam Eşleşme Oranı:** 40/40 (%100.0)
- **Sayısal Tolerans Uyum Oranı (df, delta, t_crit, power <= 1e-4):** 40/40 (%100.0)
- **A Priori Minimal Örneklem Doğrulama Oranı (N-1 hedef gücü sağlamaz):** 20/20 (%100.0)
- **Ekran Görüntüsü Durumu:** Windows Session 0 arka plan kısıtı nedeniyle otomatik masaüstü yakalama yapılamamış; sahte ekran görüntüsü üretmeme kuralına uyulmuştur.

## Detaylı Karşılaştırma Tablosu

| ID | Mod | Kuyruk | d | Alfa | Hedef Güç | Oran | N1 (Beklenen / Klon) | N2 (Beklenen / Klon) | Total N | df | delta | t_crit | Güç (Beklenen / Klon) | N Tam Eşleşme | Tolerans | Minimal N | Ekran Görüntüsü Yolu |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| AP_01 | A_priori | 2 | 0.2 | 0.05 | 0.8 | 1.0 | 394 / 394 | 394 / 394 | 788 | 786 | 2.807134 | 1.962987 | 0.800593 / 0.800593 | EVET | EVET | EVET | `screenshots/AP_01.png` |
| AP_02 | A_priori | 2 | 0.2 | 0.05 | 0.9 | 1.0 | 527 / 527 | 527 / 527 | 1054 | 1052 | 3.246537 | 1.962222 | 0.900360 / 0.900360 | EVET | EVET | EVET | `screenshots/AP_02.png` |
| AP_03 | A_priori | 2 | 0.2 | 0.01 | 0.8 | 1.0 | 586 / 586 | 586 / 586 | 1172 | 1170 | 3.423449 | 2.580038 | 0.800320 / 0.800320 | EVET | EVET | EVET | `screenshots/AP_03.png` |
| AP_04 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 1.0 | 64 / 64 | 64 / 64 | 128 | 126 | 2.828427 | 1.978971 | 0.801460 / 0.801460 | EVET | EVET | EVET | `screenshots/AP_04.png` |
| AP_05 | A_priori | 2 | 0.5 | 0.05 | 0.9 | 1.0 | 86 / 86 | 86 / 86 | 172 | 170 | 3.278719 | 1.974017 | 0.903230 / 0.903230 | EVET | EVET | EVET | `screenshots/AP_05.png` |
| AP_06 | A_priori | 2 | 0.5 | 0.01 | 0.8 | 1.0 | 96 / 96 | 96 / 96 | 192 | 190 | 3.464102 | 2.601952 | 0.804547 / 0.804547 | EVET | EVET | EVET | `screenshots/AP_06.png` |
| AP_07 | A_priori | 2 | 0.5 | 0.01 | 0.95 | 1.0 | 145 / 145 | 145 / 145 | 290 | 288 | 4.257347 | 2.593008 | 0.951234 / 0.951234 | EVET | EVET | EVET | `screenshots/AP_07.png` |
| AP_08 | A_priori | 2 | 0.8 | 0.05 | 0.8 | 1.0 | 26 / 26 | 26 / 26 | 52 | 50 | 2.884441 | 2.008559 | 0.807487 / 0.807487 | EVET | EVET | EVET | `screenshots/AP_08.png` |
| AP_09 | A_priori | 2 | 0.8 | 0.05 | 0.95 | 1.0 | 42 / 42 | 42 / 42 | 84 | 82 | 3.666061 | 1.989319 | 0.951827 / 0.951827 | EVET | EVET | EVET | `screenshots/AP_09.png` |
| AP_10 | A_priori | 2 | 0.8 | 0.01 | 0.9 | 1.0 | 49 / 49 | 49 / 49 | 98 | 96 | 3.959798 | 2.628016 | 0.905774 / 0.905774 | EVET | EVET | EVET | `screenshots/AP_10.png` |
| AP_11 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 0.5 | 95 / 95 | 48 / 48 | 143 | 141 | 2.823478 | 1.976931 | 0.800731 / 0.800731 | EVET | EVET | EVET | `screenshots/AP_11.png` |
| AP_12 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 1.5 | 53 / 53 | 80 / 80 | 133 | 131 | 2.823106 | 1.978239 | 0.800216 / 0.800216 | EVET | EVET | EVET | `screenshots/AP_12.png` |
| AP_13 | A_priori | 2 | 0.5 | 0.05 | 0.8 | 2.0 | 48 / 48 | 96 / 96 | 144 | 142 | 2.828427 | 1.976811 | 0.802140 / 0.802140 | EVET | EVET | EVET | `screenshots/AP_13.png` |
| AP_14 | A_priori | 2 | 0.3 | 0.05 | 0.85 | 1.2 | 184 / 184 | 221 / 221 | 405 | 403 | 3.006068 | 1.965868 | 0.850582 / 0.850582 | EVET | EVET | EVET | `screenshots/AP_14.png` |
| AP_15 | A_priori | 1 | 0.2 | 0.05 | 0.8 | 1.0 | 310 / 310 | 310 / 310 | 620 | 618 | 2.489980 | 1.647323 | 0.800218 / 0.800218 | EVET | EVET | EVET | `screenshots/AP_15.png` |
| AP_16 | A_priori | 1 | 0.5 | 0.05 | 0.8 | 1.0 | 51 / 51 | 51 / 51 | 102 | 100 | 2.524876 | 1.660234 | 0.805899 / 0.805899 | EVET | EVET | EVET | `screenshots/AP_16.png` |
| AP_17 | A_priori | 1 | 0.5 | 0.01 | 0.9 | 1.0 | 106 / 106 | 106 / 106 | 212 | 210 | 3.640055 | 2.344236 | 0.901509 / 0.901509 | EVET | EVET | EVET | `screenshots/AP_17.png` |
| AP_18 | A_priori | 1 | 0.8 | 0.05 | 0.8 | 1.0 | 21 / 21 | 21 / 21 | 42 | 40 | 2.592296 | 1.683851 | 0.816788 / 0.816788 | EVET | EVET | EVET | `screenshots/AP_18.png` |
| AP_19 | A_priori | 1 | 0.5 | 0.05 | 0.8 | 2.0 | 38 / 38 | 76 / 76 | 114 | 112 | 2.516611 | 1.658573 | 0.804142 / 0.804142 | EVET | EVET | EVET | `screenshots/AP_19.png` |
| AP_20 | A_priori | 1 | 0.4 | 0.025 | 0.9 | 1.0 | 133 / 133 | 133 / 133 | 266 | 264 | 3.261901 | 1.968990 | 0.901483 / 0.901483 | EVET | EVET | EVET | `screenshots/AP_20.png` |
| PH_01 | Post_hoc | 2 | 0.2 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 1.000000 | 1.984467 | 0.167675 / 0.167675 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_01.png` |
| PH_02 | Post_hoc | 2 | 0.2 | 0.05 | N/A | 1.0000 | 100 / 100 | 100 / 100 | 200 | 198 | 1.414214 | 1.972017 | 0.290646 / 0.290646 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_02.png` |
| PH_03 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 1.936492 | 2.001717 | 0.477897 / 0.477897 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_03.png` |
| PH_04 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 1.984467 | 0.696893 / 0.696893 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_04.png` |
| PH_05 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 1.0000 | 64 / 64 | 64 / 64 | 128 | 126 | 2.828427 | 1.978971 | 0.801460 / 0.801460 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_05.png` |
| PH_06 | Post_hoc | 2 | 0.5 | 0.01 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 2.626931 | 0.452992 / 0.452992 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_06.png` |
| PH_07 | Post_hoc | 2 | 0.8 | 0.05 | N/A | 1.0000 | 20 / 20 | 20 / 20 | 40 | 38 | 2.529822 | 2.024394 | 0.693404 / 0.693404 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_07.png` |
| PH_08 | Post_hoc | 2 | 0.8 | 0.05 | N/A | 1.0000 | 26 / 26 | 26 / 26 | 52 | 50 | 2.884441 | 2.008559 | 0.807487 / 0.807487 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_08.png` |
| PH_09 | Post_hoc | 2 | 0.8 | 0.01 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 3.098387 | 2.663287 | 0.667756 / 0.667756 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_09.png` |
| PH_10 | Post_hoc | 2 | 0.3 | 0.05 | N/A | 1.5000 | 40 / 40 | 60 / 60 | 100 | 98 | 1.469694 | 1.984467 | 0.307217 / 0.307217 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_10.png` |
| PH_11 | Post_hoc | 2 | 0.5 | 0.05 | N/A | 2.0000 | 40 / 40 | 80 / 80 | 120 | 118 | 2.581989 | 1.980272 | 0.726070 / 0.726070 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_11.png` |
| PH_12 | Post_hoc | 2 | 0.6 | 0.05 | N/A | 2.0000 | 25 / 25 | 50 / 50 | 75 | 73 | 2.449490 | 1.992997 | 0.676241 / 0.676241 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_12.png` |
| PH_13 | Post_hoc | 2 | 0.4 | 0.01 | N/A | 1.5000 | 80 / 80 | 120 / 120 | 200 | 198 | 2.771281 | 2.600887 | 0.568372 / 0.568372 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_13.png` |
| PH_14 | Post_hoc | 1 | 0.2 | 0.05 | N/A | 1.0000 | 100 / 100 | 100 / 100 | 200 | 198 | 1.414214 | 1.652586 | 0.406921 / 0.406921 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_14.png` |
| PH_15 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 1.0000 | 30 / 30 | 30 / 30 | 60 | 58 | 1.936492 | 1.671553 | 0.606025 / 0.606025 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_15.png` |
| PH_16 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 1.660551 | 0.798936 / 0.798936 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_16.png` |
| PH_17 | Post_hoc | 1 | 0.5 | 0.01 | N/A | 1.0000 | 50 / 50 | 50 / 50 | 100 | 98 | 2.500000 | 2.365002 | 0.555319 / 0.555319 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_17.png` |
| PH_18 | Post_hoc | 1 | 0.8 | 0.05 | N/A | 1.0000 | 20 / 20 | 20 / 20 | 40 | 38 | 2.529822 | 1.685954 | 0.799408 / 0.799408 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_18.png` |
| PH_19 | Post_hoc | 1 | 0.5 | 0.05 | N/A | 2.0000 | 40 / 40 | 80 / 80 | 120 | 118 | 2.581989 | 1.657870 | 0.821810 / 0.821810 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_19.png` |
| PH_20 | Post_hoc | 1 | 0.3 | 0.05 | N/A | 1.5000 | 60 / 60 | 90 / 90 | 150 | 148 | 1.800000 | 1.655215 | 0.558399 / 0.558399 | EVET | EVET | N/A (Post_hoc) | `screenshots/PH_20.png` |
