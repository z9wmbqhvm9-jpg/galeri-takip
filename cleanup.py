import json

data = json.load(open('cars_data.json', encoding='utf-8'))

# Son 2 araç 2014 Corolla - ikincisini kaldır (boş brand olanı)
filtered_vehicles = [v for v in data['vehicles'] if v['vehicle']['brand'] != '']

# Region arraylerini güncelle
for region in data['regions']:
    data['regions'][region] = [id for id in data['regions'][region] if id in [v['id'] for v in filtered_vehicles]]

data['vehicles'] = filtered_vehicles

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Temizlendi! Toplam araç: {len(data['vehicles'])}")
