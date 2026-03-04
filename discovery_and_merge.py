import json
import os
import re

def normalize_vehicle(v):
    """Normalize common fields to the cars_data.json structure"""
    norm = {}
    
    # Primary Key
    ilan_no = str(v.get('ilan_no') or v.get('İlan No') or v.get('id') or v.get('adNo') or '')
    if not ilan_no or not ilan_no.isdigit():
        return None
    
    norm['ilan_no'] = ilan_no
    norm['İlan No'] = ilan_no
    
    # Nested "vehicle" support
    v_obj = v.get('vehicle', {})
    
    # Basics
    norm['Marka'] = v.get('Marka') or v.get('marka') or v_obj.get('brand') or '-'
    norm['Seri'] = v.get('Seri') or v.get('seri') or v.get('model') or v_obj.get('model') or '-'
    norm['Model'] = v.get('Model') or v.get('model_paket') or v.get('varyant') or v.get('Paket') or v_obj.get('package') or '-'
    norm['Yıl'] = str(v.get('Yıl') or v.get('yil') or v.get('Üretim Yılı') or v_obj.get('year') or '-')
    norm['KM'] = str(v.get('KM') or v.get('km') or v_obj.get('km') or '-')
    norm['Fiyat'] = str(v.get('Fiyat') or v.get('fiyat') or v.get('price') or '-')
    if norm['Fiyat'].isdigit() or isinstance(v.get('price'), (int, float)):
        norm['Fiyat'] = f"{int(float(norm['Fiyat'])):,} TL".replace(',', '.')
        
    norm['Yakıt Tipi'] = v.get('Yakıt Tipi') or v.get('yakit') or v.get('Yakıt') or v_obj.get('fuel') or '-'
    norm['Vites'] = v.get('Vites') or v.get('vites') or v_obj.get('transmission') or '-'
    norm['Renk'] = v.get('Renk') or v.get('renk') or v_obj.get('color') or '-'
    norm['İlan Tarihi'] = v.get('İlan Tarihi') or v.get('tarih') or v.get('ilk_gorulme') or v.get('publishDate') or '-'
    norm['url'] = v.get('url') or v.get('ilan_url') or f"https://www.sahibinden.com/ilan/vasita-{ilan_no}/detay"
    norm['Baslik'] = v.get('Baslik') or v.get('baslik') or f"{norm['Marka']} {norm['Seri']}"
    
    seller = v.get('seller', {})
    norm['Kimden'] = v.get('Kimden') or v.get('kimden') or seller.get('name') or 'Galeriden'
    norm['Paket'] = v.get('Paket') or v.get('model_paket') or v.get('varyant') or v_obj.get('package') or norm['Model']
    
    # Inspection support
    if 'ekspertiz_ozeti' in v:
        norm['ekspertiz_ozeti'] = v['ekspertiz_ozeti']
    elif 'inspection' in v:
        insp = v['inspection']
        norm['ekspertiz_ozeti'] = {
            'boya': [k for k, val in insp.items() if 'Boya' in str(val)],
            'degisen': [k for k, val in insp.items() if 'Değiş' in str(val)],
            'tramer': insp.get('Tramer') or insp.get('tramer') or ''
        }
    else:
        norm['ekspertiz_ozeti'] = {'boya': [], 'degisen': [], 'tramer': ''}
        
    return norm

def discover():
    json_files = [
        'all_data.json', 'all_data_backup_before_clear.json', 'cars_data.json',
        'cars_data_backup_before_clear.json', 'cars_data_cleaned.json', 
        'cars_data_cleaned_all.json', 'cars_data_final.json', 'cars_data_firstblock.json',
        'cars_data_fixed.json', 'cars_data_fixed_clean.json', 'ilan_sonuc.json',
        'rich_data_input.json'
    ]
    
    unique_vehicles = {} # ilan_no -> vehicle
    
    for f_name in json_files:
        if not os.path.exists(f_name):
            continue
            
        print(f"Reading {f_name}...")
        try:
            with open(f_name, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            # Handle list or dict/vehicles
            v_list = content if isinstance(content, list) else content.get('vehicles', [])
            if not isinstance(v_list, list):
                continue
                
            found_count = 0
            for v in v_list:
                if not isinstance(v, dict): continue
                norm = normalize_vehicle(v)
                if norm and norm.get('Marka') and norm.get('Marka') != '-':
                    # Update if not exists or if new one has more info
                    ino = norm['ilan_no']
                    if ino not in unique_vehicles or len(v.keys()) > len(unique_vehicles[ino].get('_raw_keys_count', 0)):
                        norm['_raw_keys_count'] = len(v.keys())
                        unique_vehicles[ino] = norm
                        found_count += 1
            print(f"   -> Found {found_count} valid vehicles")
        except Exception as e:
            print(f"   !! Error reading {f_name}: {e}")

    # Remove the helper key
    for v in unique_vehicles.values():
        if '_raw_keys_count' in v:
            del v['_raw_keys_count']

    final_list = list(unique_vehicles.values())
    
    # Save to main files
    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump({"vehicles": final_list}, f, ensure_ascii=False, indent=2)
        
    # Also update all_data.json
    all_data_list = []
    for v in final_list:
        ad = {
            "ilan_no": v['ilan_no'],
            "marka": v['Marka'],
            "model": v['Seri'],
            "varyant": v['Model'],
            "yil": int(v['Yıl']) if v['Yıl'].isdigit() else v['Yıl'],
            "km": v['KM'],
            "fiyat": v['Fiyat'],
            "yakit": v['Yakıt Tipi'],
            "vites": v['Vites'],
            "ilan_url": v['url'],
            "durum": "aktif"
        }
        all_data_list.append(ad)
        
    with open('all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data_list, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Total unique vehicles discovered and merged: {len(final_list)}")

if __name__ == "__main__":
    discover()
