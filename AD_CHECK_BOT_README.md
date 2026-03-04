# İlan Kontrol Botu - Kullanım Kılavuzu

## Özellikler

✅ **Güvenli kontrol**: İnsan gibi davranır, radara yakalanmaz
✅ **Rastgele bekleme**: İlanlar arası 30-120 saniye rastgele bekler
✅ **Farklı User-Agent**: Her isteğe farklı tarayıcı kimliği
✅ **Detaylı log**: Tüm kontroller `ad_check_log.txt` dosyasına kaydedilir
✅ **Otomatik çalıştırma**: Windows Task Scheduler ile günlük çalışır

## Manuel Kullanım

### 1. Tek seferlik çalıştırma
```bash
python check_ads_daily.py
```

veya

```bash
run_ad_check.bat
```

### 2. Sonuçları görüntüle
Kontrol tamamlandıktan sonra:
- Terminalden özet göreceksin
- Detaylı log: `ad_check_log.txt` dosyasında

## Otomatik Çalıştırma (Windows Task Scheduler)

### Adım 1: Task Scheduler'ı Aç
1. Windows Arama'ya `Görev Zamanlayıcı` veya `Task Scheduler` yaz
2. Uygulamayı aç

### Adım 2: Yeni Görev Oluştur
1. Sağ taraftan **"Temel Görev Oluştur"** tıkla
2. **Ad**: "İlan Kontrol Botu"
3. **Açıklama**: "Sahibinden ilanlarını günlük kontrol eder"
4. **İleri** tıkla

### Adım 3: Tetikleyici Ayarla
1. **"Günlük"** seç, İleri
2. **Başlangıç**: Bugünün tarihi
3. **Her**: 1 gün
4. **İleri** tıkla

### Adım 4: Eylem Ayarla
1. **"Program başlat"** seç, İleri
2. **Program/betik**: 
   ```
   C:\Users\batuh\OneDrive\Masaüstü\galeritakip-main\run_ad_check.bat
   ```
3. **Başlangıç konumu**: 
   ```
   C:\Users\batuh\OneDrive\Masaüstü\galeritakip-main
   ```
4. **İleri**, **Son**

### Adım 5: Gelişmiş Ayarlar (Opsiyonel)
1. Oluşturulan görevi sağ tıkla → **Özellikler**
2. **Tetikleyiciler** sekmesinde:
   - **Rastgele geciktirme**: 2 saat (her gün farklı saatte çalışsın)
3. **Koşullar** sekmesinde:
   - "Bilgisayar AC güç kaynağındaysa görev başlat" → Kapat
4. **Tamam** tıkla

## Güvenlik İpuçları

🔒 **Radara Yakalanmama Stratejileri:**

1. **Günde 1 kez çalıştır** - Fazla sık kontrol etme
2. **Rastgele saatte çalışsın** - Task Scheduler'da "rastgele geciktirme" aktif
3. **Yavaş ol** - Script zaten ilanlar arası 30-120 saniye bekliyor
4. **VPN kullan** (opsiyonel) - Farklı IP'den bağlan

## Log Dosyası

`ad_check_log.txt` örnek içerik:
```
[2026-02-25 14:32:10] İlan No: 1302004975 - Durum: AKTIF - İlan hala yayında
[2026-02-25 14:33:45] İlan No: 1302030245 - Durum: AKTIF - İlan hala yayında
[2026-02-25 14:35:20] İlan No: 1300736113 - Durum: SATILDI - İlan kaldırılmış
[2026-02-25 15:12:05] İlan No: ÖZET - Durum: TAMAMLANDI - Toplam: 22, Aktif: 21, Satıldı: 1, Hata: 0
```

## Sorun Giderme

### "ModuleNotFoundError: No module named 'requests'"
```bash
.venv\Scripts\activate
pip install requests
```

### Bot çok yavaş
- Normal! İlanlar arası 30-120 saniye bekliyor (radara yakalanmamak için)
- Hızlandırmak istersen `check_ads_daily.py` dosyasında `random.randint(30, 120)` değerlerini düşür
  - Örnek: `random.randint(10, 30)` (ama daha riskli)

### Task Scheduler çalışmıyor
1. Task'a sağ tıkla → Çalıştır (manuel test et)
2. "En son çalıştırma sonucu" sütununa bak
3. Hata varsa log dosyasını kontrol et

## Gelişmiş Özellikler (İleride)

Şu anki bot basit bir requests kullanıyor. Daha güvenli için:

1. **Selenium kullan** - Gerçek browser açar (daha yavaş ama çok güvenli)
2. **Proxy rotation** - Her isteğe farklı IP
3. **Email bildirimi** - Satılmış ilan bulunca mail at
4. **Dashboard entegrasyonu** - Satılan ilanları otomatik "Satıldı" olarak işaretle

İhtiyacın olursa bunları da ekleyebiliriz!
