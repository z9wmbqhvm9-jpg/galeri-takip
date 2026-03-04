import json
import uuid
from datetime import datetime

INPUT = 'safari_data.json'
OUTPUT = 'cars_data.json'

def clean_price(raw):
    # Fiyat alanı metin, sayısal değeri ayıkla
    if not raw or not isinstance(raw, str):
        return None
    for line in raw.splitlines():
        line = line.strip().replace('.', '').replace(',', '')
        if line.isdigit():
            return int(line)
    return None

def make_vehicle(entry):
    # Gerekli alanları dönüştür
    vehicle = {
        'id': entry.get('ilan_no') or entry.get('İlan No') or str(uuid.uuid4()),
        'adNo': entry.get('ilan_no') or entry.get('İlan No') or '',
        'publishDate': entry.get('İlan Tarihi', ''),
        'daysListed': 0,
        'vehicle': {
            'year': int(entry.get('Yıl', '0')) if entry.get('Yıl') else None,
            'brand': entry.get('Marka', ''),
            'model': entry.get('Model', ''),
            'fuel': entry.get('Yakıt Tipi', ''),
            'transmission': entry.get('Vites', ''),
            'km': int(entry.get('KM', '0').replace('.', '').replace(',', '')) if entry.get('KM') else None,
            'color': entry.get('Renk', ''),
            'body_type': entry.get('Kasa Tipi', entry.get('Üst Yapı', '')),
            'engine': entry.get('Motor Hacmi', ''),
            'hp': entry.get('Motor Gücü', entry.get('Motor Gücü (HP)', '')),
        },
        'price': clean_price(entry.get('Fiyat', '')),
        'seller': {
            'name': entry.get('Kimden', ''),
            'type': 'Galeri' if 'galeri' in entry.get('Kimden', '').lower() else entry.get('Kimden', ''),
            'phone': '',
            'url': entry.get('url', '')
        },
        'location': {
            'city': '',
            'district': '',
            'region': '',
            'neighborhood': ''
        },
        'condition': {
            'status': entry.get('Araç Durumu', entry.get('Durumu', '')),
            'heavyDamaged': entry.get('Ağır Hasar Kayıtlı', '').lower() == 'evet',
            'warranty': entry.get('Garanti', '').lower() == 'evet',
            'exchange': entry.get('Takas', '').lower() == 'evet',
        },
        'description': entry.get('Baslik', ''),
        'features': [],
        'inspection': {},
    }
    return vehicle

def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    vehicles = [make_vehicle(entry) for entry in data]
    regions = {}
    for v in vehicles:
        regions.setdefault('Safari', []).append(v['id'])
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({'vehicles': vehicles, 'regions': regions}, f, ensure_ascii=False, indent=2)
    print(f"Toplam araç: {len(vehicles)} | Çıktı: {OUTPUT}")

if __name__ == '__main__':
    main()
