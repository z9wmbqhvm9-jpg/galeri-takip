import re
import json

with open('cars_data.json.bak', 'r', encoding='utf-8') as f:
    raw = f.read()

# Araç nesnelerini tek tek ayıkla
vehicle_blocks = re.findall(r'\{[^\{\}]*?"id":\s*"[0-9A-Za-z]+"[\s\S]*?\}\s*[,\]]', raw)

vehicles = []
for block in vehicle_blocks:
    # publishDate ve daysListed hatalarını düzelt
    block = re.sub(r'"publishDate":\s*"([0-9\-]+)",`n\s+"daysListed":\s*([0-9]+),', r'"publishDate": "\1", "daysListed": \2,', block)
    block = block.replace('`n', '')
    try:
        vehicle = json.loads(block.rstrip(',]'))
        vehicles.append(vehicle)
    except Exception as e:
        print('Hatalı araç bloğu atlandı:', e)

# Geçerli araçları tek bir JSON dosyasında birleştir
with open('cars_data_cleaned_all.json', 'w', encoding='utf-8') as f:
    json.dump({'vehicles': vehicles}, f, ensure_ascii=False, indent=2)

print(f'{len(vehicles)} adet geçerli araç kaydedildi. cars_data_cleaned_all.json oluşturuldu.')
