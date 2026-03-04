#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı Araç Ekleme Scripti
Veriyi argümanlardan alıp JSON ve Dashboard'a ekler
"""

import json
import sys
from datetime import datetime
import re

def parse_vehicle_data(text):
    """Metin formatını parse et"""
    lines = text.strip().split('\n')
    vehicle = {}
    inspection = {}
    in_inspection = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Hasar bölümüne girişi kontrol et
        if 'hasar' in line.lower():
            in_inspection = True
            if ':' in line:
                # "Hasar: - Part: Status" formatında olabilir
                rest = line.split(':', 1)[1].strip()
                if rest and rest.startswith('-'):
                    # Aynı satırda hasar varsa işle
                    line = rest
                else:
                    continue
            else:
                continue
        
        if not ':' in line:
            continue
        
        # Hasar satırları "- Part Name: Status" veya "Part Name: Status" formatında
        if in_inspection:
            # Hypheni kaldır
            if line.startswith('-'):
                line = line[1:].strip()
            
            # "Part: Status" formatını parse et
            if ':' in line:
                part, status = line.split(':', 1)
                part = part.strip()
                status = status.strip()
                if part and status:
                    inspection[part] = status
        else:
            # Normal key:value parsing
            parts = line.split(':', 1)
            if len(parts) != 2:
                continue
            
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Turkish karakterleri normalize et LOWERCASE'DEN ÖNCE
            key = key.replace('İ', 'I').replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o')
            key = key.lower()
            # Value'da Çayırova normalizasyonu
            if 'bolge' in key:
                value = value.replace('Ç', 'C').replace('ç', 'c')
            
            if key == 'marka':
                vehicle['brand'] = value
            elif key == 'model':
                vehicle['model'] = value
            elif key == 'yil':
                vehicle['year'] = int(value) if value.isdigit() else value
            elif key == 'motor':
                vehicle['engine'] = value
                # Yakıt tipini motor açıklamasından tespit et
                if 'dizel' in value.lower() or 'dci' in value.lower() or 'hdi' in value.lower():
                    vehicle['fuel'] = 'Dizel'
                elif 'hybrid' in value.lower():
                    vehicle['fuel'] = 'Hibrit'
                else:
                    vehicle['fuel'] = 'Benzin'
            elif key == 'paket':
                vehicle['package'] = value
            elif key == 'km':
                vehicle['km'] = int(value.replace('.', '').replace(',', '')) if any(c.isdigit() for c in value) else value
            elif key == 'fiyat':
                vehicle['price'] = int(value.replace('.', '').replace(',', '')) if any(c.isdigit() for c in value) else value
            elif key == 'galeri':
                vehicle['seller_name'] = value
            elif key == 'bolge':
                vehicle['region'] = value
            elif key == 'renk':
                vehicle['color'] = value
            elif key in ['kasa tipi', 'kasatipi', 'kasa']:
                vehicle['body_type'] = value
            elif key in ['ilan tarihi', 'tarih', 'yayin tarihi']:
                vehicle['publish_date'] = value
            elif key == 'yakıt':
                vehicle['fuel'] = value
            elif key == 'vites':
                vehicle['transmission'] = value
            elif key == 'hp':
                vehicle['hp'] = int(value) if value.isdigit() else value
            elif key == 'telefon':
                vehicle['phone'] = value
            elif key in ['tramer', 'hasar kayitli', 'hasar kaydi', 'hasarkayda']:
                # Tramer/Hasar Kaydı bilgisi, inspection'a ekle
                if 'inspection' not in vehicle:
                    vehicle['inspection'] = {}
                inspection['Tramer'] = value
            elif key in ['ilan no', 'ilannо', 'adнo']:
                vehicle['ilan_no'] = value
    
    if inspection:
        vehicle['inspection'] = inspection
    
    return vehicle

def create_vehicle_object(parsed_data):
    """Parse edilen veriyi tam vehicle object'e çevir"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # İlan tarihi varsa, daysListed'i hesapla
    publish_date_raw = parsed_data.get('publish_date', today)
    
    # Tarih formatını dönüştür (DD.MM.YYYY -> YYYY-MM-DD)
    formatted_publish_date = today
    try:
        from datetime import datetime as dt
        # Çeşitli formatları dene
        for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
            try:
                pub_dt = dt.strptime(publish_date_raw, fmt)
                formatted_publish_date = pub_dt.strftime('%Y-%m-%d')
                break
            except:
                continue
    except:
        formatted_publish_date = today
    
    publish_date = formatted_publish_date
    
    if publish_date != today:
        # Tarih farkını hesapla
        try:
            from datetime import datetime as dt
            pub_dt = dt.strptime(publish_date, '%Y-%m-%d')
            today_dt = dt.strptime(today, '%Y-%m-%d')
            days_listed = (today_dt - pub_dt).days
        except:
            days_listed = 0
    else:
        days_listed = 0
    
    # İlan No varsa onu kullan, yoksa timestamp'ten oluştur
    if parsed_data.get('ilan_no'):
        vehicle_id = str(parsed_data.get('ilan_no')).strip()
    else:
        vehicle_id = str(int(datetime.now().timestamp() * 1000) % 10000000000)
    
    region = parsed_data.get('region', 'Diğer')
    
    # Region normalizasyonu - Turkish karakterleri handle et
    region_normalized = region.lower().replace('ç', 'c').replace('ş', 's').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o').replace('ı', 'i')
    
    if 'cayirova' in region_normalized:
        region = 'Çayırova'
    elif 'gebze' in region_normalized:
        region = 'Gebze'
    elif 'derciftligi' in region_normalized:
        region = 'DerÇiftliği'
    elif 'izmit' in region_normalized:
        region = 'İzmit'
    else:
        region = 'Diğer'
    
    seller = parsed_data.get('seller_name', 'Bilinmiyor')
    
    # Inspection verilerini al ve eksik parçaları tamamla
    inspection = parsed_data.get('inspection', {})
    
    # Tüm standart parçaların listesi
    all_parts = [
        'Kaput', 'Tavan', 'Ön Tampon', 'Arka Tampon',
        'Sağ Ön Çamurluk', 'Sol Ön Çamurluk',
        'Sağ Ön Kapı', 'Sol Ön Kapı',
        'Sağ Arka Kapı', 'Sol Arka Kapı',
        'Sağ Arka Çamurluk', 'Sol Arka Çamurluk',
        'Bagaj Kapağı'
    ]
    
    # Tramer bilgisi varsa onu koru
    tramer = inspection.get('Tramer', '0 TL')
    
    # Yeni inspection objesi oluştur - sıralı
    complete_inspection = {}
    
    # Önce Tramer
    complete_inspection['Tramer'] = tramer
    
    # Sonra tüm parçalar
    for part in all_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
        else:
            complete_inspection[part] = 'Orijinal'
    
    # Yapısal parçalar ve özel durumlar
    structural_parts = ['Şase', 'Podye', 'Kule', 'Direk', 'Airbag', 'Bagaj Havuzu']
    for part in structural_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
        else:
            complete_inspection[part] = 'Orijinal'
    
    # Özel durumlar için kontrol (Motor, Şanzıman, vb)
    special_parts = ['Motor', 'Şanzıman', 'Diferansiyel', 'Panel', 'Çürük', 'Çatlak', 'Macun']
    for part in special_parts:
        if part in inspection:
            complete_inspection[part] = inspection[part]
    
    vehicle = {
        "id": vehicle_id,
        "adNo": vehicle_id,
        "publishDate": publish_date,
        "daysListed": days_listed,
        "vehicle": {
            "year": parsed_data.get('year', ''),
            "brand": parsed_data.get('brand', ''),
            "model": parsed_data.get('model', ''),
            "engine": parsed_data.get('engine', ''),
            "package": parsed_data.get('package', ''),
            "fuel": parsed_data.get('fuel', 'Benzin'),
            "transmission": parsed_data.get('transmission', 'Manuel'),
            "km": parsed_data.get('km', 0),
            "hp": parsed_data.get('hp', 0),
            "color": parsed_data.get('color', ''),
            "body_type": parsed_data.get('body_type', '')
        },
        "price": parsed_data.get('price', 0),
        "seller": {
            "name": seller,
            "type": "Galeri",
            "phone": parsed_data.get('phone', ''),
            "url": ""
        },
        "location": {
            "city": "Kocaeli",
            "district": region,
            "region": region,
            "neighborhood": ""
        },
        "condition": {
            "status": "İkinci El",
            "heavyDamaged": False,
            "warranty": False,
            "exchange": False
        },
        "description": "",
        "features": [],
        "inspection": complete_inspection
    }
    
    return vehicle, region

def load_data(data_file):
    """JSON verilerini yükle"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"vehicles": [], "regions": {
            "Çayırova": [], "Gebze": [], "DerÇiftliği": [], 
            "İzmit": [], "Diğer": []
        }}
    return data

def main():
    if len(sys.argv) < 2:
        print("❌ Kullanım: python add_car.py \"Marka: Toyota...\"")
        sys.exit(1)
    
    vehicle_text = sys.argv[1]
    data_file = 'cars_data.json'
    html_file = 'dashboard_new.html'
    
    # Parse et
    parsed = parse_vehicle_data(vehicle_text)
    vehicle, region = create_vehicle_object(parsed)
    
    # Veriyi yükle
    data = load_data(data_file)
    
    # Araç ekle
    data['vehicles'].append(vehicle)
    if region not in data['regions']:
        data['regions'][region] = []
    data['regions'][region].append(vehicle['id'])
    
    # Kaydet
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Araç eklendi!")
    print(f"   {vehicle['vehicle']['year']} {vehicle['vehicle']['brand']} {vehicle['vehicle']['model']}")
    print(f"   Fiyat: {vehicle['price']:,} TL")
    print(f"   Bölge: {region}")
    print(f"   📊 Toplam araç: {len(data['vehicles'])}")

if __name__ == "__main__":
    main()
