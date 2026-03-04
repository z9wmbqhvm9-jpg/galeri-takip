import json

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

unique_ids = set()
unique_ads = set()
filtered_vehicles = []

for vehicle in data['vehicles']:
    vid = vehicle.get('id')
    adno = vehicle.get('adNo')
    if vid in unique_ids or adno in unique_ads:
        continue  # Skip duplicates
    unique_ids.add(vid)
    unique_ads.add(adno)
    filtered_vehicles.append(vehicle)

# Save filtered vehicles
with open('cars_data_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump({'vehicles': filtered_vehicles}, f, ensure_ascii=False, indent=2)

print(f"Toplam {len(filtered_vehicles)} benzersiz araç kaydedildi.")
