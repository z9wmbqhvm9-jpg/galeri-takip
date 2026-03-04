import re

with open('cars_data_fixed.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Hatalı publishDate satırlarını düzelt
    line = re.sub(r',`n\s+"daysListed":\s*([0-9]+),', r', "daysListed": \1,', line)
    # Tek tırnakları çift tırnak yap
    line = line.replace("'", '"')
    # Fazladan karakterleri kaldır
    line = line.replace('`n', '')
    # Property keyleri çift tırnaklı yap
    line = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', line)
    fixed_lines.append(line)

# Sonunda fazladan kod varsa kapat
raw = ''.join(fixed_lines)
if raw.count('{') > raw.count('}'):
    raw += '}'
if raw.count('[') > raw.count(']'):
    raw += ']'

with open('cars_data_fixed_clean.json', 'w', encoding='utf-8') as f:
    f.write(raw)

print('cars_data_fixed_clean.json dosyası satır satır otomatik olarak düzeltildi.')
