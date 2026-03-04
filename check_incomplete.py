import json

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

vehicles = data['vehicles']

standard_parts = ['Kaput', 'Tavan', 'Ön Tampon', 'Arka Tampon', 
                  'Sağ Ön Çamurluk', 'Sol Ön Çamurluk',
                  'Sağ Ön Kapı', 'Sol Ön Kapı',
                  'Sağ Arka Kapı', 'Sol Arka Kapı',
                  'Sağ Arka Çamurluk', 'Sol Arka Çamurluk',
                  'Bagaj Kapağı']

structural_parts = ['Şase', 'Podye', 'Kule', 'Direk', 'Airbag', 'Bagaj Havuzu']

incomplete = []

for i, v in enumerate(vehicles):
    vehicle_id = v.get('adNo', 'N/A')
    brand = v.get('vehicle', {}).get('brand', '')
    model = v.get('vehicle', {}).get('model', '')
    year = v.get('vehicle', {}).get('year', '')
    inspection = v.get('inspection', {})
    
    # Eski format atla
    has_old_format = any(key in inspection for key in ['frontBumper', 'leftFender', 'hood', 'rightRearDoor'])
    if has_old_format:
        continue
    
    # Eksik parça kontrolü
    missing_parts = []
    for part in standard_parts + structural_parts:
        if part not in inspection:
            missing_parts.append(part)
    
    if missing_parts:
        incomplete.append({
            'index': i+1,
            'id': vehicle_id,
            'name': f'{year} {brand} {model}',
            'missing': len(missing_parts)
        })

print('EKSİK DETAYLI ARAÇLAR:')
print('='*70)
for item in incomplete:
    print(f"{item['index']:2}. {item['id']} - {item['name']:40} ({item['missing']:2} parça eksik)")

print('\n' + '='*70)
print(f'Toplam: {len(incomplete)} araçta eksik detay var')
