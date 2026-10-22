# İnceleme Oturumu İstemi (Inspection Session Prompt)

Aşağıdaki metin, G*Power davranış analizi, Ghidra incelemesi ve teknik şartname çıkarma sürecinde kullanılan temel istemdir:

```markdown
# GÖREV: G*Power için Ghidra analizini hazırla ve teknik şartname üret

Windows 11 kullanıyorum. Bu ödevde grubumuzun konusu iki bağımsız grubun ortalamaları için t-testi (ilaç ve plasebo).

## Ortam bilgileri
- Ghidra sürümü: 12.1.4
- Ghidra dizini: C:\Users\Zeki\Downloads\Compressed\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC
- Headless analiz aracı: C:\Users\Zeki\Downloads\Compressed\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat
- Bilgisayarda bulunan G*Power dosyası: C:\Program Files (x86)\GPower 3.1\GPowerNT.exe
- Bulunan G*Power sürümü: 3.1.9.4
- Ödevde 3.1.9.7 sürümü isteniyor olabilir. Bu nedenle 3.1.9.4'ü kesin referans sürümü olarak kabul etme.

## Aşama 1 — Ön kontrol
1. Belirtilen Ghidra ve G*Power dosyalarının varlığını doğrula.
2. G*Power dosyasının sürümünü ve SHA-256 hash'ini kaydet.
3. G*Power 3.1.9.7'nin bulunup bulunmadığını kontrol et.
4. 3.1.9.7 bulunmuyorsa, mevcut dosyanın üzerine yazma. Bana durumu raporla ve resmî indirme kaynağını belirt.
5. Dosyaları silme, değiştirme veya başka konuma taşıma.

## Aşama 2 — Ghidra projesini otomatik oluştur
Yalnızca doğru referans sürümünü belirledikten sonra devam et.
1. Ayrı bir çalışma klasörü oluştur: C:\Users\Zeki\Documents\GPowerReverseEngineering
2. Ghidra'nın analyzeHeadless.bat aracını kullanarak yeni bir Ghidra projesi oluştur.
3. Doğru G*Power EXE dosyasını bu projeye içe aktar.
4. Ghidra'nın statik analizini çalıştır.
5. Orijinal EXE dosyasını değiştirme veya yeniden paketleme.
6. Analiz başarısız olursa hatayı kaydet; başarılıymış gibi davranma.

## Aşama 3 — İlgili davranışları araştır
Ödev kapsamımız:
- İki bağımsız grubun ortalamaları için t-testi.
- A priori örneklem büyüklüğü hesabı.
- Post hoc istatistiksel güç hesabı.
- Tek ve çift kuyruk seçenekleri.
- Etki büyüklüğü d, alfa, hedef güç ve grup oranı.
- Sonuçlarda örneklem sayıları, gerçekleşen güç, kritik değer, serbestlik derecesi ve noncentrality parameter.

Ghidra'nın ürettiği fonksiyonlar, stringler ve importlar arasından konuyla ilişkili olabilecekleri araştır. Her bulgunun hangi teknik kanıta dayandığını belirt. Kanıtlanmayan çıkarımları [AJAN] olarak etiketle. Yalnızca gerçekten gözlemlenmiş bulguları [REA] olarak kaydet.

## Aşama 4 — G*Power arayüzüyle referans sonuçları
G*Power arayüzünde iki bağımsız grup t-testini kullanarak gerçek sonuçlar üretmeye hazırlan. En az 30 referans vektörünü gerçek çalıştırmalarla oluştur.

## Aşama 5 — Dosyalar
- SPEC.md
- LEDGER.md
- oracle/
- prompts/inspection_session.md
- prompts/implementation_session.md
- HALLUCINATIONS.md
- AGENT_COST.md
```
