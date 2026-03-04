import os
import json
import glob
import shutil
from datetime import datetime

def load_vehicles_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'cars' in data:
                return data['cars']
            elif isinstance(data, list):
                return data
            else:
                return []
    except Exception as e:
        print(f"[WARN] {filepath} okunamadı: {e}")
        return []

def merge_all_vehicle_data():
    # Tüm cars_data*.json, safari_data.json, all_data.json dosyalarını bul
    patterns = [
        'cars_data*.json',
        'safari_data.json',
        'all_data.json'
    ]
    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern))
    print(f"Bulunan dosyalar: {files}")
    all_vehicles = []
    seen = set()
    for file in files:
        vehicles = load_vehicles_from_file(file)
        for v in vehicles:
            # Benzersiz anahtar: plaka veya varsa id/ad_no
            key = str(v.get('plaka') or v.get('ad_no') or v.get('id') or json.dumps(v, sort_keys=True))
            if key not in seen:
                all_vehicles.append(v)
                seen.add(key)
    return all_vehicles

def backup_file(filepath):
    if os.path.exists(filepath):
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f"{os.path.basename(filepath)}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)
        print(f"Yedek alındı: {backup_path}")

def validate_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"[HATA] JSON bozuk: {filepath} - {e}")
        return False

def main():
    output_file = 'cars_data.json'
    backup_file(output_file)
    all_vehicles = merge_all_vehicle_data()
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_vehicles, f, ensure_ascii=False, indent=2)
    print(f"Birleştirilen araç sayısı: {len(all_vehicles)}")
    if validate_json(output_file):
        print("cars_data.json başarıyla oluşturuldu ve doğrulandı.")
    else:
        print("[UYARI] cars_data.json kaydedildi fakat JSON bozuk!")

if __name__ == '__main__':
    main()
