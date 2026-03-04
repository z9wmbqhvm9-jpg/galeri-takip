import json
import re

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for v in data.get('vehicles', []):
    e = v.get('ekspertiz_ozeti', {})
    boya = e.get('boya', [])
    degisen = e.get('degisen', [])
    
    # If both are empty, check if description mentions damage
    if not boya and not degisen:
        desc = v.get('Aciklama', '').lower()
        if desc and re.search(r'boya|değişen|degisen|lokal|tramer|hasar', desc):
            count += 1
            if count <= 3:
                print(f"Ilan: {v.get('ilan_no')}")
                print(f"Ekspertiz: {e}")
                print(f"Desc Snippet: {desc[:200]}...")
                print('-'*40)

print(f'Listings with empty damage arrays but damage keywords in description: {count}')
