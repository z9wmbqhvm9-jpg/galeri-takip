#!/usr/bin/env python3
"""
Çayırova içindeki galericileri sahibinden.com üzerinden tespit eden basit scraper.

Nasıl çalışır (kısa):
- Sahibinden'de "Çayırova" araması yapar
- Arama sonuçlarındaki ilanlardan "Galeriden" ibaresi ve lokasyon bilgisi arar
- Her ilanı açıp satıcı (galeri) bölümünü kazıyıp aday galericileri toplar
- Sonuçları `cayirova_galeriler.json` içine kaydeder

Notlar:
- Cloudflare veya site challenge çıkarsa tarayıcıda elle geçiş yapmalısınız.
- Bu bir en iyi-çaba (best-effort) betiktir; site yapısı değişirse seçiciler güncellenmelidir.
"""

import json
import time
import argparse
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1366,900')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        # navigator.webdriver = undefined
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
    except Exception:
        pass
    return driver


def search_listings(driver, query, limit=200):
    q = quote(query)
    # Sahibinden arama URL (en basit hali)
    url = f'https://www.sahibinden.com/ara?q={q}'
    driver.get(url)
    time.sleep(3)

    # Uzun sayfalarda daha çok ilan çekmek için sayfada aşağı in
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)

    links = set()
    # Yaygın ilan link seçicisi
    anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/ilan/"]')
    for a in anchors:
        href = a.get_attribute('href')
        if href and '/ilan/' in href:
            links.add(href.split('?')[0])
        if len(links) >= limit:
            break

    return list(links)[:limit]


def extract_seller_from_listing(driver, listing_url, timeout=8):
    data = {'listing_url': listing_url, 'seller_name': None, 'seller_profile': None, 'seller_type': None, 'location_text': None}
    try:
        driver.get(listing_url)
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)

        page_text = driver.page_source

        # Basit kontrol: sayfada Çayırova geçiyor mu?
        if 'Çayırova' in page_text or 'Cayirova' in page_text:
            data['location_text'] = 'Çayırova'

        # Seller type: aramada genelde "Kimden: Galeriden" ifadesi bulunur
        if 'Galeriden' in page_text:
            data['seller_type'] = 'Galeriden'

        # Denenecek seller link/selectors
        candidate = None
        selectors = [
            'a[class*="classifiedSeller"]',
            'a[href*="sahibinden.com"]',
            'a[class*="sellerName"]',
            '.userInfo a',
            '.classifiedSeller a',
        ]
        for sel in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                href = el.get_attribute('href')
                text = el.text.strip()
                if text:
                    data['seller_name'] = text
                if href and 'sahibinden.com' in href:
                    data['seller_profile'] = href
                    break
                candidate = (text, href)
            except Exception:
                continue

        # Fallback: sayfadaki başlık veya ilan başlığı içinden satıcı ismi çekmeye çalış
        if not data['seller_name']:
            try:
                title = driver.find_element(By.CSS_SELECTOR, 'h1').text
                if title:
                    data['seller_name'] = title.split('|')[0].strip()
            except Exception:
                pass

        # Eğer seller_profile yok ama candidate varsa kullan
        if not data['seller_profile'] and candidate:
            data['seller_profile'] = candidate[1]
            if not data['seller_name'] and candidate[0]:
                data['seller_name'] = candidate[0]

    except Exception as e:
        data['error'] = str(e)

    return data


def main(limit, headless, out_file):
    driver = get_driver(headless=headless)
    try:
        listings = search_listings(driver, 'Çayırova', limit=limit)
        print(f'İlan linkleri bulundu: {len(listings)}')

        sellers = {}
        for i, url in enumerate(listings, 1):
            print(f'[{i}/{len(listings)}] İşleniyor: {url}')
            info = extract_seller_from_listing(driver, url)
            key = info.get('seller_profile') or info.get('seller_name') or url
            if key not in sellers:
                sellers[key] = info
            time.sleep(0.8)

        # Sadece Çayırova ve 'Galeriden' olanları filtrele (eğer bulunan varsa)
        filtered = [v for v in sellers.values() if (v.get('location_text') == 'Çayırova' or v.get('seller_type') == 'Galeriden')]
        if not filtered:
            # Eğer filtreleme sonucu 0 ise, tüm adayları kaydet
            filtered = list(sellers.values())

        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)

        print(f'✅ Sonuçlar kaydedildi: {out_file} (bulunan galerici adedi: {len(filtered)})')

    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Çayırova galerici bulucu (sahibinden.com)')
    parser.add_argument('--limit', type=int, default=120, help='Toplanacak ilan linki limiti')
    parser.add_argument('--headless', action='store_true', help='Headless modda çalıştır')
    parser.add_argument('--out', default='cayirova_galeriler.json', help='Çıktı JSON dosyası')
    args = parser.parse_args()

    main(args.limit, args.headless, args.out)
