import json
import os

def load_any(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get('vehicles', [])
    except Exception as e:
        print(f"Error loading {path}: {e}")
    return []

def normalize(v):
    # Map to cars_data.json standard
    res = {}
    ino = str(v.get('ilan_no') or v.get('İlan No') or v.get('id') or v.get('adNo') or '')
    if not ino: return None
    
    res['ilan_no'] = ino
    res['İlan No'] = ino
    
    veh = v.get('vehicle', {})
    res['Marka'] = v.get('Marka') or v.get('marka') or v.get('brand') or veh.get('brand') or '-'
    res['Seri'] = v.get('Seri') or v.get('seri') or v.get('model') or veh.get('model') or '-'
    res['Model'] = v.get('Model') or v.get('package') or veh.get('package') or '-'
    res['Yıl'] = str(v.get('Yıl') or v.get('yil') or veh.get('year') or '-')
    res['KM'] = str(v.get('KM') or v.get('km') or veh.get('km') or '-')
    
    fiyat = v.get('Fiyat') or v.get('fiyat') or v.get('price') or '-'
    if str(fiyat).isdigit():
        res['Fiyat'] = f"{int(float(fiyat)):,} TL".replace(',', '.')
    else:
        res['Fiyat'] = str(fiyat)
        
    res['Yakıt Tipi'] = v.get('Yakıt Tipi') or v.get('yakit') or veh.get('fuel') or '-'
    res['Vites'] = v.get('Vites') or v.get('vites') or veh.get('transmission') or '-'
    res['Renk'] = v.get('Renk') or v.get('renk') or veh.get('color') or '-'
    res['İlan Tarihi'] = v.get('İlan Tarihi') or v.get('publishDate') or '-'
    res['url'] = v.get('url') or v.get('adUrl') or f"https://www.sahibinden.com/ilan/vasita-{ino}/detay"
    res['Baslik'] = v.get('Baslik') or v.get('baslik') or f"{res['Marka']} {res['Seri']}"
    
    seller = v.get('seller', {})
    res['Kimden'] = v.get('Kimden') or v.get('kimden') or seller.get('name') or 'Galeriden'
    res['Paket'] = v.get('Paket') or res['Model']
    
    # Expertise
    if 'ekspertiz_ozeti' in v:
        res['ekspertiz_ozeti'] = v['ekspertiz_ozeti']
    elif 'inspection' in v:
        insp = v['inspection']
        res['ekspertiz_ozeti'] = {
            'boya': [k for k, val in insp.items() if 'Boya' in str(val)],
            'degisen': [k for k, val in insp.items() if 'Değiş' in str(val)],
            'tramer': str(insp.get('Tramer') or insp.get('tramer') or '')
        }
    else:
        res['ekspertiz_ozeti'] = {'boya': [], 'degisen': [], 'tramer': ''}
        
    return res

def main():
    files = [
        'cars_data_backup_before_clear.json',
        'ilan_sonuc.json',
        'rich_data_input.json',
        'cars_data.json'
    ]
    
    all_vehicles = {}
    
    for f in files:
        data = load_any(f)
        for v in data:
            norm = normalize(v)
            if norm and norm['Marka'] != '-':
                ino = norm['ilan_no']
                # Prefer one with more data
                if ino not in all_vehicles or len(str(v)) > len(str(all_vehicles[ino]['_orig'])):
                    norm['_orig'] = v
                    all_vehicles[ino] = norm
                    
    final_list = []
    for v in all_vehicles.values():
        if '_orig' in v: del v['_orig']
        final_list.append(v)
        
    print(f"Total merged: {len(final_list)}")
    
    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump({"vehicles": final_list}, f, ensure_ascii=False, indent=2)
        
    # Generate all_data.json for dashboard compatibility
    all_data = []
    for v in final_list:
        all_data.append({
            "ilan_no": v['ilan_no'],
            "marka": v['Marka'],
            "model": v['Seri'],
            "varyant": v['Model'],
            "yil": v['Yıl'],
            "km": v['KM'],
            "fiyat": v['Fiyat'],
            "yakit": v['Yakıt Tipi'],
            "vites": v['Vites'],
            "ilan_url": v['url'],
            "durum": "aktif"
        })
    with open('all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
