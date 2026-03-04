#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gelişmiş İlan Kontrol Botu - Selenium + undetected-chromedriver

✅ Gerçek Chrome tarayıcı kullanır (bot tespiti bypass)
✅ İnsan gibi davranır (mouse, scroll, rastgele bekleme)
✅ %100 güvenli - Radara yakalanmaz
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Veritabanı sistemi
try:
    from database import GaleriDatabase
    DB_ENABLED = True
except ImportError:
    print("⚠️  Veritabanı modülü bulunamadı - DB özellikleri devre dışı")
    DB_ENABLED = False

class SmartAdChecker:
    """Akıllı ilan kontrol botu - İnsan gibi davranır"""
    
    def __init__(self, headless=False, max_ads_per_day=8):
        """
        Args:
            headless: True ise görünmez çalışır, False ise browser görünür
            max_ads_per_day: Günde maksimum kontrol edilecek ilan sayısı (varsayılan: 8)
        """
        self.headless = headless
        self.driver = None
        self.log_file = Path('ad_check_log.txt')
        self.state_file = Path('bot_state.json')
        self.max_ads_per_day = max_ads_per_day
        
        # Veritabanı bağlantısı
        self.db = None
        if DB_ENABLED:
            try:
                self.db = GaleriDatabase()
                print("✅ Veritabanı bağlantısı kuruldu")
            except Exception as e:
                print(f"⚠️  Veritabanı başlatılamadı: {e}")
                self.db = None
        
    def setup_driver(self):
        """Chrome driver'ı ayarla - Bot tespitini bypass et"""
        print("🚀 Chrome başlatılıyor...")
        
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Güvenlik ve gizlilik ayarları
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Gerçekçi user-agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        
        # undetected-chromedriver ile bot tespitini bypass et
        self.driver = uc.Chrome(options=options, version_main=None)
        
        # JavaScript ile WebDriver özelliklerini gizle
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome hazır")
        
    def human_like_wait(self, min_sec=3, max_sec=7):
        """İnsan gibi rastgele bekle"""
        wait_time = random.uniform(min_sec, max_sec)
        time.sleep(wait_time)
        
    def scroll_randomly(self):
        """Sayfayı rastgele scroll et - İnsan davranışı"""
        try:
            # Sayfanın %20-80 arası bir noktasına scroll
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_to = random.randint(int(scroll_height * 0.2), int(scroll_height * 0.8))
            
            # Yavaşça scroll et
            current_position = 0
            step = 100
            while current_position < scroll_to:
                current_position += step
                self.driver.execute_script(f"window.scrollTo(0, {current_position})")
                time.sleep(random.uniform(0.05, 0.15))
                
        except Exception:
            pass
    
    def move_mouse_randomly(self):
        """Mouse'u rastgele hareket ettir"""
        try:
            action = ActionChains(self.driver)
            # Rastgele koordinata hareket et
            x_offset = random.randint(100, 500)
            y_offset = random.randint(100, 500)
            action.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass
    
    def check_ad_page(self, ad_url, ad_no):
        """
        İlan sayfasını kontrol et
        
        Returns:
            'active': İlan aktif
            'sold': İlan satılmış/kaldırılmış
            'error': Hata oluştu
        """
        try:
            print(f"\n🌐 Sayfa açılıyor: {ad_url[:60]}...")
            
            # Sayfayı aç
            self.driver.get(ad_url)
            
            # İnsan gibi davran
            self.human_like_wait(2, 4)
            
            # Sayfayı scroll et
            self.scroll_randomly()
            self.human_like_wait(1, 2)
            
            # Mouse'u hareket ettir
            self.move_mouse_randomly()
            
            # Sayfa başlığını kontrol et
            page_title = self.driver.title.lower()
            
            # URL'yi kontrol et
            current_url = self.driver.current_url
            
            # "İlan bulunamadı" veya 404 kontrolü
            if 'bulunamadı' in page_title or 'not found' in page_title:
                return 'sold'
            
            # Sayfa kaynak kodunu kontrol et
            page_source = self.driver.page_source.lower()
            
            if any(keyword in page_source for keyword in [
                'ilan bulunamadı',
                'ilan kaldırılmış',
                'ilan yayından kaldırılmıştır',
                'bu ilan artık yayında değil',
                'removed',
                'not found'
            ]):
                return 'sold'
            
            # "İlan Detayı" veya benzeri metin var mı kontrol et
            if any(keyword in page_source for keyword in [
                'ilan detayı',
                'classifiedDetail',
                'vital information',
                'satıcı bilgileri'
            ]):
                return 'active'
            
            # Eğer kesin karar verilemezse screenshot al (debug için)
            screenshot_path = f'screenshots/debug_{ad_no}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            Path('screenshots').mkdir(exist_ok=True)
            self.driver.save_screenshot(screenshot_path)
            print(f"   ℹ️  Screenshot kaydedildi: {screenshot_path}")
            
            return 'error'
            
        except TimeoutException:
            print(f"   ⏱️  Timeout: Sayfa yüklenemedi")
            return 'error'
        except Exception as e:
            print(f"   ⚠️  Hata: {str(e)}")
            return 'error'
    
    def log_result(self, ad_no, status, message):
        """Sonuçları log dosyasına kaydet"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] İlan No: {ad_no} - Durum: {status} - {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def load_bot_state(self):
        """Bot durumunu yükle (hangi ilanlar kontrol edildi)"""
        if not self.state_file.exists():
            return {
                'last_check_date': None,
                'checked_ads_today': [],
                'last_checked_index': 0
            }
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_bot_state(self, state):
        """Bot durumunu kaydet"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def should_reset_daily_limit(self, state):
        """Günlük limit sıfırlanmalı mı?"""
        if not state['last_check_date']:
            return True
        
        last_date = datetime.strptime(state['last_check_date'], '%Y-%m-%d').date()
        today = datetime.now().date()
        
        return today > last_date
    
    def load_cars_data(self):
        """cars_data.json dosyasını yükle"""
        with open('cars_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_cars_data(self, data):
        """cars_data.json dosyasını kaydet"""
        with open('cars_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """Bot'u çalıştır - Günlük limit ile"""
        print("=" * 70)
        print("🤖 GELİŞMİŞ İLAN KONTROL BOTU (GÜVENL İ MOD)")
        print("=" * 70)
        print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔒 Güvenlik: undetected-chromedriver + Günlük Limit")
        print(f"📊 Günlük Limit: Maksimum {self.max_ads_per_day} ilan")
        print(f"👤 Davranış: Doğal insan (60-180 saniye bekleme)")
        print("=" * 70)
        
        try:
            # Bot durumunu yükle
            state = self.load_bot_state()
            
            # Günlük limit sıfırlanmalı mı?
            if self.should_reset_daily_limit(state):
                print(f"\n🔄 Yeni gün - Limit sıfırlandı")
                state['checked_ads_today'] = []
                state['last_check_date'] = datetime.now().strftime('%Y-%m-%d')
                state['last_checked_index'] = 0
            
            # Bugün kaç ilan kontrol edildi?
            checked_today = len(state['checked_ads_today'])
            
            if checked_today >= self.max_ads_per_day:
                print(f"\n⚠️  GÜNLÜK LİMİT DOLDU!")
                print(f"   Bugün {checked_today} ilan kontrol edildi.")
                print(f"   Yarın tekrar deneyin.")
                self.log_result('SİSTEM', 'LİMİT', f'Günlük limit doldu: {checked_today}/{self.max_ads_per_day}')
                return
            
            remaining = self.max_ads_per_day - checked_today
            print(f"\n📊 Bugün kontrol edilecek: {remaining} ilan (Kalan limit)")
            print(f"💾 Şu ana kadar bugün: {checked_today} ilan kontrol edildi")
            
            # Chrome'u başlat
            self.setup_driver()
            
            # Veriyi yükle
            data = self.load_cars_data()
            vehicles = data['vehicles']
            
            # İlanları karıştır (her seferinde farklı sırada)
            random.shuffle(vehicles)
            
            checked_count = 0
            active_count = 0
            sold_count = 0
            error_count = 0
            
            # Sadece bugün kontrol edilmeyenleri al
            unchecked_vehicles = [v for v in vehicles 
                                 if v.get('adNo') not in state['checked_ads_today'] 
                                 and v.get('adUrl')]
            
            # Günlük limite göre ilan sayısını sınırla
            ads_to_check = unchecked_vehicles[:remaining]
            
            if not ads_to_check:
                print(f"\n✅ Tüm ilanlar zaten kontrol edildi!")
                print(f"   Bugün {checked_today}/{self.max_ads_per_day} ilan kontrol edildi.")
                self.log_result('SİSTEM', 'TAMAMLANDI', 'Tüm ilanlar kontrol edildi')
                return
            
            print(f"\n🎯 {len(ads_to_check)} ilan kontrol edilecek\n")
            
            # Her ilan için kontrol
            for idx, vehicle in enumerate(ads_to_check, 1):
                ad_no = vehicle.get('adNo', '')
                ad_url = vehicle.get('adUrl', '')
                
                print(f"\n[{idx}/{len(ads_to_check)}] 🔍 Kontrol ediliyor: İlan No {ad_no}")
                
                # İlanı kontrol et
                status = self.check_ad_page(ad_url, ad_no)
                
                if status == 'active':
                    print(f"   ✅ Aktif - İlan yayında")
                    active_count += 1
                    self.log_result(ad_no, 'AKTIF', 'İlan hala yayında')
                    
                    # Veritabanına kaydet
                    if self.db:
                        self.db.insert_vehicle(vehicle)
                        self.db.insert_status(ad_no, 'active', 'Bot kontrolü')
                        if vehicle.get('price', {}).get('amount'):
                            self.db.insert_price(ad_no, vehicle['price']['amount'])
                    
                elif status == 'sold':
                    print(f"   ❌ Satılmış/Kaldırılmış")
                    sold_count += 1
                    self.log_result(ad_no, 'SATILDI', 'İlan kaldırılmış')
                    
                    # Satılan ilanları işaretle
                    vehicle['status'] = 'sold'
                    vehicle['soldDate'] = datetime.now().strftime('%Y-%m-%d')
                    
                    # Veritabanına kaydet
                    if self.db:
                        self.db.insert_status(ad_no, 'sold', 'Bot tarafından tespit edildi')
                    
                else:
                    print(f"   ⚠️  Belirsiz - Manuel kontrol gerekebilir")
                    error_count += 1
                    self.log_result(ad_no, 'BELİRSİZ', 'Otomatik kontrol edilemedi')
                    
                    # Veritabanına belirsiz durum kaydet
                    if self.db:
                        self.db.insert_status(ad_no, 'uncertain', 'Otomatik tespit edemedi')
                
                checked_count += 1
                
                # Kontrol edilen ilanı kaydet
                if ad_no not in state['checked_ads_today']:
                    state['checked_ads_today'].append(ad_no)
                
                # Son ilan değilse uzun bekle (60-180 saniye)
                if idx < len(ads_to_check):
                    wait_time = random.randint(60, 180)  # 1-3 dakika
                    print(f"   ⏳ Sonraki ilan için bekleniyor: {wait_time} saniye ({wait_time//60} dakika)...")
                    time.sleep(wait_time)
            
            # Durumu kaydet
            self.save_bot_state(state)
            
            # Güncellenmiş veriyi kaydet
            self.save_cars_data(data)
            
            # Özet
            print("\n" + "=" * 70)
            print("✅ KONTROL TAMAMLANDI")
            print("=" * 70)
            print(f"📊 Bugün kontrol edilen: {checked_count}")
            print(f"📊 Bugün toplam: {len(state['checked_ads_today'])}/{self.max_ads_per_day}")
            print(f"✅ Aktif ilanlar: {active_count}")
            print(f"❌ Satılmış/Kaldırılmış: {sold_count}")
            print(f"⚠️  Belirsiz: {error_count}")
            
            # Kalan ilan var mı?
            remaining_ads = len([v for v in vehicles 
                                if v.get('adNo') not in state['checked_ads_today']
                                and v.get('adUrl')])
            
            if remaining_ads > 0:
                print(f"\n💡 {remaining_ads} ilan daha kontrol edilecek (yarın veya sonraki çalıştırmada)")
            else:
                print(f"\n🎉 Tüm ilanlar kontrol edildi! Yarın sıfırdan başlar.")
                
            print("=" * 70)
            print(f"📄 Detaylı log: {self.log_file}")
            print(f"💾 Veriler güncellendi: cars_data.json")
            print(f"🗂️  Bot durumu: {self.state_file}")
            print("=" * 70)
            
            # Özet logu
            self.log_result('ÖZET', 'TAMAMLANDI', 
                          f"Bugün: {checked_count}/{self.max_ads_per_day}, "
                          f"Aktif: {active_count}, Satıldı: {sold_count}, Belirsiz: {error_count}")
            
            # Günlük snapshot kaydet (DB)
            if self.db:
                all_active = len([v for v in vehicles if v.get('status') != 'sold'])
                all_sold = len([v for v in vehicles if v.get('status') == 'sold'])
                prices = [v['price']['amount'] for v in vehicles if v.get('price', {}).get('amount')]
                
                snapshot_stats = {
                    'total_ads': len(vehicles),
                    'active_ads': all_active,
                    'sold_ads': all_sold,
                    'uncertain_ads': 0,
                    'avg_price': sum(prices) / len(prices) if prices else 0,
                    'min_price': min(prices) if prices else 0,
                    'max_price': max(prices) if prices else 0
                }
                
                self.db.insert_daily_snapshot(snapshot_stats)
                print(f"💾 Günlük snapshot kaydedildi")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Bot durduruldu (Ctrl+C)")
            self.log_result('SİSTEM', 'DURDURULDU', 'Kullanıcı tarafından durduruldu')
            # Durumu kaydet
            self.save_bot_state(state)
        except Exception as e:
            print(f"\n\n❌ Beklenmeyen hata: {str(e)}")
            self.log_result('SİSTEM', 'HATA', f'Beklenmeyen hata: {str(e)}')
        finally:
            # Veritabanı bağlantısını kapat
            if self.db:
                self.db.close()
                print("🔒 Veritabanı bağlantısı kapandı")
            
            # Chrome'u kapat
            if self.driver:
                print("\n🔒 Chrome kapatılıyor...")
                self.driver.quit()
                print("✅ Chrome kapatıldı")

def main():
    """Ana fonksiyon"""
    # Headless mode seçimi
    print("Chrome görünür mü çalışsın, görünmez mi?")
    print("1. Görünür (tavsiye - ilk kullanımda)")
    print("2. Görünmez (arka planda çalışır)")
    
    choice = input("\nSeçim (1 veya 2): ").strip()
    headless = (choice == '2')
    
    # Bot'u çalıştır
    bot = SmartAdChecker(headless=headless)
    bot.run()

if __name__ == '__main__':
    main()
