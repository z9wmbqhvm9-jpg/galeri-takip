import json
import re

INPUT = 'cars_data.json.bak'
OUTPUT = 'cars_data_cleaned.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

# Bazı satırlarda \`n    "daysListed": 1, gibi bozukluklar var, düzelt
raw = re.sub(r'`n\s*"', ',\n"', raw)

# "vehicles": [ ile "regions": { arasını al
vehicles_section = re.search(r'"vehicles"\s*:\s*\[(.*?)]\s*,\s*"regions"', raw, re.DOTALL)
if vehicles_section:
    vehicles_raw = vehicles_section.group(1)
    # Her bir { ... } blokunu bul
    blocks = re.findall(r'\{[\s\S]*?\}', vehicles_raw)
    vehicles = []
    for block in blocks:
        try:
            obj = json.loads(block)
            vehicles.append(obj)
        except Exception:
            continue
else:
    vehicles = []

# regions alanını bul
regions_section = re.search(r'"regions"\s*:\s*\{[\s\S]*?\}\s*}', raw)
if regions_section:
    regions_str = '{' + regions_section.group(0).split('{',1)[1]
    try:
        regions = json.loads(regions_str)
    except Exception:
        regions = {"Çayırova": [], "Gebze": [], "DerÇiftliği": [], "İzmit": [], "Diğer": []}
else:
    regions = {"Çayırova": [], "Gebze": [], "DerÇiftliği": [], "İzmit": [], "Diğer": []}

result = {
    "vehicles": vehicles,
    "regions": regions
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Temizlenen araç sayısı: {len(vehicles)}")
print(f"Çıktı dosyası: {OUTPUT}")
