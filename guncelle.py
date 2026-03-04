#!/usr/bin/env python3
"""
Manuel veri güncelleme scripti
Safari'den çekilen JSON verisini buraya yapıştırın
"""

import sqlite3
import os
import re
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'galeri.db')

def guncelle(json_veri):
    """JSON verisini veritabanına ekle ve değişiklikleri tespit et"""
    
    if isinstance(json_veri, str):
        ilanlar = json.loads(json_veri)
    else:
        ilanlar = json_veri
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galeri ID'sini al
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE "%piranlar%"')
    result = cursor.fetchone()
    if not result:
        print("❌ Galeri bulunamadı!")
        return
    
    galeri_id = result[0]
    
    # Mevcut aktif ilanları al
    cursor.execute('SELECT ilan_no FROM araclar WHERE galeri_id = ? AND durum = "aktif"', (galeri_id,))
    mevcut_aktif = set(row[0] for row in cursor.fetchall())
    
    bulunan = set()
    yeni_sayisi = 0
    
    for ilan in ilanlar:
        ilan_no = ilan.get('id')
        if not ilan_no:
            continue
        
        bulunan.add(ilan_no)
        
        if ilan_no not in mevcut_aktif:
            # Yeni ilan!
            yil_match = re.search(r'\b(19|20)\d{2}\b', ilan.get('baslik', ''))
            yil = int(yil_match.group()) if yil_match else None
            
            cursor.execute('''
                INSERT OR IGNORE INTO araclar 
                (galeri_id, ilan_no, ilan_url, baslik, yil, durum)
                VALUES (?, ?, ?, ?, ?, 'aktif')
            ''', (galeri_id, ilan_no, ilan.get('url'), ilan.get('baslik'), yil))
            
            if cursor.rowcount > 0:
                print(f"🆕 Yeni ilan: {ilan.get('baslik', '')[:50]}")
                yeni_sayisi += 1
        else:
            # Son görülme güncelle
            cursor.execute('UPDATE araclar SET son_gorulme = ? WHERE ilan_no = ?', (datetime.now(), ilan_no))
    
    # Satılanları tespit et
    satilan_sayisi = 0
    for ilan_no in mevcut_aktif:
        if ilan_no not in bulunan:
            cursor.execute('''
                UPDATE araclar SET durum = 'satildi', son_gorulme = ?
                WHERE ilan_no = ?
            ''', (datetime.now(), ilan_no))
            
            cursor.execute('SELECT baslik FROM araclar WHERE ilan_no = ?', (ilan_no,))
            satilan = cursor.fetchone()
            print(f"🏷️ SATILDI: {satilan[0][:50] if satilan else ilan_no}")
            satilan_sayisi += 1
    
    # Galeri güncelle
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Özet: {yeni_sayisi} yeni, {satilan_sayisi} satıldı, {len(bulunan)} toplam aktif")


# Kullanım:
# 1. Safari'de JavaScript kodunu çalıştırın
# 2. Sonucu aşağıya yapıştırın
# 3. python3 guncelle.py çalıştırın

if __name__ == '__main__':
    # Safari'den aldığınız JSON verisini buraya yapıştırın:
    veri = """
    [
        BURAYA_JSON_YAPIŞTIRIN
    ]
    """
    
    if "BURAYA_JSON" in veri:
        print("📝 Kullanım:")
        print("1. Safari'de galeri sayfasını açın")
        print("2. Konsola şu kodu yapıştırın:")
        print("""
var liste = [];
document.querySelectorAll('a[href*="sahibinden.com/ilan/"]').forEach(a => {
    var href = a.href;
    var idMatch = href.match(/(\\d{9,})/);
    var baslik = a.innerText.trim();
    if(idMatch && baslik && baslik.length > 5 && !liste.find(x => x.id === idMatch[1])) {
        liste.push({ id: idMatch[1], baslik: baslik, url: href });
    }
});
JSON.stringify(liste);
        """)
        print("\n3. Sonucu bu dosyadaki 'veri' değişkenine yapıştırın")
        print("4. python3 guncelle.py çalıştırın")
    else:
        guncelle(veri)
