import json

def merge_fragments():
    # Load fragmented data from the user
    fragments = [
        {"name": "BATUHAN KAYA OTOMOTİV", "type": "Galeri", "phone": "(530) 384 93 00", "url": "https://batuhankayaotomotiv.sahibinden.com/"},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": "Çayırova Mh."},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": True},
        {"frontBumper": "Değişti", "leftFender": "Boyalı", "rightRearDoor": "Boyalı", "hood": "Değişen"},
        {"name": "GÜNDOĞDU OTOMOTİV", "type": "Galeri", "phone": "(541) 862 18 18", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Motor Kaputu": "Boyalı", "Sol Ön Çamurluk": "Boyalı", "Sol Arka Çamurluk": "Boyalı", "Tramer": "2.500 TL"},
        {"name": "Ömer Faruk Yeşilbaş", "type": "Galeri", "phone": "(542) 544 60 17", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Sağ Arka Çamurluk Ağzı": "Lokal Boyalı"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(543) 598 26 18", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Motor Kaputu": "Lokal Boyalı", "Sol Arka Kapı": "Lokal Boyalı", "Sağ Ön Çamurluk": "Boyalı", "Sol Ön Çamurluk": "Boyalı", "Sol Arka Çamurluk": "Boyalı", "Tramer": "5 Bin TL"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(543) 598 26 18", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Motor Kaputu": "Lokal Boyalı", "Sol Arka Çamurluk": "Lokal Boyalı", "Sağ Arka Kapı": "Boyalı", "Sağ Arka Çamurluk": "Boyalı", "Bagaj Kapağı": "Değişti", "Tramer": "34 Bin TL"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(535) 458 20 87", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Sol Arka Kapı": "Değişti", "Sol Arka Çamurluk": "Lokal Boyalı", "Tramer": "8200 TL"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(535) 458 20 87", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Sol Arka Kapı": "Değişti", "Sol Arka Çamurluk": "Lokal Boyalı"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(535) 458 20 87", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Sol Ön Çamurluk": "Değişti", "Sağ Ön Çamurluk": "Lokal Boyalı", "Kaput": "Söktaklı"},
        {"name": "GARANTİ OTOMOTİV", "type": "Galeri", "phone": "(535) 458 20 87", "url": ""},
        {"city": "Kocaeli", "district": "Çayırova", "region": "Çayırova", "neighborhood": ""},
        {"status": "İkinci El", "heavyDamaged": False, "warranty": False, "exchange": False},
        {"Motor Kaputu": "Boyalı", "Sağ Ön Çamurluk": "Boyalı", "Sağ Ön Kapı": "Boyalı", "Sol Ön Çamurluk": "Boyalı", "Bagaj Kapağı": "Boyalı", "Sağ Arka Çamurluk": "Lokal Boyalı", "Sol Arka Çamurluk": "Lokal Boyalı"}
    ]

    # Group every 4 objects
    sets = []
    for i in range(0, len(fragments), 4):
        group = fragments[i:i+4]
        combined = {}
        for obj in group:
            combined.update(obj)
        sets.append(combined)

    # These 9 vehicles are the ones we just added (IDs match order)
    target_ids = ["1302004975", "1940026587", "1940334985", "1941268701", "1941426096", "1941609108", "1941765888", "1941785769", "1941886543"]

    with open('cars_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vehicles = data.get('vehicles', [])
    
    for i, tid in enumerate(target_ids):
        if i >= len(sets): break
        details = sets[i]
        
        # Find the vehicle in our main list
        for v in vehicles:
            if v.get('ilan_no') == tid or v.get('İlan No') == tid:
                # Update info
                v['Kimden'] = details.get('name', v.get('Kimden'))
                
                # Expert summary
                boya = []
                degisen = []
                tramer = details.get('Tramer') or details.get('tramer') or ''
                
                for k, val in details.items():
                    if k in ['name', 'type', 'phone', 'url', 'city', 'district', 'region', 'neighborhood', 'status', 'heavyDamaged', 'warranty', 'exchange', 'Tramer', 'tramer']:
                        continue
                    if 'Boya' in str(val):
                        boya.append(k)
                    if 'Değiş' in str(val) or 'Sök' in str(val):
                        degisen.append(k)
                
                v['ekspertiz_ozeti'] = {
                    'boya': boya,
                    'degisen': degisen,
                    'tramer': tramer
                }
                break

    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump({"vehicles": vehicles}, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Success: Updated details for {len(sets)} vehicles.")

if __name__ == "__main__":
    merge_fragments()
