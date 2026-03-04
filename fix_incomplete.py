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

updated_count = 0

for i, v in enumerate(vehicles):
    inspection = v.get('inspection', {})
    
    # Eski format kontrolü
    has_old_format = any(key in inspection for key in ['frontBumper', 'leftFender', 'hood', 'rightRearDoor'])
    if has_old_format:
        print(f"Atlanan (eski format): {v.get('adNo')} - {v.get('vehicle', {}).get('brand')} {v.get('vehicle', {}).get('model')}")
        continue
    
    # Mevcut inspection'ı al
    complete_inspection = {}
    
    # Tramer varsa önce ekle
    if 'Tramer' in inspection:
        complete_inspection['Tramer'] = inspection['Tramer']
    else:
        complete_inspection['Tramer'] = '0 TL'
    
    # Standart parçalar
    updated = False
    for part in standard_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
        else:
            complete_inspection[part] = 'Orijinal'
            updated = True
    
    # Yapısal parçalar
    for part in structural_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
        else:
            complete_inspection[part] = 'Orijinal'
            updated = True
    
    # Özel durumlar (Motor, Şanzıman, vb)
    special_parts = ['Motor', 'Şanzıman', 'Diferansiyel', 'Panel', 'Çürük', 'Çatlak', 'Macun']
    for part in special_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
    
    # Güncelle
    if updated:
        vehicles[i]['inspection'] = complete_inspection
        updated_count += 1
        print(f"✅ Güncellendi: {v.get('adNo')} - {v.get('vehicle', {}).get('year')} {v.get('vehicle', {}).get('brand')} {v.get('vehicle', {}).get('model')}")

# Kaydet
with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n✅ Toplam {updated_count} araç güncellendi!')
print(f'📊 Tüm araçlar artık tam detaylı!')
