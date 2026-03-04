import json

updates = {
    "1300745923": {
        "ekspertiz_ozeti": {
            "boya": ["Bagaj Kapağı"],
            "degisen": [],
            "tramer": ""
        }
    },
    "1297813431": {
        "ekspertiz_ozeti": {
            "boya": [],
            "degisen": [],
            "tramer": "0 TL (Yok)"
        }
    }
}

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for v in data.get('vehicles', []):
    ilan_no = v.get('ilan_no')
    if ilan_no in updates:
        v['ekspertiz_ozeti'] = updates[ilan_no]['ekspertiz_ozeti']
        print(f"Updated {ilan_no}")

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("cars_data.json is updated successfully.")
