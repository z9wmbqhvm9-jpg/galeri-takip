"""
BÜYÜK BOZUK JSON DOSYASINI PARSE ET
cars_data_fixed.json dosyasi birden fazla JSON yapistirmasi.
Her arac { "id": ... } ile basliyor. Bunlari regex ile ayir ve parse et.
"""
import json
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def parse_broken_file(path):
    """Parcalanmis JSON dosyasindaki araclari bul"""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    vehicles = []
    
    # Strateji: "id": "XXXX" kaliplarini bul, sonra o bloku JSON olarak parse et
    # Split by { ile baslayan ve "id" iceren bloklara
    
    # Oncelikle { ... } bloklarini dengeli sekilde bul
    # Ama bazi bloklar bozuk. O yuzden alternatif:
    # JSON objelerini bir bir dene
    
    # Pattern: Her arac {"id": veya {  "id": ile baslar
    # Bunlarin pozisyonlarini bul
    starts = [m.start() for m in re.finditer(r'\{\s*\n?\s*"id"\s*:', text)]
    
    print(f'  {os.path.basename(path)}: {len(starts)} arac baslangici bulundu')
    
    for idx, start_pos in enumerate(starts):
        # End pozisyonu: ya sonraki start, ya da dosya sonu
        end_limit = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        
        chunk = text[start_pos:end_limit]
        
        # Bu chunk icinden dengeli { } blogu bul
        depth = 0
        end_pos = 0
        for i, ch in enumerate(chunk):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end_pos = i + 1
                    break
        
        if end_pos > 0:
            block = chunk[:end_pos]
            try:
                obj = json.loads(block)
                if isinstance(obj, dict) and ('id' in obj or 'adNo' in obj):
                    vehicles.append(obj)
            except json.JSONDecodeError:
                # Blok kendi icinde bozuk olabilir - basitlestirilmis parse dene
                # Gereksiz alanları al
                try:
                    # Duplicate key problemini handle et
                    # line 507: "daysListed": 9, sonra line 508: "publishDate": ... duplicate
                    # Bu aslında ilk JSON düzeyinde olan ama ikinci bir obje gibi açılan alanlar
                    # Bunları temizle
                    
                    # Strateji: vehicle objesini bul
                    vid = re.search(r'"id"\s*:\s*"(\d+)"', block)
                    vbrand = re.search(r'"brand"\s*:\s*"([^"]+)"', block)
                    vprice = re.search(r'"price"\s*:\s*(\d+)', block)
                    vyear = re.search(r'"year"\s*:\s*(\d+)', block)
                    vmodel = re.search(r'"model"\s*:\s*"([^"]+)"', block)
                    vfuel = re.search(r'"fuel"\s*:\s*"([^"]+)"', block)
                    vtrans = re.search(r'"transmission"\s*:\s*"([^"]+)"', block)
                    vcolor = re.search(r'"color"\s*:\s*"([^"]+)"', block)
                    vkm = re.search(r'"km"\s*:\s*(\d+)', block)
                    vpackage = re.search(r'"package"\s*:\s*"([^"]+)"', block)
                    vhp = re.search(r'"hp"\s*:\s*(\d+)', block)
                    vseller = re.search(r'"name"\s*:\s*"([^"]+)"', block)
                    vcity = re.search(r'"city"\s*:\s*"([^"]+)"', block)
                    vdistrict = re.search(r'"district"\s*:\s*"([^"]+)"', block)
                    vpublish = re.search(r'"publishDate"\s*:\s*"([^"]+)"', block)
                    vadurl = re.search(r'"adUrl"\s*:\s*"([^"]+)"', block)
                    
                    if vid and vbrand:
                        obj = {
                            'id': vid.group(1),
                            'adNo': vid.group(1),
                            'vehicle': {
                                'brand': vbrand.group(1) if vbrand else '',
                                'model': vmodel.group(1) if vmodel else '',
                                'year': int(vyear.group(1)) if vyear else 0,
                                'fuel': vfuel.group(1) if vfuel else '',
                                'transmission': vtrans.group(1) if vtrans else '',
                                'color': vcolor.group(1) if vcolor else '',
                                'km': int(vkm.group(1)) if vkm else 0,
                                'package': vpackage.group(1) if vpackage else '',
                                'hp': int(vhp.group(1)) if vhp else 0,
                            },
                            'price': int(vprice.group(1)) if vprice else 0,
                            'publishDate': vpublish.group(1) if vpublish else '',
                        }
                        if vadurl:
                            obj['adUrl'] = vadurl.group(1)
                        if vseller:
                            obj['seller'] = {'name': vseller.group(1)}
                        if vcity:
                            obj['location'] = {
                                'city': vcity.group(1),
                                'district': vdistrict.group(1) if vdistrict else ''
                            }
                        
                        # Inspection bilgilerini cek
                        inspection = {}
                        insp_patterns = re.findall(r'"((?:Boyalı|Değişen|Tramer|Lokal Boyalı|Durum|Boyalı Parçalar|Değişen Parçalar|Lokal Boyalı Parçalar)[^"]*?)"\s*:\s*"([^"]*)"', block)
                        for ik, iv in insp_patterns:
                            inspection[ik] = iv
                        
                        # Detaylı inspection (part-level)
                        part_patterns = re.findall(r'"((?:Kaput|Tavan|Ön Tampon|Arka Tampon|Sağ Ön Çamurluk|Sol Ön Çamurluk|Sağ Ön Kapı|Sol Ön Kapı|Sağ Arka Kapı|Sol Arka Kapı|Sağ Arka Çamurluk|Sol Arka Çamurluk|Bagaj Kapağı|Motor Kaputu|Şase|Podye|Kule|Direk|Airbag|Bagaj Havuzu)[^"]*?)"\s*:\s*"([^"]*)"', block)
                        for pk, pv in part_patterns:
                            inspection[pk] = pv
                        
                        if inspection:
                            obj['inspection'] = inspection
                        
                        # Description
                        vdesc = re.search(r'"description"\s*:\s*"([^"]*)"', block)
                        if vdesc:
                            obj['description'] = vdesc.group(1)
                        
                        # Features
                        features_match = re.search(r'"features"\s*:\s*\[(.*?)\]', block, re.DOTALL)
                        if features_match:
                            feat_text = features_match.group(1)
                            feats = re.findall(r'"([^"]+)"', feat_text)
                            obj['features'] = feats
                        
                        vehicles.append(obj)
                except Exception as e2:
                    pass
    
    print(f'  Toplam parse edilen arac: {len(vehicles)}')
    return vehicles


def normalize(v):
    res = {}
    ino = str(v.get('ilan_no') or v.get('İlan No') or v.get('id') or v.get('adNo') or '')
    if not ino:
        return None
    res['ilan_no'] = ino
    res['İlan No'] = ino
    
    veh = v.get('vehicle', {})
    if not isinstance(veh, dict):
        veh = {}
    
    marka = v.get('Marka') or v.get('marka') or v.get('brand') or veh.get('brand') or ''
    if not marka or marka == '-':
        return None
    res['Marka'] = marka
    res['Seri'] = v.get('Seri') or v.get('seri') or v.get('series') or v.get('model') or veh.get('model') or '-'
    res['Model'] = v.get('Model') or v.get('model_paket') or v.get('package') or veh.get('package') or '-'
    res['Yıl'] = str(v.get('Yıl') or v.get('yil') or v.get('year') or veh.get('year') or '-')
    km = v.get('KM') or v.get('km') or veh.get('km') or '-'
    res['KM'] = str(km)
    
    fiyat = v.get('Fiyat') or v.get('fiyat') or v.get('price') or '-'
    if isinstance(fiyat, (int, float)) and fiyat > 0:
        res['Fiyat'] = f"{int(fiyat):,} TL".replace(',', '.')
    else:
        fstr = str(fiyat).replace(' TL', '').replace('.', '').replace(',', '').strip()
        if fstr.isdigit() and int(fstr) > 0:
            res['Fiyat'] = f"{int(fstr):,} TL".replace(',', '.')
        else:
            res['Fiyat'] = str(fiyat)
    
    res['Yakıt Tipi'] = v.get('Yakıt Tipi') or v.get('yakit') or v.get('fuel') or veh.get('fuel') or '-'
    res['Vites'] = v.get('Vites') or v.get('vites') or v.get('gear') or veh.get('transmission') or '-'
    res['Renk'] = v.get('Renk') or v.get('renk') or v.get('color') or veh.get('color') or '-'
    res['İlan Tarihi'] = v.get('İlan Tarihi') or v.get('publishDate') or v.get('adDate') or '-'
    res['url'] = v.get('url') or v.get('adUrl') or v.get('ilan_url') or f"https://www.sahibinden.com/ilan/vasita-{ino}/detay"
    res['Baslik'] = v.get('Baslik') or f"{res['Marka']} {res['Seri']}"
    
    seller = v.get('seller', {})
    if not isinstance(seller, dict):
        seller = {}
    res['Kimden'] = v.get('Kimden') or v.get('sellerType') or seller.get('name') or 'Galeriden'
    res['Paket'] = v.get('Paket') or v.get('package') or veh.get('package') or res['Model']
    
    if 'ekspertiz_ozeti' in v:
        res['ekspertiz_ozeti'] = v['ekspertiz_ozeti']
    elif 'inspection' in v:
        insp = v['inspection']
        if isinstance(insp, dict):
            boya = []
            degisen = []
            tramer = ''
            for k, val in insp.items():
                sval = str(val)
                sk = k.lower()
                if sk == 'tramer':
                    tramer = sval
                elif 'boyalı' in sval.lower() or 'boya' in sval.lower():
                    boya.append(k)
                elif 'değiş' in sval.lower():
                    degisen.append(k)
            boyali_str = insp.get('Boyalı') or insp.get('Boyalı Parçalar') or ''
            if boyali_str and str(boyali_str) not in ('Yok', 'YOK', '-', ''):
                boya.append(str(boyali_str))
            degisen_str = insp.get('Değişen') or insp.get('Değişen Parçalar') or ''
            if degisen_str and str(degisen_str) not in ('Yok', 'YOK', '-', ''):
                degisen.append(str(degisen_str))
            if not tramer:
                tramer = str(insp.get('Tramer') or insp.get('tramer') or '')
            res['ekspertiz_ozeti'] = {'boya': boya, 'degisen': degisen, 'tramer': tramer}
        else:
            res['ekspertiz_ozeti'] = {'boya': [], 'degisen': [], 'tramer': ''}
    else:
        res['ekspertiz_ozeti'] = {'boya': [], 'degisen': [], 'tramer': ''}
    
    return res


def load_normal(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        elif isinstance(data, dict):
            vlist = data.get('vehicles', [])
            if isinstance(vlist, list):
                return [x for x in vlist if isinstance(x, dict)]
    except:
        pass
    return []


def main():
    all_vehicles = {}
    
    # 1) Önce normal JSON dosyalarını oku
    normal_files = [
        'all_data.json', 'all_data_backup_before_clear.json',
        'cars_data_backup_before_clear.json', 'cars_data_cleaned.json',
        'cars_data_dashboard_ready.json', 'cars_data_final.json',
        'cars_data_firstblock.json', 'ilan_sonuc.json', 'rich_data_input.json'
    ]
    
    print('=== NORMAL JSON DOSYALARI ===')
    for fname in normal_files:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            continue
        raw = load_normal(path)
        added = 0
        for v in raw:
            norm = normalize(v)
            if norm:
                ino = norm['ilan_no']
                size = len(json.dumps(v, ensure_ascii=False))
                if ino not in all_vehicles or size > all_vehicles[ino][1]:
                    all_vehicles[ino] = (norm, size)
                    added += 1
        print(f'  {fname}: {len(raw)} ham, {added} eklendi')
    
    print(f'\nNormal dosyalardan toplam: {len(all_vehicles)} benzersiz')
    
    # 2) Bozuk büyük dosyayi parse et
    print('\n=== BOZUK JSON DOSYALARI ===')
    broken_files = ['cars_data_fixed.json', 'cars_data_fixed_clean.json', 'cars_data_final_invalid.json', 'cars_data_secondblock_invalid.json']
    for bfname in broken_files:
        bpath = os.path.join(BASE, bfname)
        if not os.path.exists(bpath):
            continue
        sz = os.path.getsize(bpath)
        if sz < 100:
            continue
        print(f'\n  {bfname} ({sz:,} bytes) parse ediliyor...')
        broken_vehicles = parse_broken_file(bpath)
        added = 0
        for v in broken_vehicles:
            norm = normalize(v)
            if norm:
                ino = norm['ilan_no']
                size = len(json.dumps(v, ensure_ascii=False))
                if ino not in all_vehicles or size > all_vehicles[ino][1]:
                    all_vehicles[ino] = (norm, size)
                    added += 1
        print(f'  {bfname}: {added} yeni eklendi')
    
    # 3) Mevcut en güncel cars_data.json'ı da oku (en son)
    cd_path = os.path.join(BASE, 'cars_data.json')
    if os.path.exists(cd_path):
        raw = load_normal(cd_path)
        added = 0
        for v in raw:
            norm = normalize(v)
            if norm:
                ino = norm['ilan_no']
                size = len(json.dumps(v, ensure_ascii=False))
                if ino not in all_vehicles or size > all_vehicles[ino][1]:
                    all_vehicles[ino] = (norm, size)
                    added += 1
        print(f'\n  cars_data.json (mevcut): {len(raw)} ham, {added} eklendi')
    
    final_list = [entry[0] for entry in all_vehicles.values()]
    
    print(f'\n{"=" * 50}')
    print(f'TOPLAM BENZERSIZ ARAC: {len(final_list)}')
    print(f'{"=" * 50}')
    
    # Kaydet
    with open(os.path.join(BASE, 'cars_data.json'), 'w', encoding='utf-8') as f:
        json.dump({"vehicles": final_list}, f, ensure_ascii=False, indent=2)
    
    all_data = []
    for v in final_list:
        all_data.append({
            "ilan_no": v['ilan_no'],
            "marka": v['Marka'],
            "model": v['Seri'],
            "varyant": v['Model'],
            "yil": v['Yıl'],
            "km": v['KM'],
            "fiyat": v['Fiyat'],
            "yakit": v['Yakıt Tipi'],
            "vites": v['Vites'],
            "ilan_url": v['url'],
            "durum": "aktif"
        })
    with open(os.path.join(BASE, 'all_data.json'), 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f'Kaydedildi: cars_data.json ({len(final_list)}), all_data.json ({len(all_data)})')

if __name__ == "__main__":
    main()
