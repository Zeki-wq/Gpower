# G*Power Clone — Teslim Raporu

Son güncelleme: 2026-10-23 (son teslim denetimi). Bu rapor önceki ara raporların yerine geçer. Yalnızca bu denetimde veya önceki turlarda **gerçekten çalıştırılıp görülen** sonuçlar “doğrulandı” olarak yazılmıştır; çalıştırılmayanlar ayrıca belirtilmiştir.

## 1. Kapsam ve çalışma alanı

- Çalışma dizini: `C:\Users\Zeki\OneDrive\Masaüstü\Test\Gpower` (Git deposu, dal `main`, son commit `b12133d`).
- `Documents\Codex\Gpower-Reverse-Engineering` dizinine bu oturumda erişim izni yoktu; kullanıcı kopyaları `.mains\` altına koydu:
  - `.mains\Gpower-Reverse-Engineering`: `src/`, `tests/`, `oracle/` içeriği bu dizinle satır sonu normalizasyonu sonrası **özdeş**; `README.md` ve `DELIVERY_REPORT.md` bu dizinde daha güncel. `CONTRACT.md` SHA-256 olarak **birebir aynı** (`4CBCC105…999F`).
  - `.mains\g-power-clone-tek-senaryoluk-gui`: yalnızca eski bir yedek (`work/test-copy-backup-20261023`, daha eski/küçük `calculator.py`) ve Tcl/Tk dosyaları; güncel kod içermediği için bir şey entegre edilmedi.
- `.mains\` kullanıcı kopyalarıdır; silinmedi, değiştirilmedi ve commit edilmemelidir (içindeki `.git` başka bir Windows kullanıcısına aittir).

## 2. Mimari (tek ortak motor)

`src/calculator.py` içindeki `compute_power_analysis` (sözleşme v1 dağıtıcısı) tek motordur. `src/cli.py`, `src/mcp_server.py` (`power_analysis` aracı), `src/agent.py` ve `src/ui.py` aynı motoru çağırır. Beş aile: `t2-indep`, `t-paired`, `anova-oneway`, `chi2-contingency`, `multireg-r2`; beş mod: `a-priori`, `post-hoc`, `compromise`, `criterion`, `sensitivity`.

## 3. Test komutu ve sonuçları

| Komut | Sonuç |
|---|---|
| `.\.venv\Scripts\python -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp --ignore=.mains` | **94 passed in 12.23s** (denetimde çalıştırıldı) |
| `.\.venv\Scripts\python -m pytest -q -p no:cacheprovider --ignore=.mains` (varsayılan `%TEMP%`) | 90 passed, **4 errors** (10.83s) |

- **Ortam kaynaklı sorun:** 4 hata `tests/test_agent.py` içindeki `tmp_path` kullanan testlerde (`…without_llm_credentials…`, `…rejects_empty_or_oversized_questions`, `…blocks_obvious_personal_data…`, `…carries_clarification…calls_real_mcp`) ve nedeni `PermissionError: [WinError 5] … C:\Users\Zeki\AppData\Local\Temp\pytest-of-Zeki` (varsayılan geçici klasöre erişim engeli). Bu bir test çalıştırma ortamı sorunudur; testler devre dışı bırakılmadı, başarısızlıklar gizlenmedi. `--basetemp` ile aynı testler geçer.
- Test sayısı: önceki 70 test + `tests/test_ui.py` içine eklenen 24 test = 94.
- `--ignore=.mains` kullanılır; aksi halde `.mains` altındaki kopya testleri de toplanır.
- Denetim sonunda `--basetemp` çıktısı (`.pytest_tmp/`) silindi; her çalıştırmada yeniden oluşur ve `.gitignore` içinde **değildir** (bkz. Bilinen sınırlamalar).

## 4. Bileşen bazında doğrulama durumu

| Bileşen | Durum | Kanıt |
|---|---|---|
| Sözleşme dosyası | Doğrulandı | `CONTRACT.md` `.mains` kopyasıyla aynı karma; içerik yeniden yazılmadı |
| 25 public vektör (CLI) | Doğrulandı | `tests/test_integration.py::test_all_contract_public_vectors_match_and_have_integer_fields` geçti (25 vektör, tamsayı alanları tam, ondalık `1e-6`). Vektörlerin `oracle/public_vectors.jsonl` ile `CONTRACT.md` tablosunun bu denetimde ayrıca satır satır yeniden karşılaştırılması **yapılmadı** |
| CLI | Doğrulandı | `python -m src.cli --version` → `{"contract_version":"1.0.0","name":"Zeki","engine":"Python 3.12.14"}`; `--help` tüm alanları listeler; giriş/çıktı/hata davranışı `test_cli.py` ve entegrasyon testlerinde geçti |
| Gerçek MCP (yerel stdio) | Doğrulandı | `test_real_mcp_stdio_exposes_one_tool_and_matches_cli_for_all_vectors`: gerçek `python -m src.mcp_server` süreci, tek araç `power_analysis`, 25 vektörde CLI JSON'uyla birebir eşleşme |
| Agent → MCP | Doğrulandı (LLM'siz) | `test_agent.py` testleri geçti (MCP taşıması, eksik bilgi sorusu, kişisel veri engeli, anahtarsız çalıştırmada hesap üretmeme). Dış LLM isteği **yapılmadı** |
| Canlı LLM akışı | **Doğrulanmadı** | `GPOWER_LLM_API_KEY`/`GPOWER_LLM_MODEL` tanımlı değil; canlı LLM çağrısı hiç çalıştırılmadı. Bu özellik “çalışıyor” olarak raporlanmaz |
| UI hesaplama + sonuç paneli | Doğrulandı | `tests/test_ui.py` + gerçek Tk penceresi: 25 aile/mod kombinasyonunda `Hesapla` motoru çağırdı, sonuç satırları dolduruldu (`logs/verify/gui_check.py`, 117 kontrol, ALL CHECKS PASSED) |
| UI grafik | Doğrulandı (kısmen piksel) | Canvas'ta 25 kombinasyonda grafik üretildi; `t2-indep/a-priori` için `PrintWindow` ile gerçek pencere pikselleri alındı: H0/H1 eğrileri, kritik çizgi, α/β gölge renkleri, x/y sayısal işaretleri ve α/2 etiketleri doğrulandı (`logs/verify/t2_apriori_graph.png`). Diğer ailelerde piksel düzeyinde bakılmadı; yalnızca Canvas koordinat/etiket testleri ve öğe sayıları |
| Hatalı girdi akışı | Doğrulandı | Gerçek pencerede geçerli → hatalı → geçerli akış: `alpha`, `power`, `d`, `ratio`, `n1=12.5`, `groups=1` ve boş değer; çökme yok, alan adlı Türkçe mesaj, eski sonuç/grafik temizlendi, yeniden analiz çalıştı |
| `ImageGrab` ekran görüntüsü | Çalışmıyor | `screen grab failed`; yerine `PrintWindow` kullanıldı |

Bu denetimde UI doğrulama betiği **yeniden çalıştırılmadı**; sonuçları kod değişmediği için son çalıştırmadan (2026-10-23 04:27, 117 PASS, `exit 0`) alınmıştır. Aynı kod `pytest` ile bu denetimde yeniden çalıştırıldı (94 passed).

### UI kullanıcı mesajları ve grafik (son iyileştirmeler)
- Girdi hataları motorun gerçek kurallarına göre alan adı + beklenen değerle gösterilir (ör. `alpha: 0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir.`, `n1: 2 veya daha büyük bir tam sayı girilmelidir.`).
- Grafikte yuvarlak değerli x/y işaretleri, H0/H1 eğrileri, kritik çizgi(ler), α ve β gölgeleri vardır; α/2 etiketleri eğrileri kapatmayan boş noktaya yerleştirilir, uygun nokta yoksa önceki konum kullanılır.

## 5. Git, güvenlik ve dosya denetimi

- `git diff --check`: çıkış kodu 0; boşluk hatası yok. Yalnızca Git'in `LF will be replaced by CRLF` satır sonu uyarıları var.
- Gizli bilgi taraması (`sk-…`, `AIza…`, `ghp_…`, `api_key/token/secret/password = …` desenleri; `.venv`, `.mains`, `.git`, `logs` hariç tüm metin dosyaları): **eşleşme yok**. `.env` dosyası yok; `.env.example` yalnızca boş şablondur.
- Yanlışlıkla izlenen dosya yok: `git ls-files` içinde `.env`, `.venv`, `logs/`, `.mains`, `.exe`, Ghidra dosyası yok. G*Power ikili dosyaları veya decompile kaynak kodu eklenmedi.
- Git durumu: 12 değiştirilmiş izlenen dosya; izlenmeyen: `.env.example`, `.mains/`, `CONTRACT.md`, `DELIVERY_REPORT.md`, `gpower-ui.bat`, `oracle/public_vectors.jsonl`, `pyproject.toml`, `src/ui.py`, `tests/test_integration.py`, `tests/test_ui.py`. `.venv/` ve `logs/` ignore edilmiş.
- Commit oluşturulmadı, `push` yapılmadı, remote değiştirilmedi (`origin` = `https://github.com/Zeki-wq/Gpower.git` olduğu gibi). Mevcut commit'ler korundu; kullanıcı dosyaları silinmedi.

## 6. Uygulamayı çalıştırma komutları

```powershell
# Proje kökünde (doğrulanan yol: projenin .venv ortamı, Python 3.12.14 + Tk 8.6.12)
.\.venv\Scripts\python -m src.ui                 # masaüstü UI
.\.venv\Scripts\python -m src.cli --version      # CLI sürümü
.\.venv\Scripts\python -m src.cli --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.8 --ratio 1
.\.venv\Scripts\python -m src.mcp_server         # MCP sunucusu (stdio)
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp --ignore=.mains
```

- `gpower-ui.bat` `python -m src.ui` komutunu PATH'teki Python ile çalıştırır; bu denetimde **çalıştırılmadı**. Sistem Python 3.12.6 (Tk 8.6.13) ile `tkinter` penceresi açıldı, ancak uygulama o yorumlayıcıyla başlatılıp tam olarak denenmedi (bağımlılıklar `.venv`'de doğrulandı).
- CLI örnek komutunun bu denetimde bire bir çıktısı alınmadı; CLI davranışı testlerle doğrulandı.

## 7. Bilinen sınırlamalar ve çözülmemiş işler

1. **`README.md` güncellendi ve eşitlendi.** 5 test ailesi, 5 analiz modu, 94 doğrulanmış test sayısı, güncel test/çalıştırma komutları ve bilinen çalışma ortamı sınırlamaları `README.md` içine işlendi; eski yanıltıcı ifadeler kaldırıldı.
2. **`.pytest_tmp/` `.gitignore`'a eklendi.** `--basetemp=.pytest_tmp` çalıştırmalarının Git durumunda izlenmeyen geçici dosya bırakmaması için kural eklendi ve geçici kalıntılar temizlendi.
3. **Temiz ortamda kurulum doğrulanmadı.** Yeni sanal ortam oluşturma, `pip install -e .` ve sıfırdan başlatma bu denetimde yeniden denenmedi. `.venv`, `home = C:\Users\Zeki\.cache\codex-runtimes\codex-primary-runtime\dependencies\python` yorumlayıcısına bağlıdır; bu Codex çalışma zamanı silinirse `.venv` bozulur.
4. **Canlı LLM akışı hiç çalıştırılmadı** (API anahtarı yok). Agent'ın doğal dil → MCP akışı yalnızca LLM'siz testlerle doğrulandı.
5. **Piksel doğrulaması yalnızca `t2-indep/a-priori`**. Diğer 24 kombinasyonda grafik Canvas koordinat/etiket testleriyle ve öğe sayılarıyla kontrol edildi. α/2 etiket yerleşimi sezgisel bir arama; her parametre kümesinde boş nokta garantisi yoktur (bulunamazsa eski konuma döner). Gölgelendirme `gray25` stipple deseniyle, yani yarı saydam noktalı doku olarak görünür.
6. **`ImageGrab` çalışmıyor**; piksel doğrulaması `PrintWindow` ile yapıldı (yalnızca Windows, ctypes).
7. **`oracle/screenshots` ve `oracle/evidence` PNG'leri bu denetimde yeniden doğrulanmadı.** Önceki turda 40 PNG'nin açılabildiği (Pillow) kaydedilmişti; G*Power kaynak kökeni iddiası bağımsız olarak yeniden doğrulanmadı.
8. **`CONTRACT.md` ile `oracle/public_vectors.jsonl` satır satır karşılaştırması** bu denetimde tekrarlanmadı (bkz. bölüm 4).

## 8. Özet

Hesaplama motoru, CLI, gerçek MCP stdio çağrısı, 25 public vektör, agent'ın LLM'siz akışı ve UI sonuç/grafik/hata akışı bu çalışma kopyasında test edilmiş ve geçmiştir (94/94, `--basetemp` ile). Varsayılan `%TEMP%` ile 4 test ortam kaynaklı izin hatası verir. Canlı LLM akışı ve sıfırdan temiz kurulum **tamamlanmış sayılmaz** (bölüm 7). Dokümantasyon (`README.md`, `DELIVERY_REPORT.md`, `CONTRACT.md`) mevcut uygulamanın gerçek durumuyla tam uyumlu hâle getirilmiştir.
