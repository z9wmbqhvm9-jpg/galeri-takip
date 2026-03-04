#!/usr/bin/env python3
"""
Sahibinden Manuel İlan İçe Aktarıcı
Pazarlanan metni parse eder ve veritabanına ekler.
"""

import sqlite3
import os
import re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'galeri.db')

def parse_pasted_text(text):
    data = {}
    
    # İlan No
    match = re.search(r'İlan No\s+(\d+)', text)
    if match:
        data['ilan_no'] = match.group(1)
        
    # Fiyat
    match = re.search(r'(\d+\.?\d+)\s+TL', text)
    if match:
        data['fiyat_text'] = match.group(0)
        data['fiyat'] = int(match.group(1).replace('.', ''))
        
    # Marka
    match = re.search(r'Marka\s+(.+)', text)
    if match:
        data['marka'] = match.group(1).strip()
        
    # Seri / Model (Genelde Marka'dan sonra gelir)
    match = re.search(r'Seri\s+(.+)', text)
    if match:
        data['seri'] = match.group(1).strip()
    
    match = re.search(r'Model\s+(.+)', text)
    if match:
        data['model_detail'] = match.group(1).strip()
        
    # Yıl
    match = re.search(r'Yıl\s+(\d+)', text)
    if match:
        data['yil'] = int(match.group(1))
        
    # KM
    match = re.search(r'KM\s+([\d.]+)', text)
    if match:
        data['kilometre'] = match.group(1).strip()
        
    # Yakıt
    match = re.search(r'Yakıt Tipi\s+(.+)', text)
    if match:
        data['yakit'] = match.group(1).strip()
        
    # Vites
    match = re.search(r'Vites\s+(.+)', text)
    if match:
        data['vites'] = match.group(1).strip()
        
    # Renk
    match = re.search(r'Renk\s+(.+)', text)
    if match:
        data['renk'] = match.group(1).strip()

    # Başlık oluştur (eğer parse edildiyse)
    if 'yil' in data and 'marka' in data:
        data['baslik'] = f"{data['yil']} {data['marka']} {data.get('seri', '')} {data.get('model_detail', '')}".strip()
    else:
        # Alternatif başlık bulma (metnin en başındaki büyük yazı)
        lines = text.split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                data['baslik'] = line.strip()
                break

    if 'ilan_no' in data:
        data['ilan_url'] = f"https://www.sahibinden.com/ilan/{data['ilan_no']}"
        
    return data

def save_to_db(data):
    if not data.get('ilan_no'):
        print("Hata: İlan numarası bulunamadı!")
        return False
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # "Manuel Import" galerisi var mı?
    cursor.execute('SELECT id FROM galeriler WHERE galeri_adi = ?', ('Manuel Import',))
    row = cursor.fetchone()
    if row:
        galeri_id = row[0]
    else:
        cursor.execute('INSERT INTO galeriler (galeri_url, galeri_adi) VALUES (?, ?)', 
                       ('manual://import', 'Manuel Import'))
        galeri_id = cursor.lastrowid
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO araclar 
            (galeri_id, ilan_no, ilan_url, baslik, marka, model, yil, kilometre, yakit, vites, renk, fiyat, fiyat_text, durum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            galeri_id,
            data.get('ilan_no'),
            data.get('ilan_url'),
            data.get('baslik'),
            data.get('marka'),
            f"{data.get('seri', '')} {data.get('model_detail', '')}".strip(),
            data.get('yil'),
            data.get('kilometre'),
            data.get('yakit'),
            data.get('vites'),
            data.get('renk'),
            data.get('fiyat'),
            data.get('fiyat_text'),
            'aktif'
        ))
        conn.commit()
        print(f"Basariyla eklendi/guncellendi: {data.get('baslik')} ({data.get('ilan_no')})")
        return True
    except Exception as e:
        print(f"Veritabani hatasi: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    # Kullanıcıdan input alabiliriz ya da direkt buraya yapıştırabiliriz
    # Bu versiyonda bir input.txt dosyasından okuyacak şekilde yapalım
    if os.path.exists('import_input.txt'):
        with open('import_input.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed_data = parse_pasted_text(content)
        if parsed_data:
            print("--- Parse edilen bilgiler ---")
            for k, v in parsed_data.items():
                print(f"   {k}: {v}")
            save_to_db(parsed_data)
        else:
            print("Hata: Metin parse edilemedi.")
    else:
        print("Bilgi: import_input.txt dosyası bulunamadı. Lütfen ilan metnini bu dosyaya yapıştırın.")
