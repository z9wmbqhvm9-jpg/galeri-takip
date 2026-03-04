import json
import uuid
from datetime import datetime

INPUT = 'all_data.json'
OUTPUT = 'cars_data.json'

def make_vehicle(entry):
    vehicle = {
        'id': entry.get('ilan_no', str(uuid.uuid4())),
        'adNo': entry.get('ilan_no', ''),
        'publishDate': entry.get('ilk_gorulme', ''),
        'daysListed': 0,
        'vehicle': {
            'year': entry.get('yil', None),
            'brand': entry.get('marka', ''),
            'model': entry.get('model', ''),
            'fuel': entry.get('yakit', ''),
            'transmission': entry.get('vites', ''),
            'km': entry.get('km', None),
            'color': entry.get('renk', ''),
            'body_type': '',
            'engine': '',
            'hp': entry.get('motor_gucu', ''),
        },
        'price': entry.get('fiyat', None),
        'seller': {
            'name': entry.get('galeri', ''),
            'type': 'Galeri',
            'phone': '',
            'url': entry.get('ilan_url', '')
        },
        'location': {
            'city': entry.get('sehir', ''),
            'district': '',
            'region': '',
            'neighborhood': ''
        },
        'condition': {
            'status': entry.get('durum', ''),
            'heavyDamaged': False,
            'warranty': False,
            'exchange': False,
        },
        'description': entry.get('aciklama', entry.get('baslik', '')),
        'features': [],
        'inspection': {},
    }
    return vehicle

def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('cars_data.json', 'r', encoding='utf-8') as f:
        cars_data = json.load(f)
    vehicles = cars_data['vehicles']
    ids = set(v['id'] for v in vehicles)
    new_vehicles = [make_vehicle(entry) for entry in data if entry.get('ilan_no', str(uuid.uuid4())) not in ids]
    vehicles.extend(new_vehicles)
    regions = cars_data.get('regions', {})
    for v in new_vehicles:
        regions.setdefault('AllData', []).append(v['id'])
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({'vehicles': vehicles, 'regions': regions}, f, ensure_ascii=False, indent=2)
    print(f"Eklenen yeni araç: {len(new_vehicles)} | Toplam araç: {len(vehicles)} | Çıktı: {OUTPUT}")

if __name__ == '__main__':
    main()
