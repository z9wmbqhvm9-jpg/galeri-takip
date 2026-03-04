# 🚗 GALERİ TAKİP SİSTEMİ - KULLANIM KILAVUZU

## 📊 SİSTEM DURUMU

✅ **Tüm sistemler çalışıyor ve hazır!**

---

## 🎯 HIZLI BAŞLATMA

### 1️⃣ Dashboard'u Aç (Bilgisayar + Telefon)
```
Çift tıkla: tam_baslat.bat
```
- ✅ Dashboard otomatik açılır
- ✅ API sunucusu başlar
- ✅ Telefon erişimi aktif

**Adresler:**
- 💻 Bilgisayar: `http://localhost:8080/advanced_dashboard.html`
- 📱 Telefon: `http://192.168.1.103:8080/advanced_dashboard.html`

### 2️⃣ Sistemi Kapat
```
Çift tıkla: dashboard_stop.bat
```
Hem dashboard hem API sunucusu kapanır.

---

## 🤖 BOT KULLANIMI

### İlk Kez Bot Çalıştırma
```
Çift tıkla: run_selenium_bot.bat
```

**Bot ne yapar?**
- ✅ Günde maksimum 8 ilan kontrol eder
- ✅ 22 ilan → 3 günde tamamlanır
- ✅ Chrome görünür modda açılır (ilk test için)
- ✅ İnsan gibi davranır (60-180 saniye bekleme)
- ✅ Satılan ilanları tespit eder
- ✅ Log tutar: `ad_check_log.txt`

### Otomatik Çalıştırma (Görev Zamanlayıcı)
1. **Win + R** → `taskschd.msc`
2. **Temel Görev Oluştur**
3. İsim: "Galeri Bot"
4. Tetikleyici: **Günlük**
5. Program: `run_selenium_bot.bat` dosyasını seç
6. **Rastgele geciktirme: 2 saat**
7. Tamam!

🎯 **Bot artık her gün otomatik çalışır!**

---

## 🎨 DASHBOARD ÖZELLİKLERİ

### Ana Ekran
- 📊 4 İstatistik Kartı
  - Toplam İlan
  - Aktif İlan
  - Satılan İlan
  - Ortalama Fiyat

- 📈 4 Grafiği
  - Marka Dağılımı (Pasta)
  - Fiyat Aralığı (Bar)
  - Yıl Dağılımı (Bar)
  - Durum (Doughnut)

### Filtreler
- 🔍 Arama (Marka, Model, Galeri)
- 🚗 Marka
- 📅 Yıl
- 💰 Fiyat Aralığı (Min-Max)
- ✅ Durum (Aktif/Satıldı)

### Tablo
**Sütunlar:**
- İlan No
- Marka
- Model
- Yıl
- Motor
- Paket
- Vites
- Renk
- KM
- Fiyat
- Galeri
- Hasar (Detay butonu)
- Durum
- İşlem

### Butonlar
- 🔴 **Satıldı** butonu → Aracı satıldı olarak işaretle
- 🟢 **Aktif** butonu → Satılmış aracı tekrar aktif yap
- 📄 **Hasar Detay** → Boyalı/Değişen parçalar
- 🔗 **İlanı Aç** → Sahibinden.com'da görüntüle
- 📊 **Excel'e Aktar** → CSV olarak indir

---

## 📁 DOSYA YAPISI

### Ana Dosyalar
- `advanced_dashboard.html` → Dashboard
- `cars_data.json` → 22 araç verisi
- `galeri_takip.db` → SQLite veritabanı
- `api_server.py` → API sunucusu

### Batch Dosyaları
- `tam_baslat.bat` → Dashboard + API başlat
- `dashboard_stop.bat` → Tümünü kapat
- `run_selenium_bot.bat` → Bot çalıştır

### Bot Dosyaları
- `check_ads_selenium.py` → Selenium bot
- `bot_state.json` → Bot durumu (otomatik oluşur)
- `ad_check_log.txt` → Bot log dosyası

---

## 🔄 GÜNLÜK KULLANIM

### Sabah Rutini
1. `tam_baslat.bat` çalıştır
2. Dashboard'u kontrol et
3. Yeni ilanları incele

### Araç Satınca
1. Dashboard'da aracı bul
2. **Satıldı** butonuna tıkla
3. Otomatik güncellenir

### Bot Kontrol
1. `ad_check_log.txt` dosyasını aç
2. Son kontrolü gör
3. Durum: `bot_state.json`

---

## 📱 TELEFON İÇİN

### Aynı WiFi'de İseniz
```
http://192.168.1.103:8080/advanced_dashboard.html
```

### Firewall Açma (Gerekirse)
1. **Windows Güvenlik Duvarı** → Gelişmiş ayarlar
2. **Gelen Kurallar** → Yeni Kural
3. Port → TCP → 8080
4. Bağlantıya izin ver
5. İsim: "Dashboard"

---

## 🛠️ SORUN GİDERME

### Dashboard Açılmıyor
```
dashboard_stop.bat → Kapat
tam_baslat.bat → Tekrar başlat
```

### Satıldı Butonu Çalışmıyor
```
API sunucusu çalışıyor mu kontrol et:
netstat -ano | findstr ":5000"
```

### Bot Hata Veriyor
```
ad_check_log.txt dosyasına bak
Chrome güncel mi kontrol et
```

### Veri Güncellenmiyor
```
F5 ile sayfayı yenile
Tarayıcı cache'ini temizle (Ctrl+Shift+Del)
```

---

## 🎯 PERİYODİK BAKIM

### Günlük
- ✅ Bot loglarını kontrol et
- ✅ Satılan araçları işaretle

### Haftalık
- ✅ Veritabanı yedeği al (`galeri_takip.db`)
- ✅ JSON yedeği al (`cars_data.json`)

### Aylık
- ✅ Eski ilanları temizle
- ✅ Bot performansını incele

---

## 📞 DESTEK

### Log Dosyaları
- `ad_check_log.txt` → Bot logları
- `bot_state.json` → Bot durumu

### Kontrol Komutları
```powershell
# Sunucu durumu
netstat -ano | findstr ":8080"
netstat -ano | findstr ":5000"

# Veritabanı boyutu
dir galeri_takip.db

# Araç sayısı
python -c "import json; print(len(json.load(open('cars_data.json'))['vehicles']))"
```

---

## ✅ BAŞARILI KULLANIM!

Şu anda:
- ✅ 22 araç takip ediliyor
- ✅ Dashboard aktif
- ✅ API çalışıyor
- ✅ Bot hazır
- ✅ Telefon erişimi açık

**Her şey hazır! İyi çalışmalar! 🚀**
