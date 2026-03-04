"""
Sahibinden İlan Screenshot Otomatik Çekici
Her ilana girdiğinde otomatik SS alır ve klasörde depolaya
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pyautogui

# Ayarlar
SCREENSHOT_FOLDER = "screenshots"
CHROME_DRIVER_PATH = "chromedriver.exe"

# Screenshot klasörü oluştur
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)
    print(f"✅ '{SCREENSHOT_FOLDER}' klasörü oluşturuldu")

def setup_driver():
    """Chrome browser'ı ayarla"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Chrome başlatılamadı: {e}")
        return None

def get_listing_info(driver):
    """Sahibinden sayfasından ilanlı bilgileri çek"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # İlan numarasını al
        ilan_no_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'İlan No')]/../Following-sibling::td//text()|//span[contains(text(), 'İlan No')]/following-sibling::*"))
        )
        
        # Temel bilgileri al
        info = {}
        
        # İlan No
        try:
            ilan_no = driver.find_element(By.XPATH, "//td[contains(text(), 'İlan No')]/following-sibling::td").text
            info['ilan_no'] = ilan_no.strip()
        except:
            info['ilan_no'] = 'BILINMIYOR'
        
        # Model/Başlık
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text
            info['title'] = title.strip()
        except:
            info['title'] = 'BILINMIYOR'
        
        # Fiyat
        try:
            price = driver.find_element(By.XPATH, "//div[contains(@class, 'price')]").text
            info['fiyat'] = price.strip()
        except:
            info['fiyat'] = 'BILINMIYOR'
        
        return info
    
    except Exception as e:
        print(f"⚠️ Bilgi çekilirken hata: {e}")
        return {}

def take_screenshot(driver, info):
    """Tam sayfa screenshot al ve kaydet"""
    try:
        # İlan numarasını dosya adında kullan
        ilan_no = info.get('ilan_no', 'UNKNOWN')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{SCREENSHOT_FOLDER}/ILAN_{ilan_no}_{timestamp}.png"
        
        # Tam sayfayı screenshot al
        driver.save_screenshot(filename)
        
        print(f"✅ Screenshot kaydedildi: {filename}")
        
        # Bilgileri JSON dosyasına da kaydet
        info_file = filename.replace('.png', '_info.json')
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump({
                'screenshot': filename,
                'bilgiler': info,
                'timestamp': timestamp
            }, f, ensure_ascii=False, indent=2)
        
        return filename
    
    except Exception as e:
        print(f"❌ Screenshot kaydedilemedi: {e}")
        return None

def main():
    """Ana program"""
    print("=" * 50)
    print("🚗 GALERİ TAKİP - OTOMATİK SCREENSHOT ALICI")
    print("=" * 50)
    print()
    
    driver = None
    
    try:
        driver = setup_driver()
        if not driver:
            return
        
        while True:
            print("\n📋 Seçenekler:")
            print("1. Link gir - Screenshot al")
            print("2. Son screenshotları göster")
            print("3. Çık")
            
            secim = input("\nSeçim: ").strip()
            
            if secim == '1':
                link = input("\n🔗 Sahibinden link gir: ").strip()
                
                if not link:
                    print("❌ Boş link girildi!")
                    continue
                
                # URL kontrol et
                if not link.startswith('http'):
                    link = 'https://' + link
                
                try:
                    print(f"\n⏳ {link} açılıyor...")
                    driver.get(link)
                    
                    # Sayfanın yüklenmesini bekle
                    time.sleep(3)
                    
                    # Bilgileri çek
                    info = get_listing_info(driver)
                    
                    print(f"\n📊 Çekilen Bilgiler:")
                    print(f"  İlan No: {info.get('ilan_no', '?')}")
                    print(f"  Başlık: {info.get('title', '?')}")
                    print(f"  Fiyat: {info.get('fiyat', '?')}")
                    
                    # Screenshot al
                    screenshot = take_screenshot(driver, info)
                    
                    if screenshot:
                        print(f"\n✅ Tamamlandı! Dosya kaydedildi.")
                        print(f"📁 Klasör: {SCREENSHOT_FOLDER}")
                    
                except Exception as e:
                    print(f"❌ Hata: {e}")
            
            elif secim == '2':
                files = os.listdir(SCREENSHOT_FOLDER)
                png_files = [f for f in files if f.endswith('.png')]
                
                if png_files:
                    print(f"\n📸 Son screenshotlar ({len(png_files)} adet):")
                    for i, f in enumerate(sorted(png_files, reverse=True)[:10], 1):
                        print(f"  {i}. {f}")
                else:
                    print("\n❌ Henüz screenshot yok!")
            
            elif secim == '3':
                print("\n👋 Çıkılıyor...")
                break
            
            else:
                print("❌ Geçersiz seçim!")
    
    except KeyboardInterrupt:
        print("\n\n⏸️ Program durduruldu (Ctrl+C)")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Browser kapatıldı")

if __name__ == "__main__":
    main()
