#!/usr/bin/env python3
"""
Tam otomatik Safari scraper - Herhangi bir galeri için çalışır
Kullanım: python3 full_auto_scraper.py <galeri_url> <sayfa_sayisi>
"""

import subprocess
import json
import time
import re
import sqlite3
import sys
from datetime import datetime

DB_PATH = '/Volumes/AS1000_Plus/galeri/galeri.db'

def run_applescript(script):
    """AppleScript çalıştır"""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def open_url_in_new_window(url):
    """Safari'de yeni pencerede URL aç"""
    script = f'''
    tell application "Safari"
        activate
        make new document with properties {{URL:"{url}"}}
    end tell
    '''
    run_applescript(script)

def open_url_in_new_tab(url):
    """Safari'de yeni sekmede URL aç"""
    script = f'''
    tell application "Safari"
        tell front window
            make new tab with properties {{URL:"{url}"}}
        end tell
    end tell
    '''
    run_applescript(script)

def get_tab_count():
    """Safari'deki sekme sayısını al"""
    script = '''
    tell application "Safari"
        tell front window
            return count of tabs
        end tell
    end tell
    '''
    try:
        return int(run_applescript(script))
    except:
        return 0

def run_js_in_tab(tab_index, js_code):
    """Belirli sekmede JavaScript çalıştır"""
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    
    script = f'''
    tell application "Safari"
        tell front window
            do JavaScript "{js_escaped}" in tab {tab_index}
        end tell
    end tell
    '''
    return run_applescript(script)

def run_js_in_current_tab(js_code):
    """Aktif sekmede JavaScript çalıştır"""
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    
    script = f'''
    tell application "Safari"
        tell front window
            do JavaScript "{js_escaped}" in current tab
        end tell
    end tell
    '''
    return run_applescript(script)

def get_listing_urls():
    """Galeri sayfasından ilan URL'lerini çek"""
    js_code = '''
    (function() {
        var links = [];
        document.querySelectorAll('a[href*="/ilan/"][href*="/detay"]').forEach(function(a) {
            var href = a.href;
            if(links.indexOf(href) === -1 && href.match(/\\d{9,}/)) {
                links.push(href);
            }
        });
        return JSON.stringify(links);
    })();
    '''
    result = run_js_in_current_tab(js_code)
    try:
        return json.loads(result)
    except:
        return []

def click_next_page():
    """Sonraki sayfa butonuna tıkla"""
    js_code = '''
    (function() {
        var next = document.querySelector('a[title="Sonraki"]:not(.passive), a.prevNextBut:not(.passive)');
        if(next) {
            next.click();
            return "clicked";
        }
        return "no_next";
    })();
    '''
    return run_js_in_current_tab(js_code)

def extract_data_from_tab(tab_index):
    """Sekmeden veri çek"""
    js_code = '''
    (function() {
        var data = {};
        document.querySelectorAll('ul.classifiedInfoList li, .classifiedInfo li').forEach(function(item) {
            var strong = item.querySelector('strong');
            var span = item.querySelector('span');
            if(strong && span) {
                var key = strong.innerText.replace(':', '').trim();
                var val = span.innerText.trim();
                if(key && val) data[key] = val;
            }
        });
        var priceEl = document.querySelector('.classifiedInfo h3');
        if(priceEl) data['Fiyat'] = priceEl.innerText.trim();
        var titleEl = document.querySelector('h1.classifiedDetailTitle');
        if(titleEl) data['Baslik'] = titleEl.innerText.trim();
        var match = location.href.match(/(\\d{9,})/);
        if(match) data['ilan_no'] = match[1];
        data['url'] = location.href;
        return JSON.stringify(data);
    })();
    '''
    result = run_js_in_tab(tab_index, js_code)
    try:
        return json.loads(result)
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python3 full_auto_scraper.py <galeri_url> [sayfa_sayisi]")
        print("Örnek: python3 full_auto_scraper.py https://yenikoymotors.sahibinden.com 3")
        return
    
    galeri_url = sys.argv[1]
    sayfa_sayisi = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print(f"🚀 Tam otomatik scraper başlıyor...")
    print(f"📂 Galeri: {galeri_url}")
    print(f"📄 Sayfa sayısı: {sayfa_sayisi}")
    print("=" * 50)
    
    # 1. Galeri sayfasını aç
    print("\n📂 Galeri sayfası açılıyor...")
    open_url_in_new_window(galeri_url)
    time.sleep(8)  # Cloudflare geçişi için bekle
    
    all_urls = []
    
    # 2. Her sayfadan URL'leri topla
    for sayfa in range(1, sayfa_sayisi + 1):
        print(f"\n📄 Sayfa {sayfa} işleniyor...")
        time.sleep(3)
        
        urls = get_listing_urls()
        print(f"   {len(urls)} ilan bulundu")
        all_urls.extend(urls)
        
        if sayfa < sayfa_sayisi:
            print("   Sonraki sayfaya geçiliyor...")
            click_next_page()
            time.sleep(4)
    
    # Tekrarları kaldır
    all_urls = list(set(all_urls))
    print(f"\n📊 Toplam {len(all_urls)} benzersiz ilan URL'si bulundu")
    
    # 3. Her ilanı yeni sekmede aç
    print("\n🔄 İlan sayfaları açılıyor...")
    for i, url in enumerate(all_urls):
        if (i + 1) % 10 == 0:
            print(f"   {i+1}/{len(all_urls)} açıldı...")
        open_url_in_new_tab(url)
        time.sleep(0.4)
    
    print(f"   ✅ {len(all_urls)} sekme açıldı")
    
    print("\n⏳ Sayfaların yüklenmesi bekleniyor (20 saniye)...")
    time.sleep(20)
    
    # 4. Her sekmeden veri çek
    print("\n📥 Veriler çekiliyor...")
    all_data = []
    tab_count = get_tab_count()
    
    for i in range(2, tab_count + 1):  # İlk sekme galeri sayfası
        if (i - 1) % 10 == 0:
            print(f"   {i-1}/{tab_count-1} sekme işlendi...")
        
        data = extract_data_from_tab(i)
        if data and data.get('ilan_no'):
            all_data.append(data)
        time.sleep(0.3)
    
    print(f"\n📊 Toplam {len(all_data)} ilan verisi çekildi!")
    
    # 5. Verileri kaydet
    output_file = f'/Volumes/AS1000_Plus/galeri/{galeri_url.split("//")[1].split(".")[0]}_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Veriler {output_file} dosyasına kaydedildi!")
    
    # 6. Veritabanını güncelle
    update_database(galeri_url, all_data)
    
    print("\n✅ İşlem tamamlandı!")
    
    # Özet göster
    print("\n" + "=" * 50)
    print("📊 ÖZET")
    print("=" * 50)
    for data in all_data[:10]:
        km = data.get('KM', '-')
        renk = data.get('Renk', '-')
        baslik = data.get('Baslik', 'Bilinmeyen')[:50]
        print(f"• {baslik}... | KM: {km} | Renk: {renk}")
    if len(all_data) > 10:
        print(f"... ve {len(all_data) - 10} ilan daha")

def update_database(galeri_url, data_list):
    """Veritabanını güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galeri ID'sini al
    galeri_name = galeri_url.split('//')[1].split('.')[0]
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE ?', (f'%{galeri_name}%',))
    result = cursor.fetchone()
    
    if not result:
        print(f"⚠️ Galeri bulunamadı, yeni ekleniyor: {galeri_url}")
        cursor.execute('INSERT INTO galeriler (galeri_url, galeri_adi) VALUES (?, ?)',
                       (galeri_url, galeri_name.upper()))
        galeri_id = cursor.lastrowid
    else:
        galeri_id = result[0]
    
    eklenen = 0
    guncellenen = 0
    
    for data in data_list:
        ilan_no = data.get('ilan_no')
        if not ilan_no:
            continue
        
        # KM
        km_str = data.get('KM', data.get('Kilometre', ''))
        km = None
        if km_str:
            km_clean = km_str.replace('.', '').replace(' ', '')
            km_match = re.search(r'(\d+)', km_clean)
            if km_match:
                km = int(km_match.group(1))
        
        # Renk
        renk = data.get('Renk', '')
        
        # Fiyat
        fiyat_str = data.get('Fiyat', '')
        fiyat = None
        if fiyat_str:
            fiyat_clean = re.sub(r'[^\d]', '', fiyat_str)
            if fiyat_clean:
                fiyat = int(fiyat_clean)
        
        # Başlık
        baslik = data.get('Baslik', '')
        
        # Yıl
        yil = data.get('Yıl', data.get('Model Yılı', ''))
        yil_int = None
        if yil:
            yil_match = re.search(r'(19|20)\d{2}', str(yil))
            if yil_match:
                yil_int = int(yil_match.group())
        
        # URL
        url = data.get('url', '')
        
        # Mevcut mı kontrol et
        cursor.execute('SELECT id FROM araclar WHERE ilan_no = ?', (ilan_no,))
        existing = cursor.fetchone()
        
        if existing:
            # Güncelle
            cursor.execute('''
                UPDATE araclar 
                SET km = ?, renk = ?, fiyat = ?, son_gorulme = ?, baslik = COALESCE(?, baslik)
                WHERE ilan_no = ?
            ''', (km, renk, fiyat, datetime.now(), baslik, ilan_no))
            guncellenen += 1
        else:
            # Yeni ekle
            cursor.execute('''
                INSERT INTO araclar (galeri_id, ilan_no, ilan_url, baslik, yil, fiyat, km, renk, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aktif')
            ''', (galeri_id, ilan_no, url, baslik, yil_int, fiyat, km, renk))
            eklenen += 1
    
    # Galeri son kontrol zamanını güncelle
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', 
                   (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Veritabanı güncellendi: {eklenen} yeni, {guncellenen} güncelleme")

if __name__ == '__main__':
    main()
