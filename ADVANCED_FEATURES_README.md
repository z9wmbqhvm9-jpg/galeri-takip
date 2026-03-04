# 🚀 Gelişmiş Özellikler - Profesyonel Galeri Takip Sistemi

## 📊 Yeni Özellikler

### 1. 🗃️ Veritabanı Sistemi (SQLite)

#### Özellikler
✅ **Geçmiş Takibi** - Tüm kontrol kayıtları saklanır
✅ **Fiyat Trendleri** - Fiyat değişiklikleri takip edilir
✅ **Durum Geçmişi** - Her ilanın aktif/satıldı geçmişi
✅ **Günlük Snapshot** - Günlük istatistikler kaydedilir
✅ **CSV Export** - Tüm veriyi Excel'e aktar

#### Veritabanı Tabloları

**vehicles**: Araç temel bilgileri
- id, ad_no, brand, model, year, engine, transmission, fuel_type, body_type, color, km, gallery, region, ad_url

**price_history**: Fiyat geçmişi
- ad_no, price, currency, recorded_at

**status_history**: Durum geçmişi
- ad_no, status (active/sold/uncertain), check_date, note

**daily_snapshots**: Günlük özet
- snapshot_date, total_ads, active_ads, sold_ads, avg_price, min_price, max_price

#### Kurulum

```bash
# 1. Veritabanını başlat
setup_database.bat

# 2. Manuel başlatma
python database.py
```

#### Kullanım

```python
from database import GaleriDatabase

# Veritabanını aç
db = GaleriDatabase()

# JSON'dan veri import et
db.import_from_json('cars_data.json')

# İstatistikleri al
stats = db.get_statistics()
print(f"Toplam: {stats['total_vehicles']}")
print(f"Aktif: {stats['active_ads']}")
print(f"Ortalama Fiyat: {stats['avg_price']}")

# Bir ilanın fiyat geçmişi
history = db.get_price_history('1302004975')
for record in history:
    print(f"{record['recorded_at']}: {record['price']} TL")

# Fiyat değişikliklerini analiz et
changes = db.get_price_changes('1302004975')
if changes:
    print(f"İlk fiyat: {changes['first_price']}")
    print(f"Son fiyat: {changes['last_price']}")
    print(f"Değişim: %{changes['change_percent']:.2f}")

# Son 7 günlük trendler
trends = db.get_trend_data(7)
for trend in trends:
    print(f"{trend['snapshot_date']}: {trend['active_ads']} aktif")

# CSV'ye export et
db.export_to_csv('rapor.csv')

# Bağlantıyı kapat
db.close()
```

### 2. 📊 Gelişmiş Dashboard

#### Özellikler
✅ **İnteraktif Grafikler** - Chart.js ile gerçek zamanlı grafikler
✅ **Gelişmiş Filtreleme** - Marka, yıl, fiyat aralığı, durum, arama
✅ **Sıralama** - Herhangi bir kolona göre artan/azalan sıralama
✅ **Excel Export** - Filtrelenmiş veriyi CSV'ye aktar
✅ **Responsive Tasarım** - Mobil uyumlu
✅ **Gerçek Zamanlı İstatistikler** - Toplam, aktif, satılan, ortalama fiyat

#### Dashboard Bileşenleri

**İstatistik Kartları**:
- 📊 Toplam İlan Sayısı
- ✅ Aktif İlan Sayısı
- ❌ Satılan İlan Sayısı
- 💰 Ortalama Fiyat

**Grafikler**:
1. **Marka Dağılımı** (Pasta grafik)
   - Her markadan kaç araç var
   - Renk kodlu görselleştirme

2. **Fiyat Dağılımı** (Bar grafik)
   - 0-500K, 500K-1M, 1M-1.5M, 1.5M-2M, 2M+
   - Fiyat aralıklarına göre araç sayısı

3. **Yıl Dağılımı** (Bar grafik)
   - Her yıldan kaç araç var
   - Kronolojik sıralama

4. **Durum Dağılımı** (Donut grafik)
   - Aktif vs Satılan
   - Yüzdelik görünüm

**Filtreler**:
- 🔍 **Arama**: Marka, model, galeri, bölge
- 🏷️ **Marka Filtresi**: Dropdown
- 📅 **Yıl Filtresi**: Dropdown
- 💰 **Fiyat Aralığı**: Min-Max input
- ✅ **Durum**: Aktif/Satıldı/Tümü

**Tablo**:
- Sıralanabilir kolonlar
- Filtrelenebilir satırlar
- Direkt ilan linkler
- Durum badge'leri (renkli)
- Hover efektleri

#### Kullanım

```bash
# 1. Dashboard'u aç
advanced_dashboard.html

# Tarayıcıda otomatik açılır
# Veya manuel:
# - Chrome'da: Dosyaya sağ tık → "Open with Chrome"
# - Edge'de: Dosyaya sağ tık → "Open with Edge"
```

#### Kısayol Tuşları
- **Enter**: Arama yap (arama kutusunda)
- **Tablo başlığına tıkla**: Sırala

#### Özellikler

**Dinamik Filtreleme**:
```javascript
// Örnek: 500K-1M arası Toyota araçlar
Marka: Toyota
Min Fiyat: 500000
Max Fiyat: 1000000
[Filtrele] butonu
```

**Excel Export**:
```javascript
// Filtrelenmiş veriyi CSV'ye aktar
[Excel'e Aktar] butonu

// Oluşturulan dosya:
galeri_takip_2026-02-25.csv
```

**Sıfırlama**:
```javascript
// Tüm filtreleri temizle
[Sıfırla] butonu
```

### 3. 🤖 Bot & Veritabanı Entegrasyonu

#### Özellikler
✅ **Otomatik Kayıt** - Her kontrol DB'ye kaydedilir
✅ **Fiyat Takibi** - Fiyat değişiklikleri kaydedilir
✅ **Durum Takibi** - Aktif/satıldı durumları kaydedilir
✅ **Günlük Snapshot** - Bot her çalıştığında snapshot alır

#### Bot Çalıştırma

```bash
# Selenium bot (DB entegreli)
run_selenium_bot.bat
```

Bot otomatik olarak:
1. Veritabanını başlatır (yoksa)
2. Her ilan için durum kaydı ekler
3. Fiyat bilgisi kaydeder
4. Bot bittiğinde günlük snapshot alır

#### Log Çıktısı

```
🤖 GELİŞMİŞ İLAN KONTROL BOTU (GÜVENLİ MOD)
✅ Veritabanı bağlantısı kuruldu
📊 Günlük Limit: Maksimum 8 ilan

[1/8] 🔍 Kontrol ediliyor: İlan No 1302004975
   ✅ Aktif - İlan yayında
   💾 Veritabanına kaydedildi

[2/8] 🔍 Kontrol ediliyor: İlan No 1300736113
   ❌ Satılmış/Kaldırılmış
   💾 Satış kaydı eklendi

...

✅ KONTROL TAMAMLANDI
📊 Bugün: 8/8 | Aktif: 7 | Satıldı: 1
💾 Günlük snapshot kaydedildi
🔒 Veritabanı bağlantısı kapandı
```

## 📈 Veri Analizi Örnekleri

### 1. Fiyat Trendi Analizi

```python
from database import GaleriDatabase

db = GaleriDatabase()

# Son 30 günlük trend
trends = db.get_trend_data(30)

for trend in trends:
    print(f"{trend['snapshot_date']}")
    print(f"  Aktif: {trend['active_ads']}")
    print(f"  Satılan: {trend['sold_ads']}")
    print(f"  Ort. Fiyat: {trend['avg_price']:,.0f} TL")
```

### 2. Bir İlanın Tam Geçmişi

```python
ad_no = '1302004975'

# Fiyat geçmişi
price_history = db.get_price_history(ad_no)
print(f"Fiyat değişimleri:")
for record in price_history:
    print(f"  {record['recorded_at']}: {record['price']:,} TL")

# Durum geçmişi
status_history = db.get_status_history(ad_no)
print(f"\nDurum değişimleri:")
for record in status_history:
    print(f"  {record['check_date']}: {record['status']} - {record['note']}")

# Fiyat değişim analizi
changes = db.get_price_changes(ad_no)
if changes:
    print(f"\nFiyat Analizi:")
    print(f"  İlk: {changes['first_price']:,} TL")
    print(f"  Son: {changes['last_price']:,} TL")
    print(f"  Değişim: {changes['change']:,} TL ({changes['change_percent']:.1f}%)")
```

### 3. Genel İstatistikler

```python
stats = db.get_statistics()

print("📊 GENEL İSTATİSTİKLER")
print("=" * 50)
print(f"Toplam Araç: {stats['total_vehicles']}")
print(f"Aktif İlanlar: {stats['active_ads']}")
print(f"Satılan İlanlar: {stats['sold_ads']}")
print(f"Ortalama Fiyat: {stats['avg_price']:,.2f} TL")
print("=" * 50)
```

## 🎯 Kullanım Senaryoları

### Senaryo 1: Günlük Takip

```bash
# Sabah 10:00
1. setup_database.bat (ilk kez)
2. run_selenium_bot.bat
3. advanced_dashboard.html aç
4. İstatistikleri kontrol et
```

### Senaryo 2: Haftalık Analiz

```python
# Haftalık rapor
db = GaleriDatabase()

# Son 7 günlük veriler
trends = db.get_trend_data(7)

print("📊 HAFTALIK RAPOR")
for trend in trends:
    print(f"{trend['snapshot_date']}: "
          f"{trend['active_ads']} aktif, "
          f"{trend['sold_ads']} satıldı, "
          f"Ort: {trend['avg_price']:,.0f} TL")

# CSV'ye aktar
db.export_to_csv('haftalik_rapor.csv')
```

### Senaryo 3: Fiyat Değişimi Alarm

```python
# Fiyatı düşen ilanları bul
db = GaleriDatabase()

for vehicle_id in ['1302004975', '1300736113', ...]:
    changes = db.get_price_changes(vehicle_id)
    
    if changes and changes['change_percent'] < -5:
        print(f"🔔 ALARM: İlan {vehicle_id}")
        print(f"   Fiyat %{abs(changes['change_percent']):.1f} düştü!")
        print(f"   {changes['first_price']:,} TL → {changes['last_price']:,} TL")
```

## 📁 Dosya Yapısı

```
galeritakip-main/
├── 📊 DASHBOARD
│   ├── dashboard_table.html         # Basit dashboard (eski)
│   └── advanced_dashboard.html      # Gelişmiş dashboard (YENİ) ⭐
│
├── 🗃️ VERİTABANI
│   ├── database.py                  # Veritabanı yönetimi (YENİ) ⭐
│   ├── galeri_takip.db             # SQLite dosyası (otomatik oluşur)
│   └── setup_database.bat          # Kolay kurulum (YENİ) ⭐
│
├── 🤖 BOTLAR
│   ├── check_ads_selenium.py       # Gelişmiş bot (DB entegreli) ⭐
│   ├── check_ads_daily.py          # Basit bot (requests)
│   └── run_selenium_bot.bat        # Kolay çalıştırma
│
├── 📄 VERİ
│   ├── cars_data.json              # 22 araç verisi
│   ├── ad_check_log.txt            # Bot logları
│   └── bot_state.json              # Bot durumu
│
└── 📚 DOKÜMANTASYON
    ├── README.md
    ├── SELENIUM_BOT_README.md
    ├── QUICKSTART_SELENIUM.md
    └── ADVANCED_FEATURES_README.md # Bu dosya ⭐
```

## 🚀 Hızlı Başlangıç

### 1. İlk Kurulum

```bash
# Veritabanını başlat
setup_database.bat

# Bot'u çalıştır
run_selenium_bot.bat

# Dashboard'u aç
advanced_dashboard.html
```

### 2. Günlük Kullanım

```bash
# Her gün otomatik çalışacak şekilde ayarla
# Windows Görev Zamanlayıcı:
# 1. Win + R → taskschd.msc
# 2. Temel Görev Oluştur
# 3. Program: run_selenium_bot.bat
# 4. Günlük, saat 10:00
```

### 3. Dashboard'u Kontrol Et

```
advanced_dashboard.html → Çift tıkla

Göreceklerin:
✅ İstatistik kartları
✅ 4 interaktif grafik
✅ Filtreleme sistemi
✅ Sıralanabilir tablo
✅ Excel export butonu
```

## 💡 Pro İpuçları

### 1. Veritabanı Yedekleme

```bash
# Günlük yedek
copy galeri_takip.db backups\galeri_takip_%date%.db

# Veya Python ile
import shutil
from datetime import datetime

backup_name = f"galeri_takip_{datetime.now().strftime('%Y%m%d')}.db"
shutil.copy2('galeri_takip.db', f'backups/{backup_name}')
```

### 2. Toplu CSV Export

```python
from database import GaleriDatabase

db = GaleriDatabase()

# Tüm veriyi export et
db.export_to_csv('rapor_tum.csv')

# Sadece aktif ilanları export et (SQL ile)
db.cursor.execute("""
    SELECT v.*, 
           (SELECT price FROM price_history WHERE ad_no = v.ad_no 
            ORDER BY recorded_at DESC LIMIT 1) as current_price
    FROM vehicles v
    WHERE (SELECT status FROM status_history WHERE ad_no = v.ad_no 
           ORDER BY check_date DESC LIMIT 1) = 'active'
""")

# CSV olarak kaydet...
```

### 3. Dashboard Özelleştirme

```javascript
// advanced_dashboard.html içinde

// Fiyat aralıklarını özelleştir
const priceRanges = {
    '0-300K': 0,
    '300K-600K': 0,
    '600K-1M': 0,
    '1M+': 0
};

// Grafik renklerini değiştir
const customColors = [
    '#FF6384', '#36A2EB', '#FFCE56', 
    '#4BC0C0', '#9966FF', '#FF9F40'
];
```

### 4. Otomatik Raporlama

```python
# Her hafta Pazar akşamı çalışacak rapor scripti
from database import GaleriDatabase
from datetime import datetime

db = GaleriDatabase()

# Son 7 günlük trend
trends = db.get_trend_data(7)

# Rapor oluştur
report = f"""
HAFTALIK RAPOR - {datetime.now().strftime('%Y-%m-%d')}
{'='*50}

ÖZET:
"""

for trend in trends:
    report += f"\n{trend['snapshot_date']}: "
    report += f"{trend['active_ads']} aktif, {trend['sold_ads']} satıldı"

# Dosyaya kaydet
with open(f"rapor_{datetime.now().strftime('%Y%m%d')}.txt", 'w', encoding='utf-8') as f:
    f.write(report)

print("✅ Haftalık rapor oluşturuldu")
```

## ⚙️ Ayarlar

### Günlük Limit Değiştirme

```python
# check_ads_selenium.py satır 221
bot = SmartAdChecker(headless=headless, max_ads_per_day=8)

# 5 ilan/gün yapmak için:
bot = SmartAdChecker(headless=headless, max_ads_per_day=5)

# Tüm ilanları kontrol etmek için (RİSKLİ):
bot = SmartAdChecker(headless=headless, max_ads_per_day=999)
```

### Dashboard Tema Renkleri

```css
/* advanced_dashboard.html içinde */

body {
    /* Gradient değiştir */
    background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
}

.header h1 {
    color: #FF6B6B; /* Ana renk */
}
```

## 🔧 Sorun Giderme

### Veritabanı Hataları

```bash
# Problem: "database is locked"
# Çözüm: Bot çalışırken database.py çalıştırma

# Problem: "no such table"
# Çözüm: Veritabanını yeniden başlat
del galeri_takip.db
python database.py
```

### Dashboard Görünmüyor

```bash
# Problem: Grafikler yüklenmiyor
# Çözüm: İnternet bağlantısını kontrol et (Chart.js CDN için gerekli)

# Problem: Veriler eski
# Çözüm: Tarayıcı cache'ini temizle (Ctrl+Shift+Delete)
```

### Bot DB'ye Kaydetmiyor

```bash
# Problem: "⚠️ Veritabanı başlatılamadı"
# Çözüm: 
python database.py  # Manuel başlat
python check_ads_selenium.py  # Tekrar dene
```

## 📊 Performans

- **Veritabanı**: ~1MB (22 araç + 30 gün geçmiş)
- **Dashboard**: Anında yükleme (<1 saniye)
- **Bot**: ~20 dakika (8 ilan + günlük limit)
- **CSV Export**: <1 saniye

## 🎉 Sonuç

Artık profesyonel bir galeri takip sisteminiz var:

✅ **Veritabanı** - Geçmiş takibi, trend analizi
✅ **Gelişmiş Dashboard** - Grafikler, filtreler, export
✅ **Bot Entegrasyonu** - Otomatik kayıt
✅ **Güvenlik** - Günlük limit, anti-detection
✅ **Raporlama** - CSV export, haftalık rapor

**Başarılar!** 🚀
