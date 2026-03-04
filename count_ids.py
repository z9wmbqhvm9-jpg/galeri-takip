import re
import json

with open('cars_data_fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

ids = re.findall(r'"id"\s*:\s*"(\d+)"', text)
unique = set(ids)
print('Toplam id bulundu:', len(ids))
print('Benzersiz id:', len(unique))

adnos = re.findall(r'"adNo"\s*:\s*"?(\d+)"?', text)
unique2 = set(adnos)
print('adNo toplam:', len(adnos), 'benzersiz:', len(unique2))

ilan_nos = re.findall(r'"ilan_no"\s*:\s*"(\d+)"', text)
unique3 = set(ilan_nos)
print('ilan_no toplam:', len(ilan_nos), 'benzersiz:', len(unique3))

all_ids = unique | unique2 | unique3
print('TUM BENZERSIZ ID:', len(all_ids))

# Tum json dosyalarindaki benzersiz ID'leri say
import os
all_global_ids = set()
for fname in sorted(os.listdir('.')):
    if not fname.endswith('.json'):
        continue
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        found_ids = set(re.findall(r'"(?:id|adNo|ilan_no|İlan No)"\s*:\s*"?(\d{7,})"?', content))
        all_global_ids |= found_ids
        if found_ids:
            print(f'{fname}: {len(found_ids)} benzersiz ID')
    except:
        pass

print(f'\nTUM DOSYALARDAKI TOPLAM BENZERSIZ ID: {len(all_global_ids)}')
