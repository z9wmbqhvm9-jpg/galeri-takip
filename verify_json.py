import json

data = json.load(open('cars_data.json', encoding='utf-8'))
print('✅ JSON geçerli!')
print('📊 Toplam araç:', len(data['vehicles']))
print()
for v in data['vehicles']:
    print(f"✓ {v['vehicle']['year']} {v['vehicle']['brand']} {v['vehicle']['model']}: {v['publishDate']}, {v['daysListed']} gün")
