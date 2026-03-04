import json
import re

INPUT = 'cars_data.json.bak'
OUTPUT = 'cars_data.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

# Bozuk satırları düzelt
raw = re.sub(r'`n\s*"', ',\n"', raw)

# JSON olarak yüklemeyi dene
try:
    data = json.loads(raw)
    vehicles = data.get('vehicles', [])
    regions = data.get('regions', {})
except Exception:
    # JSON bozuksa, elle blokları ayıkla
    vehicles = []
    regions = {"Çayırova": [], "Gebze": [], "DerÇiftliği": [], "İzmit": [], "Diğer": []}
    vehicles_section = re.search(r'"vehicles"\s*:\s*\[(.*?)]\s*,\s*"regions"', raw, re.DOTALL)
    if vehicles_section:
        vehicles_raw = vehicles_section.group(1)
        blocks = re.findall(r'\{[\s\S]*?\}', vehicles_raw)
        for block in blocks:
            try:
                obj = json.loads(block)
                vehicles.append(obj)
            except Exception:
                continue
    regions_section = re.search(r'"regions"\s*:\s*\{[\s\S]*?\}\s*}', raw)
    if regions_section:
        regions_str = '{' + regions_section.group(0).split('{',1)[1]
        try:
            regions = json.loads(regions_str)
        except Exception:
            pass

# Sonuç dosyasını yaz
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump({"vehicles": vehicles, "regions": regions}, f, ensure_ascii=False, indent=2)

print(f"Toplam araç: {len(vehicles)}")
print(f"Çıktı dosyası: {OUTPUT}")
