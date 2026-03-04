import json
from datetime import datetime

# Okunacak ve yazılacak dosya
INPUT = "cars_data.json"
OUTPUT = "cars_data_dashboard_ready.json"

# Tabloya uygun alanlar
TABLE_FIELDS = [
    ("İlan No", ["İlan No", "ilan_no", "id"]),
    ("Tarih", ["İlan Tarihi", "tarih", "date", "ilk_gorulme"]),
    ("Marka", ["Marka", "marka", "brand"]),
    ("Model", ["Model", "model"]),
    ("Yıl", ["Yıl", "yil", "Yıl", "yil", "Üretim Yılı"]),
    ("Yakıt", ["Yakıt Tipi", "yakit", "Yakıt", "yakıt"]),
    ("Vites", ["Vites", "vites"]),
    ("Renk", ["Renk", "renk"]),
    ("KM", ["KM", "km"]),
    ("Fiyat", ["Fiyat", "fiyat"]),
    ("Galeri", ["Galeri", "galeri", "Kimden", "kimden", "seller", "seller.name"]),
    ("Durum", ["Araç Durumu", "durum", "status"]),
    ("Link", ["url", "ilan_url"])
]

# Alanları birleştirici fonksiyon
def extract_field(vehicle, keys):
    for key in keys:
        # seller.name gibi iç içe anahtarlar
        if "." in key:
            parts = key.split(".")
            val = vehicle
            for p in parts:
                if isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    val = None
                    break
            if val:
                return val
        elif key in vehicle:
            return vehicle[key]
    return "-"

def convert_date(val):
    # Tarih formatını standartlaştır
    if isinstance(val, str):
        try:
            if "-" in val and ":" in val:
                return val.split()[0]
            elif "." in val:
                return datetime.strptime(val, "%d.%m.%Y").strftime("%d.%m.%Y")
            elif " " in val:
                return val.split()[0]
            else:
                return val
        except:
            return val
    return val

def main():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = data["vehicles"] if "vehicles" in data else data
    table = []
    for v in vehicles:
        row = {}
        for col, keys in TABLE_FIELDS:
            val = extract_field(v, keys)
            if col == "Tarih":
                val = convert_date(val)
            row[col] = val
        table.append(row)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"{len(table)} araç tabloya uygun şekilde kaydedildi: {OUTPUT}")

if __name__ == "__main__":
    main()
