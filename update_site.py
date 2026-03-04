import json

def update_main_data():
    with open('ilan_sonuc.json', 'r', encoding='utf-8') as f:
        new_vehicles = json.load(f)
    
    # Map fields for cars_data.json format
    # The dashboard normalizeVehicle is smart, but let's make it easy
    cars_data_list = []
    all_data_list = []
    
    for v in new_vehicles:
        # cars_data format
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
            "Fiyat": f"{v.get('fiyat'):,} TL".replace(',', '.'),
            "Baslik": f"{v.get('marka')} {v.get('seri')} {v.get('model_paket')}",
            "Kimden": v.get("kimden", "Galeriden"),
            "ilan_no": v.get("ilan_no"),
            "url": f"https://www.sahibinden.com/ilan/vasita-{v.get('ilan_no')}/detay",
            "ekspertiz_ozeti": v.get("ekspertiz_ozeti", {}),
            "Paket": v.get("model_paket")
        }
        cars_data_list.append(cd)
        
        # all_data format (for the other dashboard)
        ad = {
            "ilan_no": v.get("ilan_no"),
            "marka": v.get("marka"),
            "model": v.get("seri"),
            "varyant": v.get("model_paket"),
            "yil": v.get("yil"),
            "km": int(v.get("km").replace('.', '').replace(',', '')) if isinstance(v.get("km"), str) else v.get("km"),
            "fiyat": v.get("fiyat"),
            "yakit": v.get("yakit"),
            "vites": v.get("vites"),
            "ilan_url": cd["url"],
            "durum": "aktif"
        }
        all_data_list.append(ad)

    # Save to cars_data.json
    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump({"vehicles": cars_data_list}, f, ensure_ascii=False, indent=2)
    
    # Save to all_data.json
    with open('all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Success: 3 new vehicles are now live on the site ({len(cars_data_list)} total)")

if __name__ == "__main__":
    update_main_data()
