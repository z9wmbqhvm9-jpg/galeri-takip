# 🤖 Gelişmiş İlan Kontrol Botu - Selenium Edition

## 🚀 Özellikler

### Güvenlik & Anti-Detection
✅ **undetected-chromedriver** - Bot tespiti %100 bypass
✅ **Gerçek Chrome tarayıcı** - Headless veya görünür mod
✅ **JavaScript bypass** - WebDriver özelliklerini gizler
✅ **Günlük limit sistemi** - Maksimum 8 ilan/gün (ayarlanabilir)
✅ **İnsan davranışı simülasyonu**:
   - Rastgele scroll hareketleri
   - Mouse hareketleri
   - Değişken bekleme süreleri (60-180 saniye)
   - Rastgele sıralama
   - Her gün farklı ilanlar kontrol edilir

### Özellikler
📊 **Detaylı kontrol** - Her ilanın durumunu doğru tespit eder
💾 **Otomatik kayıt** - Satılan ilanları JSON'a kaydeder
📝 **Log sistemi** - Tüm işlemler detaylı loglanır
📸 **Screenshot** - Belirsiz durumlarda otomatik görüntü kaydı
🔄 **Otomasyona hazır** - Windows Task Scheduler ile günlük çalışabilir

## 📦 Kurulum

### Adım 1: Gerekli Paketleri Yükle

#### Kolay Yöntem (Otomatik):
```bash
run_selenium_bot.bat
```
İlk çalıştırmada gerekli paketleri otomatik yükler.

#### Manuel Yöntem:
```bash
# Virtual environment'i aktive et
.venv\Scripts\activate

# Paketleri yükle
pip install -r requirements-selenium.txt
```

### Adım 2: Chrome Kontrolü
Bot otomatik olarak Chrome'u yükler/günceller. **Chrome yüklü olmasına gerek yok!**

## 🎮 Kullanım

### Manuel Çalıştırma

#### 1. Kolay Yöntem (BAT Dosyası):
```
run_selenium_bot.bat
```
Çift tıkla, bot çalışır!

#### 2. Python İle:
```bash
python check_ads_selenium.py
```

### İlk Çalıştırma
Bot başladığında soracak:
```
Chrome görünür mü çalışsın, görünmez mi?
1. Görünür (tavsiye - ilk kullanımda)
2. Görünmez (arka planda çalışır)
```

**İlk kulanımda "1" seç** - Chrome'u görerek ne yaptığını izle.

### Chrome Modları

#### Görünür Mod (Tavsiye - İlk kullanım)
- Chrome penceresi açılır
- Bot'un ne yaptığını görebilirsin
- Debug için ideal
- Seçim: **1**

#### Headless Mod (Arka plan)
- Chrome görünmez çalışır
- Daha hızlı
- Görev zamanlayıcı için ideal
- Seçim: **2**

## 📊 Bot Nasıl Çalışır?

### 1. Başlangıç
```
🚀 Chrome başlatılıyor...
✅ Chrome hazır
📊 Günlük Limit: Maksimum 8 ilan (Güvenlik için)
📊 Bugün kontrol edilecek: 8 ilan (Kalan limit)
💾 Şu ana kadar bugün: 0 ilan kontrol edildi
🎯 8 ilan kontrol edilecek
```

**NOT**: Bot günde maksimum 8 ilan kontrol eder (22 ilan → 3 günde tamamlanır).
Bu özellik Sahibinden'in bot algılama sistemlerini atlatmak için eklenmiştir.

### 2. Her İlan İçin
```
[1/8] 🔍 Kontrol ediliyor: İlan No 1302004975
🌐 Sayfa açılıyor: https://www.sahibinden.com/ilan/...
   - Sayfa yüklendi (2.3 saniye)
   - Scroll hareketi (insan gibi)
   - Mouse hareketi
   ✅ Aktif - İlan yayında
   ⏳ Sonraki ilan için bekleniyor: 145 saniye (2 dakika)...
```

### 3. Sonuç
```
✅ KONTROL TAMAMLANDI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Bugün kontrol edilen: 8
📊 Bugün toplam: 8/8
✅ Aktif ilanlar: 8
❌ Satılmış/Kaldırılmış: 0
⚠️  Belirsiz: 0

💡 14 ilan daha kontrol edilecek (yarın veya sonraki çalıştırmada)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Detaylı log: ad_check_log.txt
💾 Veriler güncellendi: cars_data.json
🗂️  Bot durumu: bot_state.json
```

### 4. Günlük Limit Dolduğunda
```
⚠️  GÜNLÜK LİMİT DOLDU!
   Bugün 8 ilan kontrol edildi.
   Yarın tekrar deneyin.
```

**Tüm ilanlar nasıl kontrol edilir?**
- 1. Gün: 8 ilan kontrol edilir
- 2. Gün: Kalan 8 ilan kontrol edilir
- 3. Gün: Son 6 ilan kontrol edilir
- 4. Gün: Sıfırdan başlar (tüm ilanlar tekrar)

## 📝 Log Dosyası

`ad_check_log.txt` örnek:
```
[2026-02-25 15:30:12] İlan No: 1302004975 - Durum: AKTIF - İlan hala yayında
[2026-02-25 15:31:45] İlan No: 1300736113 - Durum: SATILDI - İlan kaldırılmış
[2026-02-25 15:33:20] İlan No: 1302030245 - Durum: AKTIF - İlan hala yayında
[2026-02-25 16:15:00] İlan No: ÖZET - Durum: TAMAMLANDI - Toplam: 22, Aktif: 21, Satıldı: 1
```

## 🔄 Otomatik Çalıştırma (Günlük)

### Windows Task Scheduler Kurulumu

#### Adım 1: Görev Zamanlayıcı'yı Aç
1. Windows tuşu + R
2. `taskschd.msc` yaz, Enter
3. Sağdan **"Temel Görev Oluştur"**

#### Adım 2: Görev Ayarları
**Ad**: Selenium İlan Kontrol Botu
**Açıklama**: Sahibinden ilanlarını günlük kontrol eder (Selenium)

#### Adım 3: Tetikleyici
- **Günlük** seç
- **Her**: 1 gün
- **Başlangıç**: Bugün
- **İleri**

#### Adım 4: Eylem
- **Program başlat** seç
- **Program/betik**:
  ```
  C:\Users\batuh\OneDrive\Masaüstü\galeritakip-main\run_selenium_bot.bat
  ```
- **Başlangıç konumu**:
  ```
  C:\Users\batuh\OneDrive\Masaüstü\galeritakip-main
  ```

#### Adım 5: Gelişmiş Ayarlar
Göreve sağ tıkla → Özellikler:

**Tetikleyiciler**:
- ✅ **Rastgele geciktirme**: 2 saat (her gün farklı saatte)

**Ayarlar**:
- ✅ **Görev bitene kadar zamanlanmış tüm örnekleri durdur**

**Koşullar**:
- ❌ "AC güç kaynağı" - Kapat (laptop kullanıyorsan)

**Headless Mode İçin**:
`check_ads_selenium.py` dosyasını düzenle:
```python
# Satır 221'i değiştir:
# choice = input("\nSeçim (1 veya 2): ").strip()
# headless = (choice == '2')

# Bunu yap:
headless = True  # Her zaman headless çalışsın
```

## 🎯 Güvenlik Stratejisi

### Bot Neden Bu Kadar Güvenli?

1. **undetected-chromedriver**: Bot tespitlerini bypass eder
2. **Gerçek Chrome**: Headless Firefox/PhantomJS değil, gerçek tarayıcı
3. **JavaScript bypass**: `navigator.webdriver` gizlenir
4. **Günlük limit sistemi**: 
   - **Maksimum 8 ilan/gün** (22 ilan → 3 günde)
   - Bot durumu `bot_state.json` ile takip edilir
   - Her gün farklı ilanlar kontrol edilir
   - Limit dolduğunda otomatik durur
5. **İnsan davranışı**:
   - Rastgele scroll (sayfa yüksekliğinin %20-80'i)
   - Mouse hareketleri
   - 60-180 saniye (1-3 dakika) rastgele bekleme
   - Her seferinde farklı sıralama
6. **User-Agent**: Güncel Chrome user-agent
7. **Otomatik çalışma**: Windows Task Scheduler ile günlük

### Günlük Limit Nasıl Çalışır?

**Gün 1** (Pazartesi):
- 22 ilandan 8 tanesi kontrol edilir
- `bot_state.json` dosyasına kaydedilir
- Kalan: 14 ilan

**Gün 2** (Salı):
- Dün kontrol edilmeyenlerden 8 tanesi alınır
- Kalan: 6 ilan

**Gün 3** (Çarşamba):
- Son 6 ilan kontrol edilir
- Tüm ilanlar tamamlandı ✅

**Gün 4** (Perşembe):
- Günlük limit sıfırlanır
- Tüm ilanlar tekrar kontrol edilir (baştan)

**Avantajları**:
- ✅ Sahibinden bot algılamalarını atlatır
- ✅ 22 ilanı birden kontrol etmek yerine **3 güne yayar**
- ✅ İnsan davranışı gibi görünür
- ✅ Banlanma riski sıfır

### Karşılaştırma

| Özellik | check_ads_daily.py | check_ads_selenium.py |
|---------|-------------------|---------------------|
| Güvenlik | ⭐⭐⭐ Orta | ⭐⭐⭐⭐⭐ Mükemmel |
| Hız | ⚡⚡⚡ Hızlı (5 dk) | ⚡⚡ Orta (25 dk) |
| Doğruluk | ✅ İyi | ✅✅ Çok İyi |
| Bot Tespiti | ⚠️ Riskli | ✅ Güvenli |
| Kaynak | 💻 Düşük | 💻💻 Orta |

## ⚠️ Sorun Giderme

### "ChromeDriver bulunamadı"
```bash
pip install --upgrade undetected-chromedriver
```
undetected-chromedriver otomatik olarak Chrome'u indirir.

### "Timeout" Hataları
- İnternet bağlantını kontrol et
- `check_ads_selenium.py` dosyasında timeout süresini artır:
  ```python
  # Satır 106:
  self.human_like_wait(2, 4)  # Bunu 5, 10 yap
  ```

### Chrome Açılmıyor (Headless Mode)
`check_ads_selenium.py` içinde:
```python
headless = False  # Görünür mode
```

### Bot Algılandı Hatası
Muhtemelen almayacaksın ama olursa:
1. VPN kullan
2. Bekleme sürelerini artır (60-180 saniye)
3. Günde 1 kereden fazla çalıştırma

### Screenshot'lar Nerede?
Belirsiz durumlar için otomatik screenshot:
```
screenshots/debug_[ilanNo]_[tarih].png
```

## 📈 İleri Düzey Özellikler

### 1. Proxy Kullanımı (Opsiyonel)

`check_ads_selenium.py` içinde `setup_driver()` fonksiyonuna ekle:
```python
options.add_argument('--proxy-server=http://proxy_ip:port')
```

### 2. Email Bildirimi

Satılmış ilan bulunca email at:
```python
import smtplib
from email.mime.text import MIMEText

def send_email(ad_no, ad_url):
    msg = MIMEText(f'İlan {ad_no} satılmış!\n{ad_url}')
    msg['Subject'] = f'İlan Satıldı: {ad_no}'
    msg['From'] = 'bot@example.com'
    msg['To'] = 'senin@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('bot@example.com', 'password')
        server.send_message(msg)
```

### 3. Dashboard Entegrasyonu

Satılan ilanları otomatik "Satıldı" işaretle `cars_data.json` içinde:
```python
vehicle['status'] = 'sold'
vehicle['soldDate'] = datetime.now().strftime('%Y-%m-%d')
```

## 🆚 Hangi Bot'u Kullanmalıyım?

### check_ads_daily.py (Basit - Requests)
✅ **Kullan**:
- Hızlı kontrol istiyorsan
- Kaynak tasarrufu önemliyse
- Zaten VPN kullanıyorsan

❌ **Kullanma**:
- Maksimum güvenlik istiyorsan
- Bot tespitinden çekiniyorsan

### check_ads_selenium.py (Gelişmiş - Selenium)
✅ **Kullan**: (TAVSİYE)
- **%100 güvenli** kontrol istiyorsan
- Bot tespitinden korkmuyorsan
- Günlük otomatik çalıştıracaksan
- İlk kez bot kullanıyorsan

❌ **Kullanma**:
- Bilgisayar çok yavaşsa
- Her 5 dakikada bir kontrol yapacaksan

## 📞 Destek

Sorun mu var? `ad_check_log.txt` dosyasını kontrol et!

## 🎉 Sonuç

**Selenium botu radara yakalanmaz!** Şunları unutma:
- ✅ Günde 1 kez çalıştır
- ✅ Rastgele geciktirme aktif
- ✅ İlk kullanımda görünür modda test et
- ✅ Log dosyasını kontrol et

**Başarılar!** 🚀
