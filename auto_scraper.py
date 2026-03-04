#!/usr/bin/env python3
"""
Tam otomatik Safari scraper - Her şeyi otomatik yapar!
"""

import subprocess
import json
import time
import re
import sqlite3
from datetime import datetime

DB_PATH = '/Volumes/AS1000_Plus/galeri/galeri.db'
GALERI_URL = 'https://piranlarotomotiv.sahibinden.com'

def run_applescript(script):
    """AppleScript çalıştır"""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def open_url_in_safari(url):
    """Safari'de yeni sekmede URL aç"""
    script = f'''
    tell application "Safari"
        activate
        tell front window
            set newTab to make new tab with properties {{URL:"{url}"}}
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

def get_listing_urls_from_page(tab_index):
    """Galeri sayfasından ilan URL'lerini çek"""
    js_code = '''
    (function() {
        var links = [];
        document.querySelectorAll('a[href*="/ilan/"][href*="/detay"]').forEach(function(a) {
            if(links.indexOf(a.href) === -1) links.push(a.href);
        });
        return JSON.stringify(links);
    })();
    '''
    result = run_js_in_tab(tab_index, js_code)
    try:
        return json.loads(result)
    except:
        return []

def click_next_page(tab_index):
    """Sonraki sayfa butonuna tıkla"""
    js_code = '''
    (function() {
        var next = document.querySelector('a[title="Sonraki"], a.prevNextBut');
        if(next && !next.classList.contains('passive')) {
            next.click();
            return "clicked";
        }
        return "no_next";
    })();
    '''
    return run_js_in_tab(tab_index, js_code)

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

def wait_for_page_load(tab_index, timeout=15):
    """Sayfa yüklenene kadar bekle"""
    for _ in range(timeout * 2):
        js = 'document.readyState'
        result = run_js_in_tab(tab_index, js)
        if result == 'complete':
            return True
        time.sleep(0.5)
    return False

def main():
    print("🚀 Tam otomatik Safari scraper başlıyor...")
    print("=" * 50)
    
    # 1. Galeri sayfasını aç
    print("\n📂 Galeri sayfası açılıyor...")
    open_url_in_safari(GALERI_URL)
    time.sleep(5)  # Cloudflare geçişi için bekle
    
    # Galeri sekmesinin indexini bul (son sekme)
    galeri_tab = get_tab_count()
    print(f"   Galeri sekmesi: {galeri_tab}")
    
    # Sayfa yüklenene kadar bekle
    print("   Sayfa yükleniyor...")
    time.sleep(3)
    wait_for_page_load(galeri_tab)
    
    all_urls = []
    
    # 2. Sayfa 1'den URL'leri al
    print("\n📄 Sayfa 1 işleniyor...")
    urls = get_listing_urls_from_page(galeri_tab)
    print(f"   {len(urls)} ilan bulundu")
    all_urls.extend(urls)
    
    # 3. Sayfa 2'ye git
    print("\n📄 Sayfa 2'ye gidiliyor...")
    click_next_page(galeri_tab)
    time.sleep(4)
    wait_for_page_load(galeri_tab)
    
    urls2 = get_listing_urls_from_page(galeri_tab)
    print(f"   {len(urls2)} ilan bulundu")
    all_urls.extend(urls2)
    
    # Tekrarları kaldır
    all_urls = list(set(all_urls))
    print(f"\n📊 Toplam {len(all_urls)} benzersiz ilan URL'si")
    
    # 4. Her ilanı yeni sekmede aç
    print("\n🔄 İlan sayfaları açılıyor...")
    for i, url in enumerate(all_urls):
        print(f"   {i+1}/{len(all_urls)} açılıyor...")
        open_url_in_safari(url)
        time.sleep(0.5)  # Spam yapmamak için
    
    print("\n⏳ Sayfaların yüklenmesi bekleniyor (15 saniye)...")
    time.sleep(15)
    
    # 5. Her sekmeden veri çek
    print("\n📥 Veriler çekiliyor...")
    all_data = []
    tab_count = get_tab_count()
    
    for i in range(galeri_tab, tab_count + 1):
        print(f"   Sekme {i}/{tab_count}...")
        data = extract_data_from_tab(i)
        if data and data.get('ilan_no'):
            all_data.append(data)
            km = data.get('KM', '-')
            print(f"      ✅ {data.get('ilan_no')} - KM: {km}")
        time.sleep(0.3)
    
    # 6. Verileri kaydet
    print(f"\n📊 Toplam {len(all_data)} ilan verisi çekildi!")
    
    with open('/Volumes/AS1000_Plus/galeri/safari_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # 7. Veritabanını güncelle
    update_database(all_data)
    
    print("\n✅ İşlem tamamlandı!")

def update_database(data_list):
    """Veritabanını güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE "%piranlar%"')
    result = cursor.fetchone()
    if not result:
        print("❌ Galeri bulunamadı!")
        return
    
    galeri_id = result[0]
    guncellenen = 0
    
    for data in data_list:
        ilan_no = data.get('ilan_no')
        if not ilan_no:
            continue
        
        km_str = data.get('KM', '')
        km = None
        if km_str:
            km_clean = km_str.replace('.', '').replace(' ', '')
            km_match = re.search(r'(\d+)', km_clean)
            if km_match:
                km = int(km_match.group(1))
        
        renk = data.get('Renk', '')
        
        cursor.execute('''
            UPDATE araclar SET km = ?, renk = ?, son_gorulme = ?
            WHERE ilan_no = ?
        ''', (km, renk, datetime.now(), ilan_no))
        
        if cursor.rowcount > 0:
            guncellenen += 1
    
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', 
                   (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ {guncellenen} ilan veritabanında güncellendi!")

if __name__ == '__main__':
    main()
