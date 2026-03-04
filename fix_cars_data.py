import re
import json

# Kaynak dosya ve hedef dosya
INPUT = 'cars_data.json'
OUTPUT = 'cars_data_cleaned.json'

# Tüm araçları yakalayacak regex (her bir { ile başlayan ve } ile biten blok)
vehicle_pattern = re.compile(r'\{[^{}]*?"id"\s*:\s*"[0-9A-Za-z]+"[\s\S]*?\}(?=,|\])', re.MULTILINE)

with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

# Tüm araç bloklarını bul
vehicles = vehicle_pattern.findall(raw)

cleaned_vehicles = []
for v in vehicles:
    try:
        # Virgül sorunlarını düzelt
        v_fixed = v.strip().rstrip(',')
        # JSON olarak parse et
        obj = json.loads(v_fixed)
        cleaned_vehicles.append(obj)
    except Exception as e:
        continue

# regions alanını otomatik oluştur
regions = {"Çayırova": [], "Gebze": [], "DerÇiftliği": [], "İzmit": [], "Diğer": []}
for v in cleaned_vehicles:
    region = v.get('location', {}).get('region', 'Diğer')
    if region not in regions:
        regions[region] = []
    regions[region].append(v.get('id'))

# Sonuç JSON'u oluştur
result = {
    "vehicles": cleaned_vehicles,
    "regions": regions
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Temizlenen araç sayısı: {len(cleaned_vehicles)}")
print(f"Çıktı dosyası: {OUTPUT}")
