import json
data = json.load(open('cars_data.json', encoding='utf-8'))
corolla = [v for v in data['vehicles'] if v['vehicle']['brand'] == 'Toyota' and v['vehicle']['year'] == 2014][0]
print(f"Bölge: {corolla['location']['region']}")
print(f"İlan No: {corolla['id']}")
print(f"Tarih: {corolla['publishDate']}, {corolla['daysListed']} gün")
print(f"Galeri: {corolla['seller']['name']}")
