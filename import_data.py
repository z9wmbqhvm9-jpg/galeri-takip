#!/usr/bin/env python3
"""İlanları veritabanına aktar"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'galeri.db')

# Sayfa 1 - 20 ilan
sayfa1 = [
    {"id": "1285210048", "baslik": "PİRANLAR | 2025 Relive Light Truck 1.6 | Klima | Geri Görüş |K12", "url": "https://sahibinden.com/ilan/vasita-ticari-araclar-kamyon-kamyonet-piranlar-2025-relive-light-truck-1.6-klima-geri-gorus-k12-1285210048/detay"},
    {"id": "1299246786", "baslik": "PİRANLAR | 2011 Mercedes-Benz E 350 CDI 4Matic Premium", "url": "https://sahibinden.com/ilan/vasita-otomobil-mercedes-benz-piranlar-2011-mercedes-benz-e-350-cdi-4matic-premium-1299246786/detay"},
    {"id": "1299243212", "baslik": "PİRANLAR | 2023 Hyundai i20 1.2 MPI Jump", "url": "https://sahibinden.com/ilan/vasita-otomobil-hyundai-piranlar-2023-hyundai-i20-1.2-mpi-jump-1299243212/detay"},
    {"id": "1299243311", "baslik": "PİRANLAR | 2021 Peugeot 3008 1.5 BlueHDi GT EAT8", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-peugeot-piranlar-2021-peugeot-3008-1.5-bluehdi-gt-eat8-1299243311/detay"},
    {"id": "1299242311", "baslik": "PİRANLAR | 2024 BMW 520i MHEV M Sport", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2024-bmw-520i-mhev-m-sport-1299242311/detay"},
    {"id": "1299241884", "baslik": "PİRANLAR | 2022 Range Rover Sport 3.0 MHEV D350 First Edition", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-land-rover-piranlar-2022-range-rover-sport-3.0-mhev-d350-first-edition-1299241884/detay"},
    {"id": "1299239447", "baslik": "PİRANLAR | 2023 Audi A8 L 55 TFSI Quattro Tiptronic", "url": "https://sahibinden.com/ilan/vasita-otomobil-audi-piranlar-2023-audi-a8-l-55-tfsi-quattro-tiptronic-1299239447/detay"},
    {"id": "1272970119", "baslik": "PİRANLAR | 2024 BMW Z4 30i sDrive M Sport | Hatasız | KK12", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2024-bmw-z4-30i-sdrive-m-sport-hatasiz-kk12-1272970119/detay"},
    {"id": "1290655272", "baslik": "PİRANLAR | 2025 Mercedes GLC 180 AMG | Soğutma | Burmester |360°", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-mercedes-benz-piranlar-2025-mercedes-glc-180-amg-sogutma-burmester-360-1290655272/detay"},
    {"id": "1290661630", "baslik": "PİRANLAR | 2025 Mercedes GLC Coupe | 360° | Burmester", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-mercedes-benz-piranlar-2025-mercedes-glc-coupe-360-burmester-1290661630/detay"},
    {"id": "1295803042", "baslik": "PİRANLAR | Kia Sorento 1.6 Hybrid 4x4 | Isıtma & Soğutma | 360°", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-kia-piranlar-kia-sorento-1.6-hybrid-4x4-isitma-sogutma-360-1295803042/detay"},
    {"id": "1098676110", "baslik": "PİRANLAR | Dodge Challenger Scatpack 6.4 V8 | 498HP | TR Tek", "url": "https://sahibinden.com/ilan/vasita-otomobil-dodge-piranlar-dodge-challenger-scatpack-6.4-v8-498hp-tr-tek-1098676110/detay"},
    {"id": "1263450688", "baslik": "PİRANLAR | 2015 Audi Q7 3.0 TDI Quattro | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-audi-piranlar-2015-audi-q7-3.0-tdi-quattro-kk-12-ay-1263450688/detay"},
    {"id": "1281824713", "baslik": "PİRANLAR | Audi A7 40 TDI S-Line | B&O | Vakum | 360° | Bayi", "url": "https://sahibinden.com/ilan/vasita-otomobil-audi-piranlar-audi-a7-40-tdi-s-line-b-o-vakum-360-bayi-1281824713/detay"},
    {"id": "1292948013", "baslik": "PİRANLAR | 2025 Mercedes C200 AMG 4MATIC 360° Burmester | KK 12", "url": "https://sahibinden.com/ilan/vasita-otomobil-mercedes-benz-piranlar-2025-mercedes-c200-amg-4matic-360-burmester-kk-12-1292948013/detay"},
    {"id": "1286494068", "baslik": "PİRANLAR | 2025 BMW X3 20 | Harman | Isıtma | E.Bagaj | Brown", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-bmw-piranlar-2025-bmw-x3-20-harman-isitma-e.bagaj-brown-1286494068/detay"},
    {"id": "1263504231", "baslik": "PİRANLAR | 2025 BMW 520i M Sport Harman | %20 KDV | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2025-bmw-520i-m-sport-harman-20-kdv-kk-12-ay-1263504231/detay"},
    {"id": "1186217231", "baslik": "PİRANLAR | 2022 Skoda Karoq 1.5 TSI Prestige |Cam Tavan| Hatasız", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-skoda-piranlar-2022-skoda-karoq-1.5-tsi-prestige-cam-tavan-hatasiz-1186217231/detay"},
    {"id": "1281448181", "baslik": "PİRANLAR | 2025 BMW X3 20d xDrive M Sport | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-bmw-piranlar-2025-bmw-x3-20d-xdrive-m-sport-kk-12-ay-1281448181/detay"},
    {"id": "1263060655", "baslik": "PİRANLAR | 2025 MINI Countryman E Favoured | KK 12 Ay", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-mini-piranlar-2025-mini-countryman-e-favoured-kk-12-ay-1263060655/detay"},
]

# Sayfa 2 - 17 ilan
sayfa2 = [
    {"id": "1289804746", "baslik": "PİRANLAR | BMW 740 xDrive M | Masaj | Aktif Arka Aks |Bayi |KK12", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-bmw-740-xdrive-m-masaj-aktif-arka-aks-bayi-kk12-1289804746/detay"},
    {"id": "1281832728", "baslik": "PİRANLAR | 2025 BMW 320i M Sport | Brooklyn | Taba | KK 12 Ay", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2025-bmw-320i-m-sport-brooklyn-taba-kk-12-ay-1281832728/detay"},
    {"id": "1280856120", "baslik": "PİRANLAR | 2025 BMW i4 eDrive40 M Sport | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2025-bmw-i4-edrive40-m-sport-kk-12-ay-1280856120/detay"},
    {"id": "1274511555", "baslik": "PİRANLAR | 2025 SsangYong Torres 1.5 GDI | Hatasız", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-kgm-ssangyong-piranlar-2025-ssangyong-torres-1.5-gdi-hatasiz-1274511555/detay"},
    {"id": "1236881438", "baslik": "PİRANLAR | 2017 BMW X5 25d xDrive | Hayalet | Vakum | KK12", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-bmw-piranlar-2017-bmw-x5-25d-xdrive-hayalet-vakum-kk12-1236881438/detay"},
    {"id": "1286406454", "baslik": "PİRANLAR | 2024 Ford Ranger Wildtrak 4x4 | Isıtma | B&O", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-ford-piranlar-2024-ford-ranger-wildtrak-4x4-isitma-b-o-1286406454/detay"},
    {"id": "1289584198", "baslik": "PİRANLAR | Ford Focus 1.6 TDCi Trend X | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-otomobil-ford-piranlar-ford-focus-1.6-tdci-trend-x-kk-12-ay-1289584198/detay"},
    {"id": "1288252327", "baslik": "PİRANLAR | 2025 BMW iX xDrive60 M Sport | 360 | Isıtma & Soğutma", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-bmw-piranlar-2025-bmw-ix-xdrive60-m-sport-360-isitma-sogutma-1288252327/detay"},
    {"id": "1282188891", "baslik": "PİRANLAR | BMW X3 20 M Sport | Harman | Isıtma | Brown | KK12", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-bmw-piranlar-bmw-x3-20-m-sport-harman-isitma-brown-kk12-1282188891/detay"},
    {"id": "1280850731", "baslik": "PİRANLAR | 2025 BMW 320i Sport Line | KK 12 AY", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2025-bmw-320i-sport-line-kk-12-ay-1280850731/detay"},
    {"id": "1280858884", "baslik": "PİRANLAR | 2025 BMW 520i | B&W | Sürüş Asistanı | Soğutma | KK12", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2025-bmw-520i-b-w-surus-asistani-sogutma-kk12-1280858884/detay"},
    {"id": "1294905618", "baslik": "PİRANLAR | Prestige 60 Fly Motoryat | 2025 Refit", "url": "https://sahibinden.com/ilan/vasita-deniz-araclari-satilik-piranlar-prestige-60-fly-motoryat-2025-refit-1294905618/detay"},
    {"id": "1288246565", "baslik": "PİRANLAR | 2023 BMW 520i M Sport | Taba | Harman | E.Bagaj |KK12", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2023-bmw-520i-m-sport-taba-harman-e.bagaj-kk12-1288246565/detay"},
    {"id": "1285500804", "baslik": "PİRANLAR | Audi Q3 Sportback 45 TFSI Plug-in Hybrid | 245HP", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-audi-piranlar-audi-q3-sportback-45-tfsi-plug-in-hybrid-245hp-1285500804/detay"},
    {"id": "1282393019", "baslik": "PİRANLAR | 2024 BMW 320i M Sport LCI2 | Laser | Shadow |19\" |K12", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-2024-bmw-320i-m-sport-lci2-laser-shadow-19-k12-1282393019/detay"},
    {"id": "1285213563", "baslik": "PİRANLAR | BMW 320i 50 Jahre E. | 360° | Harman | M Koltuk | 19\"", "url": "https://sahibinden.com/ilan/vasita-otomobil-bmw-piranlar-bmw-320i-50-jahre-e-360-harman-m-koltuk-19-1285213563/detay"},
    {"id": "1292601658", "baslik": "PİRANLAR | 2025 Mercedes Bayi G580 EQ Manufaktur | ÖZEL RENK", "url": "https://sahibinden.com/ilan/vasita-arazi-suv-pickup-mercedes-benz-piranlar-2025-mercedes-bayi-g580-eq-manufaktur-ozel-renk-1292601658/detay"},
]

# Tüm ilanlar
tum_ilanlar = sayfa1 + sayfa2

def import_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galeri ID'sini al
    cursor.execute('SELECT id FROM galeriler WHERE galeri_url LIKE "%piranlar%"')
    result = cursor.fetchone()
    if not result:
        print("❌ Galeri bulunamadı! Önce galeri ekleyin.")
        return
    
    galeri_id = result[0]
    
    eklenen = 0
    for ilan in tum_ilanlar:
        try:
            # Yıl bilgisini başlıktan çıkar
            import re
            yil_match = re.search(r'\b(19|20)\d{2}\b', ilan['baslik'])
            yil = int(yil_match.group()) if yil_match else None
            
            cursor.execute('''
                INSERT OR IGNORE INTO araclar 
                (galeri_id, ilan_no, ilan_url, baslik, yil, durum)
                VALUES (?, ?, ?, ?, ?, 'aktif')
            ''', (galeri_id, ilan['id'], ilan['url'], ilan['baslik'], yil))
            
            if cursor.rowcount > 0:
                eklenen += 1
                print(f"✅ Eklendi: {ilan['baslik'][:50]}...")
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    # Galeri son kontrol zamanını güncelle
    cursor.execute('UPDATE galeriler SET son_kontrol = ? WHERE id = ?', (datetime.now(), galeri_id))
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Toplam {eklenen} ilan veritabanına eklendi!")
    print(f"📊 Tüm ilanlar: {len(tum_ilanlar)}")

if __name__ == '__main__':
    import_data()
