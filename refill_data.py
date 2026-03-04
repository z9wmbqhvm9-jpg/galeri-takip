import json
import time
import re
import subprocess
import os
import pychrome

DEBUG_PORT = 9222

def connect_to_chrome():
    try:
        browser = pychrome.Browser(url=f"http://127.0.0.1:{DEBUG_PORT}")
        return browser
    except:
        return None

def run_js(tab, js_code):
    try:
        result = tab.Runtime.evaluate(expression=js_code, returnByValue=True)
        if 'result' in result and 'value' in result['result']:
            return result['result']['value']
        return None
    except:
        return None

def refill_missing_data():
    with open('cars_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vehicles = data.get('vehicles', []) if isinstance(data, dict) else data
    
    missing = [v for v in vehicles if not v.get('Fiyat') or 'bildirim' in str(v.get('Fiyat')) or not v.get('ekspertiz_ozeti') or not any(v['ekspertiz_ozeti'].values())]
    
    if not missing:
        print("✅ No missing data found!")
        return

    print(f"🔍 Found {len(missing)} vehicles with missing info. Connecting to Chrome...")
    browser = connect_to_chrome()
    if not browser:
        print("❌ Chrome not found at 9222. Please run chrome_scraper first or open chrome with --remote-debugging-port=9222")
        return

    tab = browser.new_tab()
    tab.start()
    
    js_extractor = '''
    (function() {
        var d = {};
        var pSel = ['.classifiedInfo h3', '.classified-price-container', '.price-value', '.classifiedInfo .price'];
        for (var s of pSel) {
            var el = document.querySelector(s);
            if (el && el.innerText.includes('TL')) {
                d['Fiyat'] = el.innerText.trim();
                break;
            }
        }
        var eks = { boya: [], degisen: [], tramer: "" };
        document.querySelectorAll('.car-vis-part[data-status]').forEach(function(part) {
            var status = part.getAttribute('data-status');
            var name = part.getAttribute('data-part-name') || part.id;
            if (status === 'painted') eks.boya.push(name);
            else if (status === 'changed') eks.degisen.push(name);
        });
        var descEl = document.querySelector('#classifiedDescription');
        if (descEl) {
            var text = descEl.innerText;
            var tramerMatch = text.match(/hasar kayd[ıi]\s*[:\-]?\s*([\d\.]+|yok|normal)/i);
            if (tramerMatch) eks.tramer = tramerMatch[0];
        }
        d['ekspertiz_ozeti'] = eks;
        return JSON.stringify(d);
    })();
    '''

    for i, v in enumerate(missing):
        url = v.get('url')
        print(f"[{i+1}/{len(missing)}] Scraping {url}...")
        tab.Page.navigate(url=url)
        time.sleep(4) # Wait for load
        
        result = run_js(tab, js_extractor)
        if result:
            new_data = json.loads(result)
            if new_data.get('Fiyat'):
                v['Fiyat'] = new_data['Fiyat']
                print(f"   💰 Price found: {v['Fiyat']}")
            if new_data.get('ekspertiz_ozeti') and any(new_data['ekspertiz_ozeti'].values()):
                v['ekspertiz_ozeti'] = new_data['ekspertiz_ozeti']
                print(f"   🛠️ Inspection found: {v['ekspertiz_ozeti']}")
        
        # Save every few items
        if i % 3 == 0:
            with open('cars_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    tab.stop()
    print("✅ Refill completed!")

if __name__ == "__main__":
    refill_missing_data()
