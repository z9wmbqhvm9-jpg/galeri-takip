"""
Ekran Izleyici - Sahibinden Ilanlarinin Otomatik Screenshot'i
Arka planda calisir, sahibinden.com'da navigasyon yaptiginda otomatik SS alir
"""

import sys
import io

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import time
import json
import re
from datetime import datetime
from PIL import ImageGrab
import threading
import psutil
import pygetwindow as gw
from urllib.parse import urlparse
import subprocess
import sys
import keyboard

# Ayarlar
SCREENSHOT_FOLDER = "screenshots"
CHECK_INTERVAL = 2  # Her 2 saniyede kontrol et
CURRENT_URL = None
LAST_SCREENSHOT = None

# Screenshot klasörü oluştur
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)
    print(f"OK: '{SCREENSHOT_FOLDER}' klasoru olusturuldu\n")

def get_chrome_url():
    """Chrome browser'dan aktif URL'yi almaya çalış"""
    try:
        # Windows'ta aktif pencereyi bul
        try:
            chrome_window = gw.getWindowsWithTitle('Chrome')[0]
        except:
            try:
                chrome_window = gw.getWindowsWithTitle('Chromium')[0]
            except:
                try:
                    chrome_window = gw.getWindowsWithTitle('Edge')[0]
                except:
                    chrome_window = None
        
        if chrome_window:
            # Window başlığından URL bilgisini al
            title = chrome_window.title
            
            # Eğer URL başlıkta ise çıkar
            if 'sahibinden' in title.lower() and 'http' not in title:
                # Sahibinden sayfasındayız
                return "https://www.sahibinden.com"
            elif 'http' in title:
                # URL başlıkta var
                return title.split(' - ')[0] if ' - ' in title else title
            
            return None
    except Exception as e:
        return None

def extract_listing_id_from_url(url):
    """URL'den İlan Numarasını çıkar"""
    try:
        # Sahibinden URL'lerinden ilan no çıkar
        # Örnek: https://www.sahibinden.com/ilan/1293041202
        match = re.search(r'/ilan/(\d+)', url)
        if match:
            return match.group(1)
        
        # Detay sayfasından
        match = re.search(r'(\d{10,})', url)
        if match:
            return match.group(1)
        
        return None
    except:
        return None

def take_screenshot(listing_id=None):
    """Screenshot al ve kaydet"""
    global LAST_SCREENSHOT
    
    try:
        # Tam ekran screenshot al
        screenshot = ImageGrab.grab()
        
        # Dosya adını oluştur
        if listing_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{SCREENSHOT_FOLDER}/ILAN_{listing_id}_{timestamp}.png"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{SCREENSHOT_FOLDER}/SS_{timestamp}.png"
        
        # Dosyayı kaydet
        screenshot.save(filename)
        
        LAST_SCREENSHOT = filename
        print(f"OK: [{datetime.now().strftime('%H:%M:%S')}] Screenshot kaydedildi: {os.path.basename(filename)}")
        
        return filename
    
    except Exception as e:
        print(f"❌ Screenshot hatası: {e}")
        return None

def monitor_screen():
    """Arka planda ekranı izle"""
    global CURRENT_URL
    
    last_listed_url = None
    consecutive_same = 0
    
    print("INFO: Ekran izlenmesi baslatildi...")
    print("INFO: Sahibinden ilanlarina gir, program otomatik SS alacak\n")
    print("-" * 60)
    
    try:
        while True:
            try:
                # Chrome URL'yi al
                current_url = get_chrome_url()
                
                # Eğer sahibinden linkiyse
                if current_url and 'sahibinden' in current_url.lower():
                    CURRENT_URL = current_url
                    
                    # İlan numarası çıkar
                    listing_id = extract_listing_id_from_url(current_url)
                    
                    # URL değiştiyse screenshot al
                    if current_url != last_listed_url:
                        consecutive_same = 0
                        
                        if listing_id:
                            print(f"\nINFO: Sahibinden Ilanina Girdin!")
                            print(f"   İlan No: {listing_id}")
                            print(f"   URL: {current_url[:80]}...")
                            
                            # Screenshot al
                            take_screenshot(listing_id)
                            last_listed_url = current_url
                        else:
                            # Ilan no bulunamadı ama sahibinden sayfası
                            print(f"\nINFO: Sahibinden Sayfasi Acildi (Ilan No bulunamadi)")
                            print(f"   URL: {current_url[:80]}...")
                            take_screenshot()
                            last_listed_url = current_url
                    else:
                        consecutive_same += 1
                
                elif current_url and 'sahibinden' not in current_url.lower():
                    last_listed_url = None
                    CURRENT_URL = None
                
            except Exception as e:
                pass
            
            # Interval kadar bekle
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "-" * 60)
        print("⏸️ İzleme durduruldu (Ctrl+C)")
        
        # İstatistikleri göster
        screenshots = [f for f in os.listdir(SCREENSHOT_FOLDER) if f.endswith('.png')]
        print(f"\nSTATS: Alinan SS'ler: {len(screenshots)} adet")
        print(f"📁 Klasör: {SCREENSHOT_FOLDER}")
        
        if screenshots:
            print("\nINFO: En son alinanlar:")
            for f in sorted(screenshots, reverse=True)[:5]:
                print(f"   • {f}")

def main():
    """Ana program"""
    print("\n" + "=" * 60)
    print("🚗 GALERİ TAKİP - EKRAN İZLEYİCİ")
    print("=" * 60)
    
    # İzlemeyi başlat
    monitor_thread = threading.Thread(target=monitor_screen, daemon=True)
    monitor_thread.start()
    
    # Klavye dinleyici başlat (Space tuşu)
    print("INFO: Space tusuna basildiginda SS alma ozelligi aktif!")
    keyboard.add_hotkey('space', lambda: take_screenshot())
    
    # Ana thread'i yaşat
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Gerekli kütüphaneleri kontrol et
    try:
        import pygetwindow
    except ImportError:
        print("\nERROR: pygetwindow yuklenmemis!")
        print("   pip install pygetwindow yapmaniz gerekiyor\n")
        sys.exit(1)
    
    main()
