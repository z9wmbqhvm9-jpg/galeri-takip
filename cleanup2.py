import json

data = json.load(open('cars_data.json', encoding='utf-8'))

# Son araçı kaldır (duplicate)
if len(data['vehicles']) > 11:
    last_id = data['vehicles'][-1]['id']
    data['vehicles'] = data['vehicles'][:-1]
    
    # Region'dan da kaldır
    for region in data['regions']:
        if last_id in data['regions'][region]:
            data['regions'][region].remove(last_id)

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Duplicate silindi! Toplam araç: {len(data['vehicles'])}")
