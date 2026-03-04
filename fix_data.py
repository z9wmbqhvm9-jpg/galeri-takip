import json
import sqlite3
import re
import os

def clean_price(price_str):
    if not price_str or not isinstance(price_str, str):
        return price_str
    if "Fiyat bildirimlerini" in price_str:
        return 0
    digits = re.sub(r'[^\d]', '', price_str)
    return int(digits) if digits else 0

def fix_cars_data():
    cars_data_path = 'cars_data.json'
    if not os.path.exists(cars_data_path):
        print(f"Error: {cars_data_path} not found")
        return

    with open(cars_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vehicles = data.get('vehicles', []) if isinstance(data, dict) else data
    
    # DB mappings
    prices_db = {}
    try:
        conn = sqlite3.connect('galeri.db')
        c = conn.cursor()
        for row in c.execute('SELECT ilan_no, fiyat FROM araclar'):
            if row[1]: prices_db[row[0]] = row[1]
        conn.close()
    except:
        pass

    try:
        conn = sqlite3.connect('galeri_takip.db')
        c = conn.cursor()
        for row in c.execute('SELECT ad_no, price FROM prices ORDER BY timestamp DESC'):
            if row[1]: prices_db[row[0]] = row[1]
        conn.close()
    except:
        pass

    fixed_count = 0
    inspection_count = 0
    for v in vehicles:
        ad_no = v.get('İlan No') or v.get('ilan_no') or v.get('id')
        baslik = v.get('Baslik', '')
        
        # 1. Hasar / Ekspertiz extraction from Baslik
        if 'ekspertiz_ozeti' not in v or (not v['ekspertiz_ozeti'].get('boya') and not v['ekspertiz_ozeti'].get('tramer')):
            v['ekspertiz_ozeti'] = v.get('ekspertiz_ozeti', {'boya': [], 'degisen': [], 'tramer': ''})
            
            # Simple keyword matching in title
            if any(word in baslik.lower() for word in ['hatasiz', 'boyasiz', 'degisensiz', 'tramersiz']):
                if 'hatasiz' in baslik.lower():
                    v['ekspertiz_ozeti']['tramer'] = 'Hatasız'
                if 'boyasiz' in baslik.lower():
                    v['ekspertiz_ozeti']['boya'] = ['Boyasız']
                if 'degisensiz' in baslik.lower():
                    v['ekspertiz_ozeti']['degisen'] = ['Değişensiz']
                inspection_count += 1
            
            # Try to find Tramer in title? Usually "HASAR KAYITLI" or "Tramer..."
            tramer_match = re.search(r"tramer\s*[:\-]\s*([\w\d\s]+)", baslik, re.I)
            if tramer_match:
                v['ekspertiz_ozeti']['tramer'] = tramer_match.group(1).split('|')[0].strip()
        
        # 2. Fix Price (Fiyat)
        current_price = clean_price(v.get('Fiyat', ''))
        if current_price == 0:
            if ad_no in prices_db:
                v['Fiyat'] = f"{prices_db[ad_no]:,} TL".replace(',', '.')
                fixed_count += 1
            else:
                price_match = re.search(r"(\d[\d\.]*)\s*TL", baslik)
                if price_match:
                    v['Fiyat'] = price_match.group(0)
                    fixed_count += 1
        
        # 3. Fix Package (Paket)
        if not v.get('Paket') or v.get('Paket') == '-':
            seri = v.get('Seri', '')
            model = v.get('Model', '')
            if model and seri and model != seri:
                v['Paket'] = model
            # Also look at title? titles often have the package name
            # e.g., "... 520i M Sport"
            if model in baslik:
                v['Paket'] = model

    # Save back
    output = {'vehicles': vehicles} if isinstance(data, dict) and 'vehicles' in data else vehicles
    with open(cars_data_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fixed {fixed_count} vehicle prices in {cars_data_path}")

if __name__ == "__main__":
    fix_cars_data()
