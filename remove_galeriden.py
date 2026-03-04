import json
import os

cars_data_file = 'cars_data.json'
all_data_file = 'all_data.json'

removed_ilan_nos = set()

# Process cars_data.json
if os.path.exists(cars_data_file):
    with open(cars_data_file, 'r', encoding='utf-8') as f:
        cars_data = json.load(f)
    
    if isinstance(cars_data, dict) and 'vehicles' in cars_data:
        original_len = len(cars_data['vehicles'])
        filtered_vehicles = []
        
        for item in cars_data['vehicles']:
            if item.get('Kimden', '') == 'Galeriden':
                if 'ilan_no' in item:
                    removed_ilan_nos.add(item['ilan_no'])
            else:
                filtered_vehicles.append(item)
        
        new_len = len(filtered_vehicles)
        if original_len != new_len:
            cars_data['vehicles'] = filtered_vehicles
            with open(cars_data_file, 'w', encoding='utf-8') as f:
                json.dump(cars_data, f, ensure_ascii=False, indent=2)
            print(f"Removed {original_len - new_len} 'Galeriden' items from {cars_data_file}.")
        else:
            print(f"No 'Galeriden' items found in {cars_data_file}.")
    else:
        print(f"Unexpected structure in {cars_data_file}.")

# Process all_data.json
if os.path.exists(all_data_file) and removed_ilan_nos:
    with open(all_data_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
        
    if isinstance(all_data, list):
        original_len = len(all_data)
        filtered_all_data = [item for item in all_data if item.get('ilan_no') not in removed_ilan_nos]
        new_len = len(filtered_all_data)
        
        if original_len != new_len:
            with open(all_data_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_all_data, f, ensure_ascii=False, indent=2)
            print(f"Removed {original_len - new_len} corresponding items from {all_data_file}.")
        else:
            print(f"No matching items to remove found in {all_data_file}.")
    else:
        print(f"Unexpected structure in {all_data_file}")
elif not removed_ilan_nos:
    print(f"No items were removed from cars_data.json, skipping {all_data_file}.")
