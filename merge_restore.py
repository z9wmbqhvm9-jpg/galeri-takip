import json

def merge_all_data():
    # 1. Load backup (the 38 vehicles)
    try:
        with open('cars_data_backup_before_clear.json', 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            vehicles_list = backup_data.get('vehicles', [])
    except:
        vehicles_list = []

    # 2. Load new ones (the 3 from ilan_sonuc.json)
    try:
        with open('ilan_sonuc.json', 'r', encoding='utf-8') as f:
            new_vehicles_raw = json.load(f)
    except:
        new_vehicles_raw = []

    # Map the 3 new ones to cars_data format
    for v in new_vehicles_raw:
        # Check if already in list (avoid duplicates)
        if any(x.get('ilan_no') == v.get('ilan_no') for x in vehicles_list):
            continue
            
        cd = {
            "İlan No": v.get("ilan_no"),
            "İlan Tarihi": v.get("ilan_tarihi"),
            "Marka": v.get("marka"),
            "Seri": v.get("seri"),
            "Model": v.get("model_paket"),
            "Yıl": str(v.get("yil")),
            "Yakıt Tipi": v.get("yakit"),
            "Vites": v.get("vites"),
            "KM": v.get("km"),
            "Fiyat": f"{v.get('fiyat'):,} TL".replace(',', '.') if isinstance(v.get('fiyat'), int) else v.get('fiyat'),
            "Baslik": f"{v.get('marka')} {v.get('seri')} {v.get('model_paket')}",
            "Kimden": v.get("kimden", "Galeriden"),
            "ilan_no": v.get("ilan_no"),
            "url": f"https://www.sahibinden.com/ilan/vasita-{v.get('ilan_no')}/detay",
            "ekspertiz_ozeti": v.get("ekspertiz_ozeti", {}),
            "Paket": v.get("model_paket")
        }
        vehicles_list.append(cd)

    # 3. Save to cars_data.json
    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump({"vehicles": vehicles_list}, f, ensure_ascii=False, indent=2)

    # 4. Update all_data.json (unified list for everything)
    all_data_list = []
    for v in vehicles_list:
        # Convert to all_data format
        ad = {
            "ilan_no": v.get("ilan_no") or v.get("İlan No"),
            "marka": v.get("Marka") or v.get("marka"),
            "model": v.get("Seri") or v.get("model"),
            "varyant": v.get("Model") or v.get("Paket") or v.get("varyant"),
            "yil": int(v.get("Yıl")) if str(v.get("Yıl", "")).isdigit() else v.get("yil"),
            "km": v.get("KM") or v.get("km"),
            "fiyat": v.get("Fiyat") or v.get("fiyat"),
            "yakit": v.get("Yakıt Tipi") or v.get("yakit"),
            "vites": v.get("Vites") or v.get("vites"),
            "ilan_url": v.get("url") or v.get("ilan_url"),
            "durum": "aktif"
        }
        all_data_list.append(ad)

    with open('all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data_list, f, ensure_ascii=False, indent=2)

    print(f"✅ Success: Merged {len(vehicles_list)} vehicles total.")

if __name__ == "__main__":
    merge_all_data()
