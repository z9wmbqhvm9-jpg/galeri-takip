import json
import glob
import os

# List all cars_data*.json files except the output file
files = glob.glob('cars_data*.json')
output_file = 'cars_data.json'
if output_file in files:
    files.remove(output_file)

all_vehicles = {}

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Try to get vehicles list
            vehicles = data.get('vehicles')
            if not vehicles:
                continue
            for v in vehicles:
                # Some files may have partial/invalid records, skip if no id
                vid = v.get('id') or v.get('adNo')
                if not vid:
                    continue
                # Deduplicate by id
                all_vehicles[vid] = v
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Write merged vehicles to cars_data.json
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({'vehicles': list(all_vehicles.values())}, f, ensure_ascii=False, indent=2)

print(f"Merged {len(all_vehicles)} unique vehicles from {len(files)} files into {output_file}")
