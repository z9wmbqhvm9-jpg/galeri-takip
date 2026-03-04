import json

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Tüm araçları kontrol et
for vehicle in data['vehicles']:
    if vehicle['publishDate'] == '2026-02-23':
        vehicle['daysListed'] = 1
    elif vehicle['publishDate'] == '2026-02-24':
        vehicle['daysListed'] = 0

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ Tüm tarihler düzeltildi!')
