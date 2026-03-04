#!/usr/bin/env python3
"""
Günlük Galeri Kontrol Sistemi
Her gün çalışır, değişiklikleri tespit eder ve bildirim gönderir
"""

import subprocess
import json
import time
import re
import sqlite3
import os
from datetime import datetime

DB_PATH = '/Volumes/AS1000_Plus/galeri/galeri.db'
LOG_PATH = '/Volumes/AS1000_Plus/galeri/logs'
REPORT_PATH = '/Volumes/AS1000_Plus/galeri/reports'

# Galeriler ve sayfa sayıları
GALERILER = [
    ('https://piranlarotomotiv.sahibinden.com', 2),
    ('https://yenikoymotors.sahibinden.com', 3),
]

def run_applescript(script):
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def send_notification(title, message):
    """macOS bildirim gönder"""
    script = f'''
    display notification "{message}" with title "{title}" sound name "Glass"
    '''
    run_applescript(script)

def open_url_in_new_window(url):
    script = f'''
    tell application "Safari"
        activate
        make new document with properties {{URL:"{url}"}}
    end tell
    '''
    run_applescript(script)

def open_url_in_new_tab(url):
    script = f'''
    tell application "Safari"
        tell front window
            make new tab with properties {{URL:"{url}"}}
        end tell
    end tell
    '''
    run_applescript(script)

def get_tab_count():
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

def close_all_tabs():
    """Tüm sekmeleri kapat"""
    script = '''
    tell application "Safari"
        close every window
    end tell
    '''
    run_applescript(script)

def run_js_in_current_tab(js_code):
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    script = f'''
    tell application "Safari"
        tell front window
            do JavaScript "{js_escaped}" in current tab
        end tell
    end tell
    '''
    return run_applescript(script)

def run_js_in_tab(tab_index, js_code):
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    script = f'''
    tell application "Safari"
        tell front window
            do JavaScript "{js_escaped}" in tab {tab_index}
        end tell
    end tell
    '''
    return run_applescript(script)

def get_listing_urls():
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
    js_code = '''
    (function() {
        var next = document.querySelector('a[title="Sonraki"]:not(.passive)');
        if(next) { next.click(); return "clicked"; }
        return "no_next";
    })();
    '''
    return run_js_in_current_tab(js_code)

def extract_data_from_tab(tab_index):
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

def scrape_galeri(galeri_url, sayfa_sayisi):
    """Tek bir galeriyi tara"""
    print(f"\n📂 {galeri_url} taranıyor...")
    
    open_url_in_new_window(galeri_url)
    time.sleep(8)
    
    all_urls = []
    
    for sayfa in range(1, sayfa_sayisi + 1):
        print(f"   Sayfa {sayfa}...")
        time.sleep(3)
        urls = get_listing_urls()
        all_urls.extend(urls)
        if sayfa < sayfa_sayisi:
            click_next_page()
            time.sleep(4)
    
    all_urls = list(set(all_urls))
    print(f"   {len(all_urls)} ilan bulundu")
    
    # Sekmeleri aç
    for url in all_urls:
        open_url_in_new_tab(url)
        time.sleep(0.4)
    
    time.sleep(15)
    
    # Verileri çek
    all_data = []
    tab_count = get_tab_count()
    
    for i in range(2, tab_count + 1):
        data = extract_data_from_tab(i)
        if data and data.get('ilan_no'):
            all_data.append(data)
        time.sleep(0.3)
    
    close_all_tabs()
    time.sleep(2)
    
    return all_data

def check_changes(galeri_url, new_data):
    """Değişiklikleri tespit et"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    galeri_name = galeri_url.split('//')[1].split('.')[0]
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE ?', (f'%{galeri_name}%',))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return {'new': [], 'sold': [], 'price_changes': []}
    
    galeri_id = result[0]
    
    # Mevcut aktif ilanları al
    cursor.execute('''
        SELECT ilan_no, baslik, fiyat 
        FROM araclar 
        WHERE galeri_id = ? AND durum = 'aktif'
    ''', (galeri_id,))
    
    mevcut = {row[0]: {'baslik': row[1], 'fiyat': row[2]} for row in cursor.fetchall()}
    
    changes = {'new': [], 'sold': [], 'price_changes': []}
    bulunan = set()
    
    for data in new_data:
        ilan_no = data.get('ilan_no')
        if not ilan_no:
            continue
        
        bulunan.add(ilan_no)
        
        # Fiyat çıkar
        fiyat_str = data.get('Fiyat', '')
        fiyat = None
        if fiyat_str:
            fiyat_clean = re.sub(r'[^\d]', '', fiyat_str)
            if fiyat_clean:
                fiyat = int(fiyat_clean)
        
        if ilan_no not in mevcut:
            # Yeni ilan!
            changes['new'].append({
                'ilan_no': ilan_no,
                'baslik': data.get('Baslik', 'Bilinmeyen'),
                'fiyat': fiyat
            })
        elif fiyat and mevcut[ilan_no]['fiyat']:
            # Fiyat değişikliği kontrolü
            eski_fiyat = mevcut[ilan_no]['fiyat']
            if fiyat != eski_fiyat:
                changes['price_changes'].append({
                    'ilan_no': ilan_no,
                    'baslik': mevcut[ilan_no]['baslik'],
                    'eski_fiyat': eski_fiyat,
                    'yeni_fiyat': fiyat
                })
    
    # Satılan araçlar
    for ilan_no, info in mevcut.items():
        if ilan_no not in bulunan:
            changes['sold'].append({
                'ilan_no': ilan_no,
                'baslik': info['baslik']
            })
    
    conn.close()
    return changes

def update_database(galeri_url, data_list):
    """Veritabanını güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    galeri_name = galeri_url.split('//')[1].split('.')[0]
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE ?', (f'%{galeri_name}%',))
    result = cursor.fetchone()
    
    if not result:
        return
    
    galeri_id = result[0]
    bulunan = set()
    
    for data in data_list:
        ilan_no = data.get('ilan_no')
        if not ilan_no:
            continue
        
        bulunan.add(ilan_no)
        
        km_str = data.get('KM', '')
        km = None
        if km_str:
            km_clean = km_str.replace('.', '').replace(' ', '')
            km_match = re.search(r'(\d+)', km_clean)
            if km_match:
                km = int(km_match.group(1))
        
        renk = data.get('Renk', '')
        
        fiyat_str = data.get('Fiyat', '')
        fiyat = None
        if fiyat_str:
            fiyat_clean = re.sub(r'[^\d]', '', fiyat_str)
            if fiyat_clean:
                fiyat = int(fiyat_clean)
        
        baslik = data.get('Baslik', '')
        url = data.get('url', '')
        
        yil = data.get('Yıl', '')
        yil_int = None
        if yil:
            yil_match = re.search(r'(19|20)\d{2}', str(yil))
            if yil_match:
                yil_int = int(yil_match.group())
        
        cursor.execute('SELECT id FROM araclar WHERE ilan_no = ?', (ilan_no,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE araclar 
                SET km = ?, renk = ?, fiyat = ?, son_gorulme = ?, durum = 'aktif'
                WHERE ilan_no = ?
            ''', (km, renk, fiyat, datetime.now(), ilan_no))
        else:
            cursor.execute('''
                INSERT INTO araclar (galeri_id, ilan_no, ilan_url, baslik, yil, fiyat, km, renk, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aktif')
            ''', (galeri_id, ilan_no, url, baslik, yil_int, fiyat, km, renk))
    
    # Satılanları işaretle
    cursor.execute('''
        SELECT ilan_no FROM araclar 
        WHERE galeri_id = ? AND durum = 'aktif'
    ''', (galeri_id,))
    
    for row in cursor.fetchall():
        if row[0] not in bulunan:
            cursor.execute('''
                UPDATE araclar SET durum = 'satildi', son_gorulme = ?
                WHERE ilan_no = ?
            ''', (datetime.now(), row[0]))
    
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', 
                   (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()

def generate_report(all_changes):
    """Rapor oluştur"""
    os.makedirs(REPORT_PATH, exist_ok=True)
    
    tarih = datetime.now().strftime('%Y-%m-%d_%H-%M')
    report_file = f'{REPORT_PATH}/rapor_{tarih}.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"📊 GALERİ TAKİP RAPORU - {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        
        for galeri, changes in all_changes.items():
            f.write(f"\n🏢 {galeri.upper()}\n")
            f.write("-" * 40 + "\n")
            
            if changes['new']:
                f.write(f"\n🆕 YENİ İLANLAR ({len(changes['new'])})\n")
                for item in changes['new']:
                    fiyat = f"{item['fiyat']:,} TL" if item['fiyat'] else '-'
                    f.write(f"   • {item['baslik'][:50]}... - {fiyat}\n")
            
            if changes['sold']:
                f.write(f"\n🔴 SATILAN ARAÇLAR ({len(changes['sold'])})\n")
                for item in changes['sold']:
                    f.write(f"   • {item['baslik'][:50]}...\n")
            
            if changes['price_changes']:
                f.write(f"\n💰 FİYAT DEĞİŞİKLİKLERİ ({len(changes['price_changes'])})\n")
                for item in changes['price_changes']:
                    eski = f"{item['eski_fiyat']:,}" if item['eski_fiyat'] else '-'
                    yeni = f"{item['yeni_fiyat']:,}" if item['yeni_fiyat'] else '-'
                    f.write(f"   • {item['baslik'][:40]}...\n")
                    f.write(f"     {eski} TL → {yeni} TL\n")
            
            if not changes['new'] and not changes['sold'] and not changes['price_changes']:
                f.write("   Değişiklik yok ✓\n")
    
    return report_file

def main():
    print("🚀 Günlük galeri kontrolü başlıyor...")
    print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 50)
    
    os.makedirs(LOG_PATH, exist_ok=True)
    
    all_changes = {}
    total_new = 0
    total_sold = 0
    total_price = 0
    
    for galeri_url, sayfa_sayisi in GALERILER:
        galeri_name = galeri_url.split('//')[1].split('.')[0]
        
        try:
            # Galeriyi tara
            data = scrape_galeri(galeri_url, sayfa_sayisi)
            
            # Değişiklikleri tespit et
            changes = check_changes(galeri_url, data)
            all_changes[galeri_name] = changes
            
            # Veritabanını güncelle
            update_database(galeri_url, data)
            
            total_new += len(changes['new'])
            total_sold += len(changes['sold'])
            total_price += len(changes['price_changes'])
            
            print(f"✅ {galeri_name}: {len(data)} ilan, {len(changes['new'])} yeni, {len(changes['sold'])} satıldı")
            
        except Exception as e:
            print(f"❌ {galeri_name} hatası: {e}")
            all_changes[galeri_name] = {'new': [], 'sold': [], 'price_changes': []}
    
    # Rapor oluştur
    report_file = generate_report(all_changes)
    print(f"\n📄 Rapor: {report_file}")
    
    # Bildirim gönder
    if total_new > 0 or total_sold > 0 or total_price > 0:
        message = f"{total_new} yeni, {total_sold} satıldı, {total_price} fiyat değişikliği"
        send_notification("🚗 Galeri Güncellemesi", message)
        print(f"\n🔔 Bildirim gönderildi: {message}")
    else:
        send_notification("🚗 Galeri Kontrolü", "Değişiklik yok")
        print("\n✓ Değişiklik yok")
    
    print("\n✅ Kontrol tamamlandı!")

if __name__ == '__main__':
    main()
