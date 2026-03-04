import re
import json
import os

def parse_single_block(text):
    """Tek bir ilan bloğunu ayrıştırır ve sadece istenen özel alanları çeker"""
    data = {}
    
    # 1. İlan No (Zorunlu - Bloğun merkezi)
    match = re.search(r"İlan No\s*(\d+)", text)
    if not match: return None
    data['ilan_no'] = match.group(1)

    # 2. Temel Bilgiler (Regex Desenleri)
    patterns = {
        'marka': r"Marka\s+(.+)",
        'seri': r"Seri\s+(.+)",
        'model_paket': r"Model\s+(.+)",
        'yil': r"Yıl\s+(\d+)",
        'km': r"KM\s+([\d.]+)",
        'yakit': r"Yakıt Tipi\s+(.+)",
        'ilan_tarihi': r"İlan Tarihi\s*(.+)",
        'agir_hasar': r"Ağır Hasar Kayıtlı\s+(.+)",
        'kimden': r"Kimden\s+(.+)",
        'vites': r"Vites\s+(.+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            val = match.group(1).strip()
            if key == 'yil':
                try: val = int(val)
                except: pass
            data[key] = val

    # 3. Fiyat (Metindeki ilk .000 TL formatlı yapıyı bulur)
    prices = re.findall(r"(\d+\.?\d*)\s*TL", text)
    if prices:
        # Genellikle teknik detayların üstündeki büyük fiyat doğrudur
        raw_price = prices[0].replace(".", "")
        try: data['fiyat'] = int(raw_price)
        except: data['fiyat'] = prices[0]

    # --- 4. AÇIKLAMA VE EKSPERTİZ ANALİZİ ---
    
    # Açıklama bölümünü ayır (Açıklama yazısından sonrasına odaklan)
    description_part = ""
    desc_match = re.search(r"Açıklama(.*)", text, re.DOTALL | re.IGNORECASE)
    if desc_match:
        description_part = desc_match.group(1)
    else:
        description_part = text # Açıklama başlığı yoksa tüm metne bak

    ekspertiz = {
        'tramer': 'Belirtilmemiş',
        'boya': [],
        'degisen': []
    }

    # Tramer Tespiti
    tramer_match = re.search(r"(TRAMER|HASAR KAYDI|HASAR)\s*[:=]?\s*(YOK|[\d.]+\s*TL|[\d.]+\s*BIN)", description_part, re.IGNORECASE)
    if tramer_match:
        ekspertiz['tramer'] = tramer_match.group(0).strip()

    # Boya ve Değişen Tespiti (Satır satır analiz)
    # Özellikle "DEĞİŞEN", "BOYA", "LOKAL", "SÖKTAK" kelimelerini içeren satırları yakalar
    lines = description_part.split('\n')
    for line in lines:
        clean_line = line.strip().upper()
        if not clean_line: continue
        
        # Değişen satırları
        if "DEĞİŞEN" in clean_line or "SÖKTAK" in clean_line or "SÖK TAK" in clean_line:
            ekspertiz['degisen'].append(line.strip())
        
        # Boya satırları
        elif "BOYA" in clean_line or "LOKAL" in clean_line:
            # "BOYASIZ" kelimesini içeren ama "LOKAL" içermeyen satırları boya olarak sayma
            if "BOYASIZ" in clean_line and "LOKAL" not in clean_line and "HARİCİ" not in clean_line:
                continue
            ekspertiz['boya'].append(line.strip())

    # Eğer liste boşsa metinde "HATASIZ" arayalım
    if not ekspertiz['boya'] and not ekspertiz['degisen']:
        if "HATASIZ" in description_part.upper() or "BOYASIZ" in description_part.upper():
            ekspertiz['genel_durum'] = "Hatasız / Boyasız"

    # Listeleri temizle ve birleştir
    ekspertiz['boya'] = ", ".join(ekspertiz['boya']) if ekspertiz['boya'] else "Belirtilmemiş"
    ekspertiz['degisen'] = ", ".join(ekspertiz['degisen']) if ekspertiz['degisen'] else "Belirtilmemiş"

    data['ekspertiz_ozeti'] = ekspertiz

    return data

def main():
    input_file = 'ilan_metni.txt'
    output_file = 'ilan_sonuc.json'

    if not os.path.exists(input_file):
        print(f"Hata: '{input_file}' bulunamadi.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        full_text = f.read()

    print("\n[ Islem Basliyor ] Ilanlar ayristiriliyor...")
    
    # 'Ilan No' isaretcilerini kullanarak metni bloklara bol
    matches = list(re.finditer(r"İlan No\s*(\d+)", full_text))
    
    if not matches:
        print("Hata: Metin icinde hic 'Ilan No' bulunamadi.")
        return

    ilanlar = []
    for i in range(len(matches)):
        start_pos = matches[i].start()
        # Baslik ve fiyat bilgisi Ilan No'nun ustunde oldugu icin geri sariyoruz
        safe_start = max(0, start_pos - 1500)
        
        if i + 1 < len(matches):
            end_pos = matches[i+1].start()
        else:
            end_pos = len(full_text)
            
        block = full_text[safe_start:end_pos]
        parsed = parse_single_block(block)
        
        if parsed:
            ilanlar.append(parsed)
            print(f"   + Ilan Bulundu: {parsed.get('marka', 'Bilinmiyor')} {parsed.get('seri', '')} ({parsed['ilan_no']})")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ilanlar, f, ensure_ascii=False, indent=2)

    print("\n" + "="*40)
    print(f"BASARIYLA TAMAMLANDI!")
    print(f"Toplam Ilan Sayisi: {len(ilanlar)}")
    print(f"Kayit: {output_file}")
    print("="*40)

if __name__ == "__main__":
    main()
