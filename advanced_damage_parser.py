import json
import re

def parse_damage(text):
    text = str(text).lower()
    
    # 1. Hasar Tespiti Önceliği
    hasar_keywords = ['boyalı', 'boyali', 'değişen', 'degisen', 'tramer', 'hasar', 'göçük', 'gocuk', 'lokal']
    has_damage_keyword = any(k in text for k in hasar_keywords)
    
    # Varsayılan Durum (Fallback) - Eğer hiç hasar kelimesi yoksa ve hatasız yazıyorsa
    if not has_damage_keyword:
        if 'hatasız' in text or 'hatasiz' in text or 'boyasız' in text or 'boyasiz' in text:
            return {'boya': [], 'degisen': [], 'tramer': 'Yok'}
    
    # Hasar kelimeleri varsa detaylı analiz
    boya_list = []
    degisen_list = []
    tramer_val = ''
    
    # 2. Parça Eşleştirme
    parcalar = [
        'sol ön çamurluk', 'sağ ön çamurluk', 'sol arka çamurluk', 'sağ arka çamurluk',
        'sol ön kapı', 'sağ ön kapı', 'sol arka kapı', 'sağ arka kapı',
        'sol çamurluk', 'sağ çamurluk', 'sol kapı', 'sağ kapı',
        'kaput', 'motor kaputu', 'tavan', 'bagaj', 'bagaj kapağı', 'marşpiyel', 'tampon'
    ]
    
    # Her parça için boyalı/değişen kontrolü
    for p in parcalar:
        # P yakında boyalı var mı? (max 20 karakter mesafe)
        if re.search(rf'{p}.{{0,20}}boyal[ıi]|boyal[ıi].{{0,20}}{p}|lokal.{{0,20}}{p}|{p}.{{0,20}}lokal', text):
            boya_list.append(p.title())
        
        # P yakında değişen var mı?
        if re.search(rf'{p}.{{0,20}}değişen|{p}.{{0,20}}degisen|değişen.{{0,20}}{p}|degisen.{{0,20}}{p}|{p}.{{0,20}}sök-tak|sök-tak.{{0,20}}{p}', text):
            degisen_list.append(p.title())

    # 3. Rakam Analizi (Tramer)
    # Örnek: "10.000 TL tramer", "Tramer: 5000", "5.000 tl hasar"
    tramer_match = re.search(r'([0-9]{1,3}(?:\.[0-9]{3})*)\s*(?:tl)?\s*(?:tramer|hasar)', text)
    if not tramer_match:
        tramer_match = re.search(r'(?:tramer|hasar kaydı|hasar).{0,15}?([0-9]{1,3}(?:\.[0-9]{3})*)\s*(?:tl)?', text)
        
    if tramer_match:
        tramer_val = tramer_match.group(1) + ' TL'
    elif 'tramer yok' in text or 'hasar kaydı yok' in text or 'tramersiz' in text:
        tramer_val = 'Yok'
        
    # Temizleme
    boya_list = list(set(boya_list))
    degisen_list = list(set(degisen_list))
    
    # Eğer hasar kelimesi geçtiği için "hatasız" diyemedik ama hiçbir parça/tramer de bulamadıysak
    # Mevcut datayı ezmemesi adına None dönüyoruz
    if not boya_list and not degisen_list and not tramer_val:
        return None
        
    return {
        'boya': boya_list,
        'degisen': degisen_list,
        'tramer': tramer_val or '-'
    }

def main():
    try:
        with open('cars_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print("Dosya okunamadı:", e)
        return

    updated_count = 0
    vehicles = data.get('vehicles', [])
    
    for v in vehicles:
        # Metin birleştirme: URL, Başlık ve varsa description
        text_content = f"{v.get('url', '')} {v.get('Baslik', '')} {v.get('description', '')}"
        
        # Eski ekspertiz
        old_exp = v.get('ekspertiz_ozeti', {})
        old_boya = old_exp.get('boya', [])
        old_degisen = old_exp.get('degisen', [])
        old_tramer = old_exp.get('tramer', '')
        
        # Eğer manuel olarak detaylı girilmişse dokunma (Boya veya değişen listesi doluysa)
        # Sadece eksik olanlara/yeni kurala uyanlara müdahale ediyoruz.
        if (not old_boya and not old_degisen) or old_tramer in ['', '-']:
            parsed = parse_damage(text_content)
            
            if parsed:
                # parsed geçerliyse uygula
                # Ama eskisinde tramer olup da parsed yeni tramer bulamadıysa eski tramer kalsın
                if not parsed['tramer'] or parsed['tramer'] == '-':
                    parsed['tramer'] = old_tramer if old_tramer else '-'
                
                # Sadece değişiklik varsa güncelle ve say
                if v.get('ekspertiz_ozeti') != parsed:
                    v['ekspertiz_ozeti'] = parsed
                    updated_count += 1
                    print(f"Güncellendi: {v.get('adNo') or v.get('ilan_no')} -> {parsed}")

    if updated_count > 0:
        with open('cars_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Toplam {updated_count} aracın hasar detayı kurallara göre güncellendi.")
    else:
        print("Kurallara uyan yeni güncellenecek araç bulunamadı.")

if __name__ == '__main__':
    main()
