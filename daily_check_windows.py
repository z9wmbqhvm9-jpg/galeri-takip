#!/usr/bin/env python3
"""
Windows için Günlük İlan Kontrol Botu
Sistemdeki tüm araçları kontrol eder, satılanları otomatik işaretler

KULLANIM:
python daily_check_windows.py

GEREKSINIMLER:
pip install selenium requests
"""

import json
import time
import os
import sys
import requests
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ayarlar
CARS_DATA_PATH = 'cars_data.json'
API_URL = 'http://localhost:5000'
CHECK_DELAY_MIN = 5  # Minimum bekleme (saniye)
CHECK_DELAY_MAX = 10  # Maximum bekleme (saniye)
HEADLESS = False  # Tarayıcı görünmesin mi? (False = insan gibi görünür)
CONTINUOUS_MODE = True  # Sürekli çalışma modu
CHECK_INTERVAL_HOURS = 6  # Kaç saatte bir kontrol (6 saat)

# Anti-bot user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
]

class DailyChecker:
    def __init__(self):
        self.driver = None
        self.results = {
            'checked': 0,
            'active': 0,
            'sold': 0,
            'error': 0,
            'details': []
        }
    
    def setup_driver(self):
        """Chrome sürücüsünü hazırla"""
        print("🌐 Chrome başlatılıyor...")
        
        chrome_options = Options()
        if HEADLESS:
            chrome_options.add_argument('--headless=new')
        
        # Random user agent (bot detection önleme)
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Anti-bot özellikleri
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Gerçek tarayıcı profilini kullan (çerezler, cache)
        chrome_options.add_argument('--disable-infobars')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # WebDriver özelliğini gizle
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Dil ve platform ayarları
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent,
                "platform": "Windows",
                "acceptLanguage": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
            })
            
            print("✅ Chrome hazır!\n")
            return True
        except Exception as e:
            print(f"❌ Chrome başlatılamadı: {e}")
            print("💡 ChromeDriver yüklü olduğundan emin olun: pip install selenium")
            return False
    
    def load_vehicles(self):
        """Araçları yükle"""
        try:
            with open(CARS_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('vehicles', [])
        except Exception as e:
            print(f"❌ Araç verileri okunamadı: {e}")
            return []
    
    def check_listing(self, vehicle):
        """Tek bir ilanı kontrol et"""
        ad_no = vehicle.get('adNo') or vehicle.get('id')
        ad_url = vehicle.get('adUrl', '')
        brand = vehicle.get('vehicle', {}).get('brand', '')
        model = vehicle.get('vehicle', {}).get('model', '')
        year = vehicle.get('vehicle', {}).get('year', '')
        
        car_info = f"{year} {brand} {model} ({ad_no})"
        
        if not ad_url:
            print(f"⚠️  URL yok: {car_info}")
            self.results['error'] += 1
            return 'error'
        
        try:
            # Driver kontrolü - eğer kapanmışsa yeniden başlat
            try:
                _ = self.driver.current_url
            except:
                print(f"      🔄 Chrome yeniden başlatılıyor...")
                self.setup_driver()
            
            print(f"🔍 Kontrol ediliyor: {car_info}")
            
            self.driver.get(ad_url)
            
            # Random insan gibi bekleme (2-4 saniye)
            time.sleep(random.uniform(2, 4))
            
            # Sayfa başlığını kontrol et
            try:
                page_title = self.driver.title.lower()
            except:
                print(f"   ⚠️  Sayfa başlığı alınamadı")
                return 'error'
            
            # Sayfa içeriğini kontrol et
            try:
                page_source = self.driver.page_source.lower()
            except:
                page_source = ""
            
            # Satıldı kontrolü - 404 veya ilan yok
            if any(keyword in page_title for keyword in ['bulunamadı', 'not found', 'hata', 'error', '404']):
                print(f"   ❌ İlan kaldırılmış (sayfa bulunamadı)")
                return 'sold'
            
            if any(keyword in page_source for keyword in ['ilan bulunamadı', 'ilan kaldırılmış', 'satıştan kaldırılmış', 'pasifleşti']):
                print(f"   ❌ İlan kaldırılmış (içerik kontrolü)")
                return 'sold'
            
            # Aktif ilan kontrolü - sahibinden.com yapısına özel
            try:
                # Sahibinden.com'da fiyat elementi
                price_element = self.driver.find_element(By.CSS_SELECTOR, '.classifiedInfo h3')
                if price_element and 'TL' in price_element.text:
                    print(f"   ✅ İlan aktif (Fiyat: {price_element.text.strip()})")
                    return 'active'
            except:
                pass
            
            # Alternatif: Başlık kontrolü
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, 'h1.classifiedDetailTitle')
                if title_element and len(title_element.text) > 10:
                    print(f"   ✅ İlan aktif (Başlık bulundu)")
                    return 'active'
            except:
                pass
            
            # Son çare: URL'de "detay" var ve 404 değilse muhtemelen aktif
            if 'detay' in ad_url and '404' not in page_title:
                print(f"   ✅ İlan aktif (URL geçerli)")
                return 'active'
            
            # Belirsiz durum
            print(f"   ⚠️  Durum belirsiz (Manuel kontrol gerekebilir)")
            return 'error'
            
        except Exception as e:
            print(f"   ⚠️  Hata: {str(e)[:100]}")
            return 'error'
    
    def mark_as_sold(self, ad_no):
        """API üzerinden satıldı olarak işaretle"""
        try:
            response = requests.post(
                f'{API_URL}/api/mark-sold',
                json={'adNo': ad_no},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"      ⚠️  API hatası: {e}")
            return False
    
    def run_check(self):
        """Tüm araçları kontrol et"""
        print("=" * 60)
        print("🚗 Günlük İlan Kontrol Sistemi")
        print("=" * 60)
        print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Chrome'u başlat
        if not self.setup_driver():
            return False
        
        # Araçları yükle
        vehicles = self.load_vehicles()
        if not vehicles:
            print("❌ Kontrol edilecek araç bulunamadı!")
            return False
        
        print(f"📊 Toplam {len(vehicles)} araç kontrol edilecek\n")
        
        # Her aracı kontrol et
        for i, vehicle in enumerate(vehicles, 1):
            ad_no = vehicle.get('adNo') or vehicle.get('id')
            brand = vehicle.get('vehicle', {}).get('brand', '')
            model = vehicle.get('vehicle', {}).get('model', '')
            year = vehicle.get('vehicle', {}).get('year', '')
            
            print(f"\n[{i}/{len(vehicles)}] ", end='')
            
            status = self.check_listing(vehicle)
            self.results['checked'] += 1
            
            if status == 'sold':
                self.results['sold'] += 1
                self.results['details'].append({
                    'adNo': ad_no,
                    'car': f"{year} {brand} {model}",
                    'status': 'sold'
                })
                
                # API'ye bildir
                print(f"      📝 Satıldı olarak işaretleniyor...")
                if self.mark_as_sold(ad_no):
                    print(f"      ✅ İşaretlendi!")
                else:
                    print(f"      ⚠️  İşaretlenemedi (API hatası)")
                    
            elif status == 'active':
                self.results['active'] += 1
                self.results['details'].append({
                    'adNo': ad_no,
                    'car': f"{year} {brand} {model}",
                    'status': 'active'
                })
            else:
                self.results['error'] += 1
                self.results['details'].append({
                    'adNo': ad_no,
                    'car': f"{year} {brand} {model}",
                    'status': 'error'
                })
            
            # İnsan gibi random bekleme
            if i < len(vehicles):
                wait_time = random.uniform(CHECK_DELAY_MIN, CHECK_DELAY_MAX)
                print(f"      ⏳ {wait_time:.1f} saniye bekleniyor...")
                time.sleep(wait_time)
        
        # Sonuçları göster
        self.show_results()
        
        return True
    
    def show_results(self):
        """Sonuçları göster"""
        print("\n" + "=" * 60)
        print("📊 KONTROL SONUÇLARI")
        print("=" * 60)
        print(f"Toplam Kontrol : {self.results['checked']}")
        print(f"✅ Aktif       : {self.results['active']}")
        print(f"❌ Satıldı     : {self.results['sold']}")
        print(f"⚠️  Hata       : {self.results['error']}")
        print("=" * 60)
        
        if self.results['sold'] > 0:
            print("\n❌ SATILAN ARAÇLAR:")
            for detail in self.results['details']:
                if detail['status'] == 'sold':
                    print(f"   • {detail['car']} (İlan No: {detail['adNo']})")
        
        if self.results['error'] > 0:
            print("\n⚠️  HATA OLAN ARAÇLAR:")
            for detail in self.results['details']:
                if detail['status'] == 'error':
                    print(f"   • {detail['car']} (İlan No: {detail['adNo']})")
        
        # Rapor dosyası oluştur
        report_file = f"check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Detaylı rapor: {report_file}")
        print(f"🕐 Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def cleanup(self):
        """Temizlik"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Chrome kapatıldı")

def main():
    print("🚀 Günlük İlan Kontrol Botu Başlatılıyor...")
    print(f"📅 Kontrol sıklığı: Her {CHECK_INTERVAL_HOURS} saatte bir")
    print(f"🤖 Anti-bot modu: {'Aktif' if not HEADLESS else 'Headless'}")
    print(f"⏱️  Bekleme süresi: {CHECK_DELAY_MIN}-{CHECK_DELAY_MAX} saniye\n")
    
    if CONTINUOUS_MODE:
        run_count = 0
        while True:
            run_count += 1
            print(f"\n{'='*60}")
            print(f"🔄 KONTROL TURU #{run_count}")
            print(f"{'='*60}\n")
            
            checker = DailyChecker()
            try:
                checker.run_check()
            except KeyboardInterrupt:
                print("\n\n⚠️  Kullanıcı tarafından durduruldu!")
                checker.cleanup()
                break
            except Exception as e:
                print(f"\n❌ Beklenmeyen hata: {e}")
            finally:
                checker.cleanup()
            
            # Bir sonraki kontrole kadar bekle
            next_check = datetime.now() + timedelta(hours=CHECK_INTERVAL_HOURS)
            print(f"\n⏰ Sonraki kontrol: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"💤 {CHECK_INTERVAL_HOURS} saat bekleniyor...\n")
            
            try:
                time.sleep(CHECK_INTERVAL_HOURS * 3600)
            except KeyboardInterrupt:
                print("\n\n⚠️  Kullanıcı tarafından durduruldu!")
                break
    else:
        # Tek seferlik çalıştırma
        checker = DailyChecker()
        try:
            checker.run_check()
        except KeyboardInterrupt:
            print("\n\n⚠️  Kullanıcı tarafından durduruldu!")
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
        finally:
            checker.cleanup()

if __name__ == '__main__':
    main()
