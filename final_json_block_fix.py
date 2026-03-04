import re
import json

with open('cars_data_fixed_clean.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 1. Hatalı blokları düzelt: publishDate ve daysListed aynı blokta olmamalı
raw = re.sub(r'("publishDate":\s*"[0-9\-]+",\s*)"daysListed":\s*([0-9]+),', r'\1\n      "daysListed": \2,', raw)

# 2. Hatalı property anahtarlarını düzelt
raw = re.sub(r'([,{\s])([a-zA-Z0-9_]+):', r'\1"\2":', raw)

# 3. Çift çift tırnakları düzelt
raw = raw.replace('""', '"')

# 4. Fazladan karakterleri ve satır sonu hatalarını kaldır
raw = raw.replace('`n', '')

# 5. JSON dosyasının sonunu doğru kapat
if raw.count('{') > raw.count('}'):
    raw += '}'
if raw.count('[') > raw.count(']'):
    raw += ']'

# 6. Geçerli JSON olup olmadığını kontrol et
try:
    data = json.loads(raw)
    with open('cars_data_final.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('cars_data_final.json dosyası geçerli JSON olarak kaydedildi.')
except Exception as e:
    with open('cars_data_final_invalid.json', 'w', encoding='utf-8') as f:
        f.write(raw)
    print('JSON format hatası devam ediyor:', e)
