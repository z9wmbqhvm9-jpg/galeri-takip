import json

# Eksik alanları tamamlamak için kullanılacak varsayılanlar
def get_defaults():
    return {
        'adUrl': '',
        'inspection': {},
        'vehicle': {
            'km': 0
        }
    }

def fix_vehicle(vehicle):
    defaults = get_defaults()
    # adUrl
    if 'adUrl' not in vehicle:
        vehicle['adUrl'] = defaults['adUrl']
    # inspection
    if 'inspection' not in vehicle:
        vehicle['inspection'] = defaults['inspection']
    # vehicle.km
    if 'vehicle' in vehicle:
        if 'km' not in vehicle['vehicle']:
            vehicle['vehicle']['km'] = defaults['vehicle']['km']
    else:
        vehicle['vehicle'] = {'km': 0}
    return vehicle

def main():
    with open('cars_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    vehicles = data.get('vehicles', [])
    fixed = [fix_vehicle(v) for v in vehicles]
    data['vehicles'] = fixed
    with open('cars_data_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Eksik alanlar tamamlandı, cars_data_fixed.json dosyasına kaydedildi.')

if __name__ == '__main__':
    main()
