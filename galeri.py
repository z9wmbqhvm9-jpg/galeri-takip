#!/usr/bin/env python3
"""
Sahibinden Galeri Takip Sistemi
- Galeri hesaplarından araç ilanlarını çeker
- Satılan araçları tespit eder
- Fiyat değişikliklerini takip eder
- Her 3 saatte otomatik kontrol yapar
"""

import sqlite3
from datetime import datetime
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Veritabanı dosyası
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'galeri.db')


def get_driver():
    """Chrome driver oluştur"""
    options = Options()
    # Headless modda Cloudflare daha çok engelliyor, görünür modda başlat
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    # Bot tespitini engelle
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver


def init_database():
    """Veritabanını oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galeriler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS galeriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            galeri_url TEXT UNIQUE NOT NULL,
            galeri_adi TEXT,
            eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            son_kontrol TIMESTAMP
        )
    ''')
    
    # Araçlar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS araclar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            galeri_id INTEGER,
            ilan_no TEXT UNIQUE,
            ilan_url TEXT,
            baslik TEXT,
            marka TEXT,
            model TEXT,
            yil INTEGER,
            kilometre TEXT,
            yakit TEXT,
            vites TEXT,
            renk TEXT,
            fiyat INTEGER,
            fiyat_text TEXT,
            resim_url TEXT,
            ilan_tarihi TEXT,
            ilk_gorulme TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            son_gorulme TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            durum TEXT DEFAULT 'aktif',
            FOREIGN KEY (galeri_id) REFERENCES galeriler(id)
        )
    ''')
    
    # Fiyat geçmişi tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiyat_gecmisi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arac_id INTEGER,
            eski_fiyat INTEGER,
            yeni_fiyat INTEGER,
            degisim_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (arac_id) REFERENCES araclar(id)
        )
    ''')
    
    # Kontrol logları
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kontrol_loglari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            galeri_id INTEGER,
            kontrol_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            toplam_ilan INTEGER,
            yeni_ilan INTEGER,
            satilan_ilan INTEGER,
            fiyat_degisen INTEGER,
            FOREIGN KEY (galeri_id) REFERENCES galeriler(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır!")


def galeri_ekle(galeri_url):
    """Yeni galeri ekle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT OR IGNORE INTO galeriler (galeri_url) VALUES (?)', (galeri_url,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Galeri eklendi: {galeri_url}")
        else:
            print(f"ℹ️ Galeri zaten mevcut: {galeri_url}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        conn.close()


def ilanlari_cek(galeri_url):
    """Selenium ile galeri sayfasından ilanları çek"""
    
    print(f"🌐 Tarayıcı başlatılıyor...")
    driver = get_driver()
    
    tum_ilanlar = []
    
    try:
        print(f"📡 Sayfa yükleniyor: {galeri_url}")
        driver.get(galeri_url)
        
        # Cloudflare challenge bekle
        print("⏳ Sayfa yükleniyor...")
        time.sleep(5)
        
        # Cloudflare challenge varsa bekle
        max_bekle = 30
        bekle = 0
        while bekle < max_bekle:
            if 'challenge' in driver.page_source.lower() or 'cloudflare' in driver.page_source.lower():
                print(f"⏳ Cloudflare kontrolü bekleniyor... ({bekle}s)")
                time.sleep(2)
                bekle += 2
            else:
                break
        
        # Cookie popup varsa kapat
        try:
            cookie_btn = driver.find_element(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
            cookie_btn.click()
            time.sleep(1)
        except:
            pass
        
        sayfa = 1
        while True:
            print(f"📄 Sayfa {sayfa} işleniyor...")
            
            # Sayfanın yüklenmesini bekle
            time.sleep(3)
            
            # İlan satırlarını bul - farklı seçiciler dene
            ilan_satirlari = []
            
            # Seçici 1: data-id ile
            ilan_satirlari = driver.find_elements(By.CSS_SELECTOR, 'tr[data-id]')
            
            if not ilan_satirlari:
                # Seçici 2: searchResultsItem class
                ilan_satirlari = driver.find_elements(By.CSS_SELECTOR, 'tr.searchResultsItem')
            
            if not ilan_satirlari:
                # Seçici 3: Tablo içindeki satırlar
                ilan_satirlari = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr:not(.searchResultsPromo498):not(.native-empty)')
            
            if not ilan_satirlari:
                # Seçici 4: Liste görünümü
                ilan_satirlari = driver.find_elements(By.CSS_SELECTOR, '.classified-list tr')
                
            if not ilan_satirlari:
                # Seçici 5: Galeri profil sayfası için
                ilan_satirlari = driver.find_elements(By.CSS_SELECTOR, '.classified-list-item, .searchResultsRow')
            
            print(f"   {len(ilan_satirlari)} ilan satırı bulundu")
            
            for satir in ilan_satirlari:
                try:
                    ilan = parse_ilan(satir)
                    if ilan and ilan.get('ilan_no'):
                        tum_ilanlar.append(ilan)
                except Exception as e:
                    continue
            
            # Sonraki sayfa var mı?
            try:
                sonraki_btn = driver.find_element(By.CSS_SELECTOR, 'a.prevNextBut[title="Sonraki"], a[title="Sonraki"]')
                if 'disabled' in sonraki_btn.get_attribute('class') or not sonraki_btn.is_enabled():
                    break
                sonraki_btn.click()
                time.sleep(4)
                sayfa += 1
            except:
                break
            
            if sayfa > 20:  # Maksimum sayfa limiti
                break
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("🌐 Tarayıcı kapatıldı")
    
    return tum_ilanlar


def parse_ilan(satir):
    """Selenium elementi parse et"""
    ilan = {}
    
    try:
        # İlan numarası
        ilan_no = satir.get_attribute('data-id')
        if not ilan_no:
            # Link'ten çek
            try:
                link = satir.find_element(By.CSS_SELECTOR, 'a[href*="/ilan/"]')
                href = link.get_attribute('href')
                match = re.search(r'/ilan/(\d+)', href)
                if match:
                    ilan_no = match.group(1)
            except:
                pass
        
        if not ilan_no:
            return None
            
        ilan['ilan_no'] = ilan_no
        
        # İlan URL
        try:
            link = satir.find_element(By.CSS_SELECTOR, 'a[href*="/ilan/"]')
            href = link.get_attribute('href')
            ilan['ilan_url'] = href if href.startswith('http') else f"https://www.sahibinden.com{href}"
        except:
            ilan['ilan_url'] = f"https://www.sahibinden.com/ilan/{ilan_no}"
        
        # Başlık
        try:
            baslik_elem = satir.find_element(By.CSS_SELECTOR, 'td.title a, .classifiedTitle, a.classifiedTitle')
            ilan['baslik'] = baslik_elem.text.strip()
        except:
            try:
                baslik_elem = satir.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a')
                ilan['baslik'] = baslik_elem.text.strip()
            except:
                pass
        
        # Fiyat
        try:
            fiyat_elem = satir.find_element(By.CSS_SELECTOR, 'td.price, .price, .searchResultsPriceValue')
            fiyat_text = fiyat_elem.text.strip()
            ilan['fiyat_text'] = fiyat_text
            fiyat_sayi = re.sub(r'[^\d]', '', fiyat_text)
            if fiyat_sayi:
                ilan['fiyat'] = int(fiyat_sayi)
        except:
            pass
        
        # Resim
        try:
            resim = satir.find_element(By.CSS_SELECTOR, 'img')
            ilan['resim_url'] = resim.get_attribute('src') or resim.get_attribute('data-src')
        except:
            pass
        
        # Tüm hücreleri al
        try:
            hucreler = satir.find_elements(By.CSS_SELECTOR, 'td')
            for hucre in hucreler:
                text = hucre.text.strip()
                
                # Renk (genellikle 3. hücre)
                if text and len(text) < 15 and not ilan.get('renk'):
                    if text.lower() in ['beyaz', 'siyah', 'gri', 'mavi', 'kırmızı', 'lacivert', 'gümüş', 'bordo', 'yeşil', 'kahverengi', 'bej', 'turuncu', 'sarı', 'mor', 'pembe', 'füme', 'şampanya', 'turkuaz', 'altın']:
                        ilan['renk'] = text
        except:
            pass
        
        # İlan tarihi (genellikle son hücre)
        try:
            tarih_elem = satir.find_element(By.CSS_SELECTOR, 'td:last-child')
            tarih_text = tarih_elem.text.strip()
            if '/' in tarih_text or 'Bugün' in tarih_text or 'Dün' in tarih_text:
                ilan['ilan_tarihi'] = tarih_text
        except:
            pass
        
        # Yıl ve diğer bilgileri başlıktan parse et
        baslik = ilan.get('baslik', '')
        
        # Yıl (4 haneli sayı)
        yil_match = re.search(r'\b(19|20)\d{2}\b', baslik)
        if yil_match:
            ilan['yil'] = int(yil_match.group())
        
        return ilan
        
    except Exception as e:
        return None


def galeri_kontrol(galeri_id, galeri_url):
    """Bir galeriyi kontrol et ve değişiklikleri kaydet"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n🔍 Galeri kontrol ediliyor: {galeri_url}")
    print("=" * 60)
    
    # İlanları çek
    tum_ilanlar = ilanlari_cek(galeri_url)
    
    print(f"📊 Toplam {len(tum_ilanlar)} ilan bulundu")
    
    if len(tum_ilanlar) == 0:
        print("⚠️ İlan bulunamadı! Sayfa yapısı değişmiş olabilir.")
        conn.close()
        return {'toplam': 0, 'yeni': 0, 'satilan': 0, 'fiyat_degisen': 0}
    
    # Mevcut aktif ilanları al
    cursor.execute('''
        SELECT ilan_no, fiyat FROM araclar 
        WHERE galeri_id = ? AND durum = 'aktif'
    ''', (galeri_id,))
    mevcut_ilanlar = {row[0]: row[1] for row in cursor.fetchall()}
    
    yeni_ilan_sayisi = 0
    fiyat_degisen_sayisi = 0
    
    # Yeni ilanları işle
    bulunan_ilan_nolari = set()
    
    for ilan in tum_ilanlar:
        ilan_no = ilan.get('ilan_no')
        if not ilan_no:
            continue
            
        bulunan_ilan_nolari.add(ilan_no)
        
        if ilan_no in mevcut_ilanlar:
            # Mevcut ilan - fiyat değişimi kontrol et
            eski_fiyat = mevcut_ilanlar[ilan_no]
            yeni_fiyat = ilan.get('fiyat')
            
            if eski_fiyat and yeni_fiyat and eski_fiyat != yeni_fiyat:
                # Fiyat değişti!
                cursor.execute('''
                    UPDATE araclar SET fiyat = ?, fiyat_text = ?, son_gorulme = ?
                    WHERE ilan_no = ?
                ''', (yeni_fiyat, ilan.get('fiyat_text'), datetime.now(), ilan_no))
                
                # Fiyat geçmişine kaydet
                cursor.execute('SELECT id FROM araclar WHERE ilan_no = ?', (ilan_no,))
                arac_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    INSERT INTO fiyat_gecmisi (arac_id, eski_fiyat, yeni_fiyat)
                    VALUES (?, ?, ?)
                ''', (arac_id, eski_fiyat, yeni_fiyat))
                
                degisim = yeni_fiyat - eski_fiyat
                yuzde = (degisim / eski_fiyat) * 100
                emoji = "📈" if degisim > 0 else "📉"
                print(f"{emoji} Fiyat değişti: {ilan.get('baslik', ilan_no)[:50]}")
                print(f"   {eski_fiyat:,} TL → {yeni_fiyat:,} TL ({yuzde:+.1f}%)")
                
                fiyat_degisen_sayisi += 1
            else:
                # Sadece son görülme güncelle
                cursor.execute('''
                    UPDATE araclar SET son_gorulme = ? WHERE ilan_no = ?
                ''', (datetime.now(), ilan_no))
        else:
            # Yeni ilan!
            cursor.execute('''
                INSERT INTO araclar 
                (galeri_id, ilan_no, ilan_url, baslik, yil, kilometre, yakit, vites, renk, fiyat, fiyat_text, resim_url, ilan_tarihi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                galeri_id,
                ilan_no,
                ilan.get('ilan_url'),
                ilan.get('baslik'),
                ilan.get('yil'),
                ilan.get('kilometre'),
                ilan.get('yakit'),
                ilan.get('vites'),
                ilan.get('renk'),
                ilan.get('fiyat'),
                ilan.get('fiyat_text'),
                ilan.get('resim_url'),
                ilan.get('ilan_tarihi')
            ))
            
            print(f"🆕 Yeni ilan: {ilan.get('baslik', ilan_no)[:60]} - {ilan.get('fiyat_text', 'Fiyat yok')}")
            yeni_ilan_sayisi += 1
    
    # Satılan araçları tespit et
    satilan_sayisi = 0
    for ilan_no in mevcut_ilanlar:
        if ilan_no not in bulunan_ilan_nolari:
            cursor.execute('''
                UPDATE araclar SET durum = 'satildi', son_gorulme = ?
                WHERE ilan_no = ?
            ''', (datetime.now(), ilan_no))
            
            cursor.execute('SELECT baslik, fiyat_text FROM araclar WHERE ilan_no = ?', (ilan_no,))
            satilan = cursor.fetchone()
            if satilan:
                print(f"🏷️ SATILDI: {satilan[0][:50]} - {satilan[1]}")
            satilan_sayisi += 1
    
    # Galeri son kontrol zamanını güncelle
    cursor.execute('''
        UPDATE galeriler SET son_kontrol = ? WHERE id = ?
    ''', (datetime.now(), galeri_id))
    
    # Log kaydet
    cursor.execute('''
        INSERT INTO kontrol_loglari (galeri_id, toplam_ilan, yeni_ilan, satilan_ilan, fiyat_degisen)
        VALUES (?, ?, ?, ?, ?)
    ''', (galeri_id, len(tum_ilanlar), yeni_ilan_sayisi, satilan_sayisi, fiyat_degisen_sayisi))
    
    conn.commit()
    conn.close()
    
    print(f"\n📈 Özet: {yeni_ilan_sayisi} yeni, {satilan_sayisi} satıldı, {fiyat_degisen_sayisi} fiyat değişti")
    return {
        'toplam': len(tum_ilanlar),
        'yeni': yeni_ilan_sayisi,
        'satilan': satilan_sayisi,
        'fiyat_degisen': fiyat_degisen_sayisi
    }


def tum_galerileri_kontrol():
    """Tüm kayıtlı galerileri kontrol et"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, galeri_url, galeri_adi FROM galeriler')
    galeriler = cursor.fetchall()
    conn.close()
    
    if not galeriler:
        print("⚠️ Henüz galeri eklenmemiş. Önce galeri ekleyin:")
        print("   python galeri.py ekle <galeri_url>")
        return
    
    print(f"\n🚗 {len(galeriler)} galeri kontrol edilecek...")
    print(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for galeri_id, galeri_url, galeri_adi in galeriler:
        galeri_kontrol(galeri_id, galeri_url)
        time.sleep(5)  # Galeriler arası bekleme
    
    print(f"\n✅ Tüm kontroller tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def rapor_goster():
    """Mevcut durumu raporla"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 GALERİ TAKİP RAPORU")
    print("=" * 60)
    
    # Galeriler
    cursor.execute('SELECT id, galeri_url, son_kontrol FROM galeriler')
    galeriler = cursor.fetchall()
    
    for galeri_id, url, son_kontrol in galeriler:
        print(f"\n🏪 Galeri: {url}")
        print(f"   Son kontrol: {son_kontrol or 'Henüz kontrol edilmedi'}")
        
        # Aktif ilanlar
        cursor.execute('SELECT COUNT(*) FROM araclar WHERE galeri_id = ? AND durum = "aktif"', (galeri_id,))
        aktif = cursor.fetchone()[0]
        
        # Satılan ilanlar
        cursor.execute('SELECT COUNT(*) FROM araclar WHERE galeri_id = ? AND durum = "satildi"', (galeri_id,))
        satilan = cursor.fetchone()[0]
        
        print(f"   📗 Aktif ilanlar: {aktif}")
        print(f"   📕 Satılan araçlar: {satilan}")
    
    # Son satılanlar
    print("\n" + "-" * 60)
    print("🏷️ SON SATILAN ARAÇLAR (Son 10)")
    print("-" * 60)
    
    cursor.execute('''
        SELECT baslik, fiyat_text, son_gorulme FROM araclar 
        WHERE durum = 'satildi' 
        ORDER BY son_gorulme DESC LIMIT 10
    ''')
    
    satirlar = cursor.fetchall()
    if satirlar:
        for baslik, fiyat, tarih in satirlar:
            print(f"  • {baslik[:50]} - {fiyat} ({tarih})")
    else:
        print("  Henüz satılan araç yok")
    
    # Son fiyat değişimleri
    print("\n" + "-" * 60)
    print("💰 SON FİYAT DEĞİŞİMLERİ (Son 10)")
    print("-" * 60)
    
    cursor.execute('''
        SELECT a.baslik, f.eski_fiyat, f.yeni_fiyat, f.degisim_tarihi
        FROM fiyat_gecmisi f
        JOIN araclar a ON f.arac_id = a.id
        ORDER BY f.degisim_tarihi DESC LIMIT 10
    ''')
    
    satirlar = cursor.fetchall()
    if satirlar:
        for baslik, eski, yeni, tarih in satirlar:
            degisim = yeni - eski
            emoji = "📈" if degisim > 0 else "📉"
            print(f"  {emoji} {baslik[:45]}")
            print(f"     {eski:,} TL → {yeni:,} TL ({degisim:+,} TL)")
    else:
        print("  Henüz fiyat değişimi yok")
    
    conn.close()


def aktif_ilanlari_listele():
    """Aktif ilanları listele"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📋 AKTİF İLANLAR")
    print("=" * 60)
    
    cursor.execute('''
        SELECT baslik, yil, kilometre, renk, fiyat_text, ilan_url
        FROM araclar WHERE durum = 'aktif'
        ORDER BY fiyat DESC
    ''')
    
    ilanlar = cursor.fetchall()
    
    if ilanlar:
        for i, (baslik, yil, km, renk, fiyat, url) in enumerate(ilanlar, 1):
            print(f"\n{i}. {baslik}")
            print(f"   Yıl: {yil or '-'} | KM: {km or '-'} | Renk: {renk or '-'}")
            print(f"   💰 {fiyat}")
            print(f"   🔗 {url}")
    else:
        print("  Henüz aktif ilan yok")
    
    conn.close()


def main():
    """Ana fonksiyon"""
    import sys
    
    init_database()
    
    if len(sys.argv) < 2:
        print("""
🚗 Sahibinden Galeri Takip Sistemi
==================================

Kullanım:
  python galeri.py ekle <galeri_url>    - Yeni galeri ekle
  python galeri.py kontrol              - Tüm galerileri kontrol et
  python galeri.py rapor                - Rapor göster
  python galeri.py liste                - Aktif ilanları listele
  python galeri.py daemon               - Arka planda sürekli çalış (3 saat arayla)

Örnek:
  python galeri.py ekle "https://piranlarotomotiv.sahibinden.com"
  python galeri.py kontrol
        """)
        return
    
    komut = sys.argv[1].lower()
    
    if komut == 'ekle' and len(sys.argv) >= 3:
        galeri_url = sys.argv[2]
        galeri_ekle(galeri_url)
        print("💡 İpucu: 'python galeri.py kontrol' ile ilk taramayı başlatın")
        
    elif komut == 'kontrol':
        tum_galerileri_kontrol()
        
    elif komut == 'rapor':
        rapor_goster()
        
    elif komut == 'liste':
        aktif_ilanlari_listele()
        
    elif komut == 'daemon':
        print("🔄 Daemon modu başlatıldı (Her 3 saatte kontrol)")
        print("   Durdurmak için: Ctrl+C")
        
        while True:
            try:
                tum_galerileri_kontrol()
                print(f"\n⏰ Sonraki kontrol: 3 saat sonra")
                print("   Bekleniyor...")
                time.sleep(3 * 60 * 60)  # 3 saat
            except KeyboardInterrupt:
                print("\n👋 Daemon durduruldu.")
                break
    else:
        print(f"❌ Bilinmeyen komut: {komut}")
        print("   Yardım için: python galeri.py")


if __name__ == '__main__':
    main()
