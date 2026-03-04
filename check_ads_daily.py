#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Günlük ilan kontrol botu - Radara yakalanmadan

Her gün rastgele saatte çalışır, ilanları kontrol eder ve durumları günceller.
"""

import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path

# User-agent listesi - rastgele seçilecek
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0 Safari/537.36'
]

def load_cars_data():
    """cars_data.json dosyasını yükle"""
    with open('cars_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cars_data(data):
    """cars_data.json dosyasını kaydet"""
    with open('cars_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_ad_status(ad_url):
    """
    İlan URL'ini kontrol et
    
    Returns:
        - 'active': İlan hala aktif
        - 'sold': İlan satılmış/kaldırılmış
        - 'error': Kontrol edilemedi
    """
    try:
        # Rastgele user-agent seç
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Request gönder
        response = requests.get(ad_url, headers=headers, timeout=10)
        
        # Durum kontrolü
        if response.status_code == 200:
            # İlan sayfasında "İlan Bulunamadı" veya "removed" var mı kontrol et
            if 'İlan bulunamadı' in response.text or 'İlan kaldırılmış' in response.text:
                return 'sold'
            return 'active'
        elif response.status_code == 404:
            return 'sold'
        else:
            return 'error'
            
    except Exception as e:
        print(f"Hata: {ad_url} kontrol edilemedi - {str(e)}")
        return 'error'

def log_result(ad_no, status, message):
    """Sonuçları log dosyasına yaz"""
    log_file = Path('ad_check_log.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] İlan No: {ad_no} - Durum: {status} - {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def main():
    """Ana bot fonksiyonu"""
    print("=" * 60)
    print("İlan Kontrol Botu Başlatıldı")
    print(f"Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Veriyi yükle
    data = load_cars_data()
    vehicles = data['vehicles']
    
    # İlanları karıştır (her seferinde farklı sırada kontrol et)
    random.shuffle(vehicles)
    
    checked_count = 0
    active_count = 0
    sold_count = 0
    error_count = 0
    
    for vehicle in vehicles:
        ad_no = vehicle.get('adNo', '')
        ad_url = vehicle.get('adUrl', '')
        
        if not ad_url:
            print(f"⚠️  İlan {ad_no}: Link yok, atlanıyor")
            continue
        
        print(f"\n🔍 Kontrol ediliyor: İlan No {ad_no}")
        print(f"   URL: {ad_url[:60]}...")
        
        # İlanı kontrol et
        status = check_ad_status(ad_url)
        
        if status == 'active':
            print(f"   ✅ Aktif")
            active_count += 1
            log_result(ad_no, 'AKTIF', 'İlan hala yayında')
        elif status == 'sold':
            print(f"   ❌ Satılmış/Kaldırılmış")
            sold_count += 1
            log_result(ad_no, 'SATILDI', 'İlan kaldırılmış')
        else:
            print(f"   ⚠️  Kontrol edilemedi")
            error_count += 1
            log_result(ad_no, 'HATA', 'İlan kontrol edilemedi')
        
        checked_count += 1
        
        # Rastgele bekleme (30-120 saniye) - İnsan gibi davran
        if checked_count < len([v for v in vehicles if v.get('adUrl')]):
            wait_time = random.randint(30, 120)
            print(f"   ⏳ Bekleniyor: {wait_time} saniye...")
            time.sleep(wait_time)
    
    # Özet
    print("\n" + "=" * 60)
    print("KONTROL TAMAMLANDI")
    print("=" * 60)
    print(f"Toplam kontrol edilen: {checked_count}")
    print(f"✅ Aktif ilanlar: {active_count}")
    print(f"❌ Satılmış/Kaldırılmış: {sold_count}")
    print(f"⚠️  Hata/Kontrol edilemedi: {error_count}")
    print("=" * 60)
    print(f"\nDetaylı log: ad_check_log.txt")
    
    # Özet logu
    log_result('ÖZET', 'TAMAMLANDI', 
               f"Toplam: {checked_count}, Aktif: {active_count}, "
               f"Satıldı: {sold_count}, Hata: {error_count}")

if __name__ == '__main__':
    main()
