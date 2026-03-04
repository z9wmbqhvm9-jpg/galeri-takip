import json

with open('cars_data_cleaned.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('cars_data.json dosyası güncellendi ve temizlendi!')
