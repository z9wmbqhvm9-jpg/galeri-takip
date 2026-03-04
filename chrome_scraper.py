#!/usr/bin/env python3
"""
Windows + Chrome için Galeri Scraper
Chrome'u debug modunda açar ve DevTools Protocol ile kontrol eder.
Robot tespiti yok çünkü gerçek Chrome kullanılıyor!

KULLANIM:
1. Chrome'u kapat
2. Bu scripti çalıştır
3. Açılan Chrome'da Cloudflare'ı elle geç
4. Script otomatik devam edecek

pip install pychrome requests
"""

import json
import time
import re
import subprocess
import os
import platform
import sqlite3
from datetime import datetime
import argparse

try:
    import pychrome
except ImportError:
    print("❌ pychrome yüklü değil. Yükleniyor...")
    os.system("pip install pychrome requests")
    import pychrome

# Ayarlar
DB_PATH = 'galeri.db'
DEBUG_PORT = 9222

# Galeriler ve sayfa sayıları
GALERILER = [
    ('https://piranlarotomotiv.sahibinden.com', 2),
    ('https://yenikoymotors.sahibinden.com', 3),
]

def get_chrome_path():
    """İşletim sistemine göre Chrome yolunu bul"""
    system = platform.system()
    
    if system == 'Windows':
        paths = [
            os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
        ]
    elif system == 'Darwin':  # macOS
        paths = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    else:  # Linux
        paths = ['/usr/bin/google-chrome', '/usr/bin/chromium-browser']
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return 'chrome'  # PATH'te olduğunu varsay

def start_chrome_debug():
    """Chrome'u debug modunda başlat"""
    chrome_path = get_chrome_path()
    
    # Kullanıcı profili ile aç (çerezler korunur)
    user_data_dir = os.path.join(os.path.expanduser('~'), 'chrome_debug_profile')
    
    cmd = [
        chrome_path,
        f'--remote-debugging-port={DEBUG_PORT}',
        f'--user-data-dir={user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
    ]
    
    print(f"🌐 Chrome başlatılıyor (debug port: {DEBUG_PORT})...")
    
    if platform.system() == 'Windows':
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    print("✅ Chrome başlatıldı!")

def connect_to_chrome():
    """Chrome'a bağlan"""
    try:
        browser = pychrome.Browser(url=f"http://127.0.0.1:{DEBUG_PORT}")
        return browser
    except Exception as e:
        print(f"❌ Chrome'a bağlanılamadı: {e}")
        return None

def run_js(tab, js_code, timeout=30):
    """Sekmede JavaScript çalıştır"""
    try:
        result = tab.Runtime.evaluate(expression=js_code, returnByValue=True, timeout=timeout)
        if 'result' in result and 'value' in result['result']:
            return result['result']['value']
        return None
    except Exception as e:
        print(f"   ⚠️ JS hatası: {e}")
        return None

def wait_for_page_load(tab, timeout=30):
    """Sayfa yüklenene kadar bekle"""
    start = time.time()
    while time.time() - start < timeout:
        state = run_js(tab, 'document.readyState')
        if state == 'complete':
            return True
        time.sleep(0.5)
    return False

def check_cloudflare(tab):
    """Cloudflare kontrolü var mı?"""
    title = run_js(tab, 'document.title') or ''
    body = run_js(tab, 'document.body?.innerText?.substring(0, 500)') or ''
    
    if 'Checking' in title or 'lütfen' in body.lower() or 'moment' in body.lower():
        return True
    return False

def wait_for_cloudflare(tab, timeout=120):
    """Cloudflare geçilene kadar bekle"""
    print("⏳ Cloudflare kontrolü bekleniyor...")
    print("   → Eğer CAPTCHA varsa elle çözün!")
    
    start = time.time()
    while time.time() - start < timeout:
        if not check_cloudflare(tab):
            print("✅ Cloudflare geçildi!")
            return True
        time.sleep(2)
    
    print("❌ Cloudflare zaman aşımı!")
    return False

def get_listing_urls(tab):
    """Sayfadan ilan URL'lerini çek"""
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
    result = run_js(tab, js_code)
    try:
        return json.loads(result)
    except:
        return []

def click_next_page(tab):
    """Sonraki sayfaya git"""
    js_code = '''
    (function() {
        var next = document.querySelector('a[title="Sonraki"]:not(.passive)');
        if(next) { next.click(); return true; }
        return false;
    })();
    '''
    return run_js(tab, js_code)

def extract_listing_data(tab):
    """İlan detay sayfasından veri çek"""
    js_code = '''
    (function() {
        var data = {};
        // Temel Bilgiler
        document.querySelectorAll('ul.classifiedInfoList li, .classifiedInfo li').forEach(function(item) {
            var strong = item.querySelector('strong');
            var span = item.querySelector('span');
            if(strong && span) {
                var key = strong.innerText.replace(':', '').trim();
                var val = span.innerText.trim();
                if(key && val) data[key] = val;
            }
        });
        
        // Fiyat - Daha robust seçim
        var priceSelectors = ['.classifiedInfo h3', '.classified-price-container', '.price-value', '.classifiedInfo .price'];
        for (var s of priceSelectors) {
            var el = document.querySelector(s);
            if (el && el.innerText.includes('TL')) {
                data['Fiyat'] = el.innerText.trim();
                break;
            }
        }
        
        // Başlık
        var titleEl = document.querySelector('h1.classifiedDetailTitle');
        if(titleEl) data['Baslik'] = titleEl.innerText.trim();
        
        // Ekspertiz (Hasar) Bilgileri
        var ekspertiz = { boya: [], degisen: [], tramer: "" };
        
        // Açıklama kısmındaki hasar kaydı vs.
        var descEl = document.querySelector('#classifiedDescription');
        if (descEl) {
            var text = descEl.innerText;
            var tramerMatch = text.match(/hasar kayd[ıi]\s*:\s*([\d\.]+)/i);
            if (tramerMatch) ekspertiz.tramer = tramerMatch[0];
        }
        
        // Şemadaki boya/değişen bilgileri (Eğer varsa)
        document.querySelectorAll('.car-vis-part[data-status]').forEach(function(part) {
            var status = part.getAttribute('data-status');
            var name = part.getAttribute('data-part-name') || part.id;
            if (status === 'painted') ekspertiz.boya.push(name);
            else if (status === 'changed') ekspertiz.degisen.push(name);
        });
        
        // Liste halindeki boya/değişenler
        document.querySelectorAll('.classifiedInfoList li').forEach(function(li) {
            var txt = li.innerText.toLowerCase();
            if (txt.includes('boyalı') || txt.includes('değişen')) {
                var parts = txt.split(':');
                if (parts.length > 1) {
                    var key = parts[0].trim();
                    var val = parts[1].trim();
                    if (val.includes('Boyalı')) ekspertiz.boya.push(key);
                    if (val.includes('Değişen')) ekspertiz.degisen.push(key);
                }
            }
        });

        data['ekspertiz_ozeti'] = ekspertiz;
        
        var match = location.href.match(/(\\d{9,})/);
        if(match) data['ilan_no'] = match[1];
        data['url'] = location.href;
        return JSON.stringify(data);
    })();
    '''
    result = run_js(tab, js_code)
    try:
        return json.loads(result)
    except:
        return None

def scrape_gallery(browser, galeri_url, sayfa_sayisi):
    """Tek bir galeriyi tara"""
    print(f"\n{'='*50}")
    print(f"📂 {galeri_url}")
    print(f"{'='*50}")
    
    # Yeni sekme aç
    tab = browser.new_tab()
    tab.start()
    tab.Page.enable()
    tab.Runtime.enable()
    
    # Galeri sayfasına git
    tab.Page.navigate(url=galeri_url)
    time.sleep(5)
    wait_for_page_load(tab)
    
    # Cloudflare kontrolü
    if check_cloudflare(tab):
        if not wait_for_cloudflare(tab):
            tab.stop()
            browser.close_tab(tab)
            return []
    
    all_urls = []
    
    # Her sayfadan URL topla
    for sayfa in range(1, sayfa_sayisi + 1):
        print(f"\n📄 Sayfa {sayfa}/{sayfa_sayisi}")
        time.sleep(2)
        
        urls = get_listing_urls(tab)
        print(f"   {len(urls)} ilan bulundu")
        all_urls.extend(urls)
        
        if sayfa < sayfa_sayisi:
            click_next_page(tab)
            time.sleep(3)
            wait_for_page_load(tab)
    
    # Tekrarları kaldır
    all_urls = list(set(all_urls))
    print(f"\n📊 Toplam {len(all_urls)} benzersiz ilan")
    
    # Her ilanı ziyaret et ve veri çek
    all_data = []
    for i, url in enumerate(all_urls):
        print(f"\r   İlan {i+1}/{len(all_urls)} işleniyor...", end='', flush=True)
        
        tab.Page.navigate(url=url)
        time.sleep(2)
        wait_for_page_load(tab)
        
        # Cloudflare kontrolü
        if check_cloudflare(tab):
            wait_for_cloudflare(tab, timeout=60)
        
        data = extract_listing_data(tab)
        if data and data.get('ilan_no'):
            all_data.append(data)
        
        time.sleep(0.5)
    
    print(f"\n✅ {len(all_data)} ilan verisi çekildi!")
    
    tab.stop()
    browser.close_tab(tab)
    
    return all_data

def update_database(galeri_url, data_list):
    """Veritabanını güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabloları oluştur (yoksa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS galeriler (
            id INTEGER PRIMARY KEY,
            galeri_url TEXT UNIQUE,
            galeri_adi TEXT,
            son_kontrol DATETIME
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS araclar (
            id INTEGER PRIMARY KEY,
            galeri_id INTEGER,
            ilan_no TEXT UNIQUE,
            ilan_url TEXT,
            baslik TEXT,
            yil INTEGER,
            fiyat INTEGER,
            km INTEGER,
            renk TEXT,
            durum TEXT DEFAULT 'aktif',
            ilk_gorulme DATETIME DEFAULT CURRENT_TIMESTAMP,
            son_gorulme DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Galeri ID al/oluştur
    galeri_name = galeri_url.split('//')[1].split('.')[0]
    cursor.execute('INSERT OR IGNORE INTO galeriler (galeri_url, galeri_adi) VALUES (?, ?)',
                   (galeri_url, galeri_name.upper()))
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url = ?', (galeri_url,))
    galeri_id = cursor.fetchone()[0]
    
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
        url = data.get('url', '')
        
        # Yıl
        yil = data.get('Yıl', '')
        yil_int = None
        if yil:
            yil_match = re.search(r'(19|20)\d{2}', str(yil))
            if yil_match:
                yil_int = int(yil_match.group())
        
        # Mevcut mı kontrol et
        cursor.execute('SELECT id FROM araclar WHERE ilan_no = ?', (ilan_no,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE araclar 
                SET km = ?, renk = ?, fiyat = ?, son_gorulme = ?, durum = 'aktif', baslik = COALESCE(?, baslik)
                WHERE ilan_no = ?
            ''', (km, renk, fiyat, datetime.now(), baslik, ilan_no))
            guncellenen += 1
        else:
            cursor.execute('''
                INSERT INTO araclar (galeri_id, ilan_no, ilan_url, baslik, yil, fiyat, km, renk, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aktif')
            ''', (galeri_id, ilan_no, url, baslik, yil_int, fiyat, km, renk))
            eklenen += 1
    
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', 
                   (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()
    
    print(f"💾 Veritabanı: {eklenen} yeni, {guncellenen} güncelleme")

def generate_dashboard(output_file='dashboard.html'):
    """Dashboard HTML oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            a.ilan_no, a.baslik, a.yil, a.km, a.fiyat, a.renk, a.ilan_url, a.durum, a.ilk_gorulme,
            CASE WHEN a.galeri_id = 1 THEN 'Piranlar' ELSE 'Yeniköy' END as galeri
        FROM araclar a
        WHERE a.durum = 'aktif'
        ORDER BY a.ilk_gorulme DESC
    ''')
    
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    # Dashboard HTML template (kısaltılmış)
    template = open('dashboard_template.html', 'r', encoding='utf-8').read()
    html = template.replace('PLACEHOLDER_DATA', json.dumps(data, ensure_ascii=False, default=str))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"📊 Dashboard oluşturuldu: {output_file}")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🚗 GALERİ TAKİP SİSTEMİ - CHROME VERSION           ║
╠══════════════════════════════════════════════════════════════╣
║  Bu script Chrome'u debug modunda açar.                      ║
║  Cloudflare kontrolü gelirse ELLE geçmeniz gerekir.          ║
║  Sonra script otomatik olarak verileri çekecek.              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Chrome'u başlat
    start_chrome_debug()
    time.sleep(2)
    
    # Chrome'a bağlan
    browser = connect_to_chrome()
    if not browser:
        print("\n❌ Chrome'a bağlanılamadı!")
        print("   Chrome zaten açıksa kapatıp tekrar deneyin.")
        return
    
    print("\n✅ Chrome'a bağlandı!")
    
    all_data = []
    
    # CLI ile tek bir URL verildiyse onu kullan, yoksa varsayılan GALERILER'i kullan
    parser = argparse.ArgumentParser(description='Chrome scraper - single gallery override')
    parser.add_argument('--url', help='Tek bir galeri URLsi (örnek: https://.../galeriden)')
    parser.add_argument('--pages', type=int, default=20, help='Kaç sayfa taranacağı (varsayılan 20)')
    args = parser.parse_args()

    target_galeriler = GALERILER
    if args.url:
        target_galeriler = [(args.url, args.pages)]

    # Her galeriyi tara
    for galeri_url, sayfa_sayisi in target_galeriler:
        try:
            data = scrape_gallery(browser, galeri_url, sayfa_sayisi)
            all_data.extend(data)
            update_database(galeri_url, data)
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    # JSON kaydet
    with open('all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ TAMAMLANDI!")
    print(f"   Toplam: {len(all_data)} ilan")
    print(f"   Veri: all_data.json")
    print(f"{'='*50}")
    
    # Dashboard oluştur
    try:
        generate_dashboard()
    except:
        print("⚠️ Dashboard oluşturulamadı (template dosyası eksik olabilir)")
    
    input("\nÇıkmak için Enter'a basın...")

if __name__ == '__main__':
    main()
