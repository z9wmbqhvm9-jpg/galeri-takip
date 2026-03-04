#!/usr/bin/env python3
"""
Safari üzerinden otomatik veri çekme
AppleScript kullanarak Safari sekmelerini kontrol eder
"""

import subprocess
import json
import time
import re
import sqlite3
from datetime import datetime

DB_PATH = '/Volumes/AS1000_Plus/galeri/galeri.db'

def run_applescript(script):
    """AppleScript çalıştır"""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def get_tab_count():
    """Safari'deki sekme sayısını al"""
    script = '''
    tell application "Safari"
        tell front window
            return count of tabs
        end tell
    end tell
    '''
    return int(run_applescript(script))

def get_tab_url(tab_index):
    """Belirli sekmenin URL'sini al"""
    script = f'''
    tell application "Safari"
        tell front window
            return URL of tab {tab_index}
        end tell
    end tell
    '''
    return run_applescript(script)

def run_js_in_tab(tab_index, js_code):
    """Belirli sekmede JavaScript çalıştır"""
    # JavaScript'i escape et
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    script = f'''
    tell application "Safari"
        tell front window
            do JavaScript "{js_escaped}" in tab {tab_index}
        end tell
    end tell
    '''
    return run_applescript(script)

def extract_data_from_tab(tab_index):
    """Sekmeden veri çek"""
    js_code = '''
    (function() {
        var data = {};
        var items = document.querySelectorAll('ul.classifiedInfoList li, table tr, .classifiedInfo li');
        items.forEach(function(item) {
            var strong = item.querySelector('strong');
            var span = item.querySelector('span');
            if(strong && span) {
                var key = strong.innerText.replace(':', '').trim();
                var val = span.innerText.trim();
                if(key && val) data[key] = val;
            }
        });
        
        // Fiyat
        var priceEl = document.querySelector('.classifiedInfo h3, [class*="price"]');
        if(priceEl) data['Fiyat'] = priceEl.innerText.trim();
        
        // Başlık
        var titleEl = document.querySelector('h1.classifiedDetailTitle, .classifiedDetailTitle');
        if(titleEl) data['Baslik'] = titleEl.innerText.trim();
        
        // İlan no - URL'den
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
    print("🚀 Safari'den veri çekme başlıyor...")
    
    tab_count = get_tab_count()
    print(f"📑 {tab_count} sekme bulundu")
    
    all_data = []
    
    for i in range(1, tab_count + 1):
        url = get_tab_url(i)
        
        # Sadece ilan detay sayfalarını işle
        if '/ilan/' not in url or '/detay' not in url:
            print(f"⏭️  Sekme {i}: İlan değil, atlanıyor")
            continue
        
        print(f"📄 Sekme {i}/{tab_count} işleniyor...")
        
        data = extract_data_from_tab(i)
        if data and data.get('ilan_no'):
            all_data.append(data)
            km = data.get('KM', data.get('Kilometre', '-'))
            print(f"   ✅ {data.get('ilan_no')} - KM: {km}")
        else:
            print(f"   ⚠️ Veri alınamadı")
        
        time.sleep(0.3)  # Çok hızlı gitmeyelim
    
    print(f"\n📊 Toplam {len(all_data)} ilan verisi çekildi!")
    
    # JSON olarak kaydet
    with open('/Volumes/AS1000_Plus/galeri/safari_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("💾 Veriler safari_data.json dosyasına kaydedildi!")
    
    # Veritabanını güncelle
    if all_data:
        update_database(all_data)

def update_database(data_list):
    """Veritabanını güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galeri ID'sini al
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
        
        # KM bilgisini al
        km_str = data.get('KM', data.get('Kilometre', ''))
        km = None
        if km_str:
            km_match = re.search(r'([\d.]+)', km_str.replace('.', ''))
            if km_match:
                try:
                    km = int(km_match.group(1))
                except:
                    pass
        
        # Fiyat bilgisini al
        fiyat_str = data.get('Fiyat', '')
        fiyat = None
        if fiyat_str:
            fiyat_clean = re.sub(r'[^\d]', '', fiyat_str)
            if fiyat_clean:
                try:
                    fiyat = int(fiyat_clean)
                except:
                    pass
        
        # Renk bilgisini al
        renk = data.get('Renk', '')
        
        # Veritabanını güncelle
        cursor.execute('''
            UPDATE araclar 
            SET km = ?, fiyat = ?, renk = ?, son_gorulme = ?
            WHERE ilan_no = ?
        ''', (km, fiyat, renk, datetime.now(), ilan_no))
        
        if cursor.rowcount > 0:
            guncellenen += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ {guncellenen} ilan veritabanında güncellendi!")

if __name__ == '__main__':
    main()
