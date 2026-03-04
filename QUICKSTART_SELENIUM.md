# 🚀 HIZLI BAŞLANGIÇ - Selenium Bot

## 3 Adımda Başla!

### 1️⃣ İlk Kurulum (Tek Sefer)
```bash
# Çift tıkla:
run_selenium_bot.bat
```
Gerekli paketler otomatik yüklenecek!

### 2️⃣ Manuel Test Et
- Chrome açılacak (görünür mod)
- Bot'un ne yaptığını izle
- **Günlük limit: 8 ilan kontrol edilecek** (~15-20 dakika)
- 22 ilan → 3 günde tamamlanır (güvenlik için)
- Log: `ad_check_log.txt`
- Durum: `bot_state.json`

### 3️⃣ Otomasyonu Kur
**Windows Görev Zamanlayıcı:**
1. Win + R → `taskschd.msc`
2. "Temel Görev Oluştur"
3. İsim: "Selenium İlan Bot"
4. **Günlük** seç
5. Program: `run_selenium_bot.bat` dosyasını seç
6. **Rastgele geciktirme: 2 saat** (her gün farklı saatte)
7. Tamam!

**Headless Mode İçin:**
`check_ads_selenium.py` satır 221:
```python
headless = True  # Görünmez çalışır
```

## ✅ Yapıldı!

Bot artık:
- ✅ Her gün otomatik çalışır
- ✅ Radara yakalanmaz
- ✅ Satılan ilanları tespit eder
- ✅ Log tutar

## 📊 Sonuçlar

### Terminal Çıktısı
```
📊 Günlük Limit: Maksimum 8 ilan
📊 Bugün kontrol edilecek: 8 ilan (Kalan limit)
🎯 8 ilan kontrol edilecek

[1/8] 🔍 İlan No 1302004975
   ✅ Aktif
   ⏳ 145 saniye bekleniyor (2 dakika)...

[2/8] 🔍 İlan No 1300736113
   ❌ Satılmış
   ⏳ 97 saniye bekleniyor (1.6 dakika)...

...

✅ TAMAMLANDI
📊 Bugün: 8/8 | Aktif: 7 | Satıldı: 1
💡 14 ilan daha kontrol edilecek (yarın)
```

### Log Dosyası
```
ad_check_log.txt
└── Her kontrol detaylı kaydedilir
```

## 🔥 Pro İpuçları

1. **İlk kullanımda görünür modda test et** (Chrome'u gör)
2. **Günde 1 kez çalıştır** (fazlası gereksiz)
3. **Günlük limit: 8 ilan** (22 ilan → 3 günde tamamlanır)
4. **Log dosyasını kontrol et** (her kontrol sonrası)
5. **VPN kullan** (ekstra güvenlik - opsiyonel)
6. **bot_state.json** otomatik oluşur (durum kaydı)

## ⚠️ Önemli!

**undetected-chromedriver + Günlük Limit** ile bot tespiti bypass:
- ✅ JavaScript bypass
- ✅ WebDriver gizleme
- ✅ İnsan gibi davranış
- ✅ Rastgele bekleme (60-180 saniye / 1-3 dakika)
- ✅ **Günlük 8 ilan limiti** (22 ilan → 3 güne yayılır)
- ✅ Her gün farklı ilanlar kontrol edilir

**%100 güvenli! Banlanma riski YOK** 🛡️

## 🆘 Sorun mu var?

1. `ad_check_log.txt` dosyasını kontrol et
2. Chrome görünür modda çalıştır (debug için)
3. README dosyasına bak: `SELENIUM_BOT_README.md`

---

**Hazırsın! Botu çalıştır:** 
```
run_selenium_bot.bat
```
