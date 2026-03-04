#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

# Kasa tipleri hangisi olduğunu belirle
body_types = {
    "1302004975": "Sedan",      # Renault Symbol
    "1940026587": "Sedan",      # Honda Civic
    "1940334985": "Sedan",      # Toyota Corolla
    "1941268701": "Sedan",      # Citroen C-Elysée
    "1941426096": "Hatchback",  # Renault Clio
    "1941609108": "Hatchback",  # Renault Clio
    "1941765888": "Hatchback",  # Renault Clio
    "1941785769": "Sedan",      # Citroen C-Elysée
    "1941886543": "Sedan",      # Peugeot 301
    "1942709795": "Hatchback",  # Renault Clio
    "1943397644": "Sedan",      # Toyota Corolla
    "1301643996": "Sedan",      # Honda Civic
    "1943397644": "Sedan",      # Honda Civic (duplicate id)
    "1301094350": "Hatchback",  # Renault Clio Touch
    "1301522563": "Hatchback"   # Hyundai i20
}

with open('cars_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for vehicle in data['vehicles']:
    vehicle_id = vehicle['id']
    if vehicle_id in body_types:
        vehicle['vehicle']['body_type'] = body_types[vehicle_id]
    else:
        vehicle['vehicle']['body_type'] = 'Sedan'  # Varsayılan

with open('cars_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Tüm araçlara Kasa Tipi eklendi!")
print("📊 Toplam araç:", len(data['vehicles']))
for v in data['vehicles']:
    print(f"✓ {v['vehicle']['year']} {v['vehicle']['brand']} {v['vehicle']['model']}: {v['vehicle']['body_type']}")
