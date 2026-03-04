import re
import json

with open('cars_data.json.bak', 'r', encoding='utf-8') as f:
    raw = f.read()

# 1. publishDate ve daysListed hatalarını düzelt
raw = re.sub(r',`n\s+"daysListed":\s*([0-9]+),', r', "daysListed": \1,', raw)

# 2. Property anahtarlarını çift tırnaklı yap
raw = re.sub(r'([,{\s])([a-zA-Z0-9_]+):', r'\1"\2":', raw)

# 3. Fazladan karakterleri ve satır sonu hatalarını kaldır
raw = raw.replace('`n', '')

# 4. JSON dosyasının sonunu doğru kapat
if raw.count('{') > raw.count('}'):
    raw += '}'
if raw.count('[') > raw.count(']'):
    raw += ']'

# 5. Geçerli JSON olup olmadığını kontrol et
try:
    data = json.loads(raw)
    with open('cars_data_final.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('cars_data_final.json dosyası geçerli JSON olarak kaydedildi.')
except Exception as e:
    with open('cars_data_final_invalid.json', 'w', encoding='utf-8') as f:
        f.write(raw)
    print('JSON format hatası devam ediyor:', e)
