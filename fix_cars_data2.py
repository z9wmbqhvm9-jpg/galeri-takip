import json
import re

INPUT = 'cars_data.json'
OUTPUT = 'cars_data_cleaned.json'

# Tüm { ile } arası blokları bul, "id": ile başlayanları filtrele
with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

# Her bir { ... } blokunu bul
blocks = re.findall(r'\{[\s\S]*?\}', raw)
vehicles = []
for block in blocks:
    if '"id"' in block and '"vehicle"' in block and '"seller"' in block:
        try:
            # Sonunda fazladan virgül varsa kaldır
            block_clean = block.rstrip(',')
            obj = json.loads(block_clean)
            vehicles.append(obj)
        except Exception:
            continue

# regions alanını otomatik oluştur
regions = {"Çayırova": [], "Gebze": [], "DerÇiftliği": [], "İzmit": [], "Diğer": []}
for v in vehicles:
    region = v.get('location', {}).get('region', 'Diğer')
    if region not in regions:
        regions[region] = []
    regions[region].append(v.get('id'))

result = {
    "vehicles": vehicles,
    "regions": regions
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Temizlenen araç sayısı: {len(vehicles)}")
print(f"Çıktı dosyası: {OUTPUT}")
