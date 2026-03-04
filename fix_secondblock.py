import re
import json

with open('cars_data.json.bak', 'r', encoding='utf-8') as f:
    raw = f.read()

# Sadece 201-434 arası satırları işle
lines = raw.splitlines()
block = '\n'.join(lines[200:434])

# publishDate ve daysListed hatalarını düzelt
block = re.sub(r'"publishDate":\s*"([0-9\-]+)",`n\s+"daysListed":\s*([0-9]+),', r'"publishDate": "\1", "daysListed": \2,', block)

# Fazladan karakterleri kaldır
block = block.replace('`n', '')

# JSON dosyasının sonunu doğru kapat
if block.count('{') > block.count('}'):
    block += '}'
if block.count('[') > block.count(']'):
    block += ']'

# Geçerli JSON olup olmadığını kontrol et
try:
    data = json.loads(block)
    with open('cars_data_secondblock.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('cars_data_secondblock.json dosyası geçerli JSON olarak kaydedildi.')
except Exception as e:
    with open('cars_data_secondblock_invalid.json', 'w', encoding='utf-8') as f:
        f.write(block)
    print('JSON format hatası devam ediyor:', e)
