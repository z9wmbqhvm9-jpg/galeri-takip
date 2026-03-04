# 🚗 Galeri Takip Sistemi

Sahibinden.com galerilerini otomatik takip eden sistem.

## 📁 Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `baslat.bat` | Windows için çift tıkla başlat |
| `chrome_scraper.py` | Chrome tabanlı veri çekici |
| `dashboard.html` | Görsel dashboard |
| `galeri.db` | Veritabanı |
| `all_data.json` | Çekilen veriler |

## 🚀 Windows'ta Kullanım

### 1. Gereksinimler
- Python 3.x yüklü olmalı
- Google Chrome yüklü olmalı

### 2. Çalıştırma
```
baslat.bat
```
dosyasına çift tıklayın.

### 3. Cloudflare
- Açılan Chrome'da Cloudflare kontrolü gelirse **ELLE** geçin
- Script otomatik olarak devam edecek

## 📊 Dashboard

`dashboard.html` dosyasını tarayıcıda açın:
- **Kart Görünümü**: Filtrelenebilir araç kartları
- **Marka Bazlı**: BMW, Mercedes, Audi vb. gruplandırılmış
- **Tablo**: Fiyata göre sıralı liste
- **Zaman Çizelgesi**: En yeni ve en eski ilanlar

## 🔧 Galeriler

Varsayılan galeriler:
- Piranlar Otomotiv (2 sayfa)
- Yeniköy Motors (3 sayfa)

Yeni galeri eklemek için `chrome_scraper.py` dosyasında `GALERILER` listesini düzenleyin:
```python
GALERILER = [
    ('https://piranlarotomotiv.sahibinden.com', 2),
    ('https://yenikoymotors.sahibinden.com', 3),
    ('https://yenigaleri.sahibinden.com', 1),  # Yeni galeri
]
```

## 📱 Özellikler

- ✅ Fiyat takibi
- ✅ KM takibi
- ✅ Yeni ilan tespiti
- ✅ Satılan araç tespiti
- ✅ Marka bazlı görüntüleme
- ✅ Modern dark mode dashboard
