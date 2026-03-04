import json
import re

# We will manually parse the 3 listings in ilan_metni.txt and update cars_data.json

updates = {
    "1301761057": {
        "ekspertiz_ozeti": {
            "boya": ["Sağ Arka Kapı", "Sağ Arka Çamurluk"],
            "degisen": ["Bagaj Kapağı"],
            "tramer": "34 Bin TL",
            "lokal_boya": ["Motor Kaputu", "Sol Arka Çamurluk"]
        }
    },
    "1301754916": {
        "ekspertiz_ozeti": {
            "boya": [],
            "degisen": ["Sol Arka Kapı", "Sol Ön Kapı (Sök-Tak)"],
            "tramer": "8200 TL",
            "lokal_boya": ["Sol Arka Çamurluk"]
        }
    },
    "1301743539": {
        "ekspertiz_ozeti": {
            "boya": [],
            "degisen": ["Sol Ön Çamurluk", "Kaput (Sök-Tak)"],
            "tramer": "0 TL",
            "lokal_boya": ["Sağ Ön Çamurluk"]
        }
    }
}

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for v in data.get('vehicles', []):
    ilan_no = v.get('ilan_no')
    if ilan_no in updates:
        # We merge or replace the ekspertiz_ozeti
        v['ekspertiz_ozeti'] = updates[ilan_no]['ekspertiz_ozeti']
        print(f"Updated {ilan_no}")

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done updating cars_data.json. Next step is syncing to all_data.json if needed.")
