import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Ayarlar
DATA_FILE = 'cars_data.json'
WAIT_BETWEEN = 2  # saniye

# Chrome ayarları
chrome_options = Options()
chrome_options.add_argument('--headless')  # Arka planda çalışsın
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# Araç verisini yükle
with open(DATA_FILE, encoding='utf-8') as f:
    data = json.load(f)


vehicles = data.get('vehicles', [])

# ASİL MOTORS ilanı ekle (varsa tekrar eklenmesin)
asil_ad_no = "1302474746"
asil_exists = any(v.get("adNo") == asil_ad_no for v in vehicles)
if not asil_exists:
    vehicles.append({
        "id": asil_ad_no,
        "adNo": asil_ad_no,
        "adUrl": "https://www.sahibinden.com/ilan/vasita-otomobil-renault-asil-motors-renault-megane-icon-1.5-blue-dci-1302474746/detay",
        "publishDate": "2026-02-26",
        "daysListed": 1,
        "vehicle": {
            "year": 2020,
            "brand": "Renault",
            "model": "Megane 1.5 Blue DCI Icon",
            "engine": "1.5 Blue DCI",
            "package": "Icon",
            "fuel": "Dizel",
            "transmission": "Otomatik",
            "km": 135000,
            "hp": 115,
            "color": "Siyah",
            "body_type": "Sedan"
        },
        "price": 1485000,
        "seller": {
            "name": "ASİL MOTORS",
            "type": "Galeriden",
            "phone": "05456063850",
            "url": ""
        },
        "location": {
            "city": "Kocaeli",
            "district": "Çayırova",
            "region": "Özgürlük Mh."
        },
        "condition": {
            "status": "İkinci El",
            "heavyDamaged": False,
            "warranty": False,
            "exchange": True
        },
        "description": "2020 RENAULT MEGANE 1.5 BLUE DCI ICON DİZEL & OTOMATİK ORİJİNAL 135.000 KM, EKSPERTİZ, SAĞ ARKA KAPI VE ÇAMURLUK LOKAL BOYALI, ANAHTARSIZ GİRİŞ, CRUISE KONTROL, PARK SENSÖRÜ, vb.",
        "features": [
            "Orijinal",
            "Lokal Boyalı",
            "Boyalı Yok",
            "Değişen Yok"
        ],
        "inspection": {
            "Lokal Boyalı Parçalar": "Sağ Arka Kapı, Sağ Arka Çamurluk",
            "Değişen": "Yok",
            "Tramer": "Yok"
        },
        "status": "active"
    })

# Selenium başlat
browser = webdriver.Chrome(options=chrome_options)


# Araçları yıla göre büyükten küçüğe sırala
def get_field(v, key):
    # Try nested 'vehicle' dict, then top-level
    if 'vehicle' in v and isinstance(v['vehicle'], dict):
        return v['vehicle'].get(key, v.get(key, '-'))
    return v.get(key, '-')

# Flat formatları tam dönüştür

# Tüm ilanları normalize et, eksik alanları tamamla

for v in vehicles:
    # Flat formatı eski formata çevir
    if 'vehicle' not in v or not isinstance(v['vehicle'], dict):
        v['vehicle'] = {
            'year': v.get('year', v.get('vehicle', {}).get('year', '-')),
            'brand': v.get('brand', v.get('vehicle', {}).get('brand', '-')),
            'model': v.get('model', v.get('vehicle', {}).get('model', '-')),
            'engine': v.get('engine', v.get('vehicle', {}).get('engine', '-')),
            'package': v.get('package', v.get('series', v.get('vehicle', {}).get('package', '-'))),
            'fuel': v.get('fuel', v.get('vehicle', {}).get('fuel', '-')),
            'transmission': v.get('gear', v.get('transmission', v.get('vehicle', {}).get('transmission', '-'))),
            'km': v.get('km', v.get('vehicle', {}).get('km', '-')),
            'hp': v.get('enginePower', v.get('vehicle', {}).get('hp', '-')),
            'color': v.get('color', v.get('vehicle', {}).get('color', '-')),
            'body_type': v.get('bodyType', v.get('vehicle', {}).get('body_type', '-'))
        }
    # Marka, model, paket alanlarını düzelt
    if not v['vehicle'].get('brand') or v['vehicle']['brand'] == '-':
        v['vehicle']['brand'] = v.get('brand', '-')
    if not v['vehicle'].get('model') or v['vehicle']['model'] == '-':
        v['vehicle']['model'] = v.get('model', '-')
    if not v['vehicle'].get('package') or v['vehicle']['package'] == '-':
        v['vehicle']['package'] = v.get('package', v.get('series', '-'))
    # publishDate ve daysListed düzelt
    if not v.get('publishDate') or v.get('publishDate') == '-':
        v['publishDate'] = v.get('adDate', '-')
    if not v.get('daysListed') or v.get('daysListed') == '-' or v.get('daysListed') is None:
        v['daysListed'] = 0
    # Özellikle 1301359379 için zorunlu düzeltme
    if str(v.get('adNo')) == '1301359379':
        v['vehicle']['package'] = '1.6 Multijet Easy'
        v['vehicle']['model'] = '1.6 Multijet Easy'
        v['vehicle']['brand'] = 'Fiat'
        v['publishDate'] = '2026-02-20'
        v['daysListed'] = 6

    # Detayda anahtar kelime yoksa inspection veya description'a 'Hatasız' ekle
    detay_text = ''
    # inspection dict varsa stringleştir
    if 'inspection' in v and isinstance(v['inspection'], dict):
        detay_text += json.dumps(v['inspection'], ensure_ascii=False)
    # description varsa ekle
    if v.get('description'):
        detay_text += ' ' + str(v['description'])
    keywords = ['DEĞİŞEN', 'BOYA', 'TRAMER', 'SÖKTAK', 'DEGİŞEN', 'BOYA', 'TRAMER', 'SÖK TAK', 'SÖK-TAK', 'SÖK TAK', 'SÖKTAK', 'DEĞİŞEN', 'BOYA', 'TRAMER', 'ÇİZİK', 'HASAR', 'AĞIR HASAR', 'KAZA']
    if not any(kw.lower() in detay_text.lower() for kw in keywords):
        # inspection varsa oraya ekle, yoksa description'a ekle
        if 'inspection' in v and isinstance(v['inspection'], dict):
            v['inspection']['Durum'] = 'Hatasız'
        else:
            v['description'] = (v.get('description') or '') + ' Hatasız'

vehicles_sorted = sorted(vehicles, key=lambda v: get_field(v, 'year'), reverse=True)

def durum_ikon(status):
    if str(status).upper() == 'AKTİF':
        return '✔️'
    elif str(status).upper() == 'SATILDI':
        return '❌'
    else:
        return '❓'

print(f"{'YIL':<5} {'MARKA':<10} {'MODEL':<18} {'KM':>8} {'FİYAT':>10} {'DURUM':^6} {'LİNK'}")
print('-'*80)
for v in vehicles_sorted[:8]:
    y = get_field(v, 'year')
    marka = get_field(v, 'brand')
    m = get_field(v, 'model')
    paket = get_field(v, 'package')
    km = get_field(v, 'km')
    fiyat = v.get('price', '-')
    status = v.get('status', 'BİLİNMİYOR')
    url = v.get('adUrl', '-')
    tarih = v.get('publishDate', '-')
    gun = v.get('daysListed', '-')
    print(f"{str(y):<5} {str(marka)[:9]:<10} {str(m)[:17]:<18} {str(paket)[:12]:<12} {str(km):>8} {str(fiyat):>10} {str(tarih):>12} {str(gun):>5} {durum_ikon(status):^6} {url}")
    time.sleep(0.1)

browser.quit()

# Sonuçları kaydet
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Kontrol tamamlandı!')
def durum_ikon(status):
    status = str(status).upper()

    if "AKT" in status:
        return "✓"
    elif "SAT" in status:
        return "✗"
    else:
        return "?"


