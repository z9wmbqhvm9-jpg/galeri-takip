import os
import json
import glob
import shutil
from datetime import datetime

def try_load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # JSON bozuksa satır satır dene
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            json_str = ''
            for line in lines:
                json_str += line
                try:
                    data = json.loads(json_str)
                    yield data
                    json_str = ''
                except:
                    continue
        except Exception as e2:
            pass
    return None

def extract_vehicles_from_any_format(obj):
    # Düz liste veya dict/cars anahtarı veya dict içinde ilan/vehicle/İlan No gibi anahtarlar
    vehicles = []
    if isinstance(obj, list):
        for item in obj:
            vehicles.extend(extract_vehicles_from_any_format(item))
    elif isinstance(obj, dict):
        if 'cars' in obj and isinstance(obj['cars'], list):
            vehicles.extend(obj['cars'])
        elif 'ilanlar' in obj and isinstance(obj['ilanlar'], list):
            vehicles.extend(obj['ilanlar'])
        elif 'İlan No' in obj or 'ilan_no' in obj or 'adNo' in obj or 'id' in obj:
            vehicles.append(obj)
        else:
            for v in obj.values():
                vehicles.extend(extract_vehicles_from_any_format(v))
    return vehicles

def scan_all_files():
    patterns = [
        'cars_data*.json', 'safari_data.json', 'all_data.json', 'backups/*.bak', '*.bak', '*.txt', '*.csv', '*.db', '*.log', '*.json', '*.py'
    ]
    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern, recursive=True))
    return list(files)

def main():
    files = scan_all_files()
    print(f"Taranan dosya sayısı: {len(files)}")
    all_vehicles = []
    seen = set()
    for file in files:
        print(f"İşleniyor: {file}")
        for data in try_load_json(file) or []:
            vehicles = extract_vehicles_from_any_format(data)
            for v in vehicles:
                key = str(v.get('plaka') or v.get('adNo') or v.get('id') or v.get('İlan No') or v.get('ilan_no') or json.dumps(v, sort_keys=True))
                if key not in seen:
                    all_vehicles.append(v)
                    seen.add(key)
    print(f"Toplam kurtarılan araç: {len(all_vehicles)}")
    with open('recovered_vehicles.json', 'w', encoding='utf-8') as f:
        json.dump(all_vehicles, f, ensure_ascii=False, indent=2)
    print("Kurtarılan araçlar recovered_vehicles.json dosyasına kaydedildi.")

if __name__ == '__main__':
    main()
