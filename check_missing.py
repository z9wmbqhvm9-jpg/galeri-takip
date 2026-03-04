import json

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = 0
for v in data.get('vehicles', []):
    e = v.get('ekspertiz_ozeti', {})
    boya = e.get('boya', [])
    degisen = e.get('degisen', [])
    tramer = e.get('tramer', '')
    
    if not boya and not degisen and not tramer:
        missing += 1

print(f"Empty damage info count: {missing}")
