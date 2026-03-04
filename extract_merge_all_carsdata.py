import json
import glob
import re

# Helper to extract all valid vehicle objects from a file, even if the file is broken

def extract_vehicles_from_file(filepath):
    vehicles = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            # Find all objects that look like vehicles
            # This regex matches { ... } blocks that contain 'adNo' or 'id'
            pattern = re.compile(r'\{[^\{\}]*?(?:"id"|"adNo")[^\{\}]*?\}', re.DOTALL)
            for match in pattern.finditer(text):
                try:
                    obj = json.loads(match.group(0))
                    vehicles.append(obj)
                except Exception:
                    continue
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return vehicles

files = glob.glob('cars_data*.json')
output_file = 'cars_data.json'
if output_file in files:
    files.remove(output_file)

all_vehicles = {}

for file in files:
    vehicles = extract_vehicles_from_file(file)
    for v in vehicles:
        vid = v.get('id') or v.get('adNo')
        if not vid:
            continue
        all_vehicles[vid] = v

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({'vehicles': list(all_vehicles.values())}, f, ensure_ascii=False, indent=2)

print(f"Extracted and merged {len(all_vehicles)} unique vehicles from {len(files)} files into {output_file}")
