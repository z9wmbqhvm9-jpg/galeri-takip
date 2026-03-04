"""
Galeri Takip - Veritabanı Yönetim Sistemi
SQLite ile ilan geçmişi, fiyat takibi, trend analizi
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class GaleriDatabase:
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self, db_path: str = "galeri_takip.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def connect(self):
        """Veritabanına bağlan"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Dict-like access
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Bağlantıyı kapat"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """Veritabanı şemasını oluştur"""
        self.connect()
        
        # İlanlar tablosu (temel bilgiler)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_no TEXT UNIQUE NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                engine TEXT,
                transmission TEXT,
                fuel_type TEXT,
                body_type TEXT,
                color TEXT,
                km INTEGER,
                gallery TEXT,
                region TEXT,
                ad_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Fiyat geçmişi tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_no TEXT NOT NULL,
                price INTEGER NOT NULL,
                currency TEXT DEFAULT 'TRY',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ad_no) REFERENCES vehicles(ad_no)
            )
        """)
        
        # Durum geçmişi tablosu (aktif/satıldı)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_no TEXT NOT NULL,
                status TEXT NOT NULL,
                check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                FOREIGN KEY (ad_no) REFERENCES vehicles(ad_no)
            )
        """)
        
        # Hasar/muayene bilgileri
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inspection_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_no TEXT NOT NULL,
                tramer_cost INTEGER,
                paint_parts TEXT,  -- JSON array
                replaced_parts TEXT,  -- JSON array
                damage_parts TEXT,  -- JSON array
                inspection_date DATE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ad_no) REFERENCES vehicles(ad_no)
            )
        """)
        
        # Günlük snapshot (bot çalıştırma kayıtları)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                total_ads INTEGER,
                active_ads INTEGER,
                sold_ads INTEGER,
                uncertain_ads INTEGER,
                avg_price REAL,
                min_price INTEGER,
                max_price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # İndeksler (hızlı sorgular için)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ad_no ON vehicles(ad_no)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_ad ON price_history(ad_no)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_ad ON status_history(ad_no)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_date ON daily_snapshots(snapshot_date)")
        
        self.conn.commit()
        print("✅ Veritabanı şeması hazır")
    
    def insert_vehicle(self, vehicle_data: Dict) -> bool:
        """Yeni araç ekle veya güncelle"""
        try:
            ad_no = vehicle_data.get('adNo')
            vehicle_info = vehicle_data.get('vehicle', {})
            location_info = vehicle_data.get('location', {})
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO vehicles 
                (ad_no, brand, model, year, engine, transmission, fuel_type, 
                 body_type, color, km, gallery, region, ad_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                ad_no,
                vehicle_info.get('brand'),
                vehicle_info.get('model'),
                vehicle_info.get('year'),
                vehicle_info.get('engine'),
                vehicle_info.get('transmission'),
                vehicle_info.get('fuelType'),
                vehicle_info.get('bodyType'),
                vehicle_info.get('color'),
                vehicle_info.get('km'),
                vehicle_data.get('seller', {}).get('name'),
                location_info.get('region'),
                vehicle_data.get('adUrl')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Araç eklenirken hata: {e}")
            return False
    
    def insert_price(self, ad_no: str, price: int, currency: str = 'TRY') -> bool:
        """Fiyat kaydı ekle"""
        try:
            self.cursor.execute("""
                INSERT INTO price_history (ad_no, price, currency)
                VALUES (?, ?, ?)
            """, (ad_no, price, currency))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Fiyat eklenirken hata: {e}")
            return False
    
    def insert_status(self, ad_no: str, status: str, note: str = None) -> bool:
        """Durum kaydı ekle (aktif/satıldı)"""
        try:
            self.cursor.execute("""
                INSERT INTO status_history (ad_no, status, note)
                VALUES (?, ?, ?)
            """, (ad_no, status, note))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Durum eklenirken hata: {e}")
            return False
    
    def get_price_history(self, ad_no: str) -> List[Dict]:
        """Bir ilanın fiyat geçmişini getir"""
        self.cursor.execute("""
            SELECT price, currency, recorded_at
            FROM price_history
            WHERE ad_no = ?
            ORDER BY recorded_at ASC
        """, (ad_no,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_status_history(self, ad_no: str) -> List[Dict]:
        """Bir ilanın durum geçmişini getir"""
        self.cursor.execute("""
            SELECT status, check_date, note
            FROM status_history
            WHERE ad_no = ?
            ORDER BY check_date DESC
        """, (ad_no,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_latest_status(self, ad_no: str) -> Optional[str]:
        """Son durum kaydını getir"""
        self.cursor.execute("""
            SELECT status
            FROM status_history
            WHERE ad_no = ?
            ORDER BY check_date DESC
            LIMIT 1
        """, (ad_no,))
        
        row = self.cursor.fetchone()
        return row['status'] if row else None
    
    def get_price_changes(self, ad_no: str) -> Optional[Dict]:
        """Fiyat değişikliklerini analiz et"""
        history = self.get_price_history(ad_no)
        
        if len(history) < 2:
            return None
        
        first_price = history[0]['price']
        last_price = history[-1]['price']
        change = last_price - first_price
        change_percent = (change / first_price) * 100 if first_price > 0 else 0
        
        return {
            'first_price': first_price,
            'last_price': last_price,
            'change': change,
            'change_percent': change_percent,
            'records': len(history)
        }
    
    def insert_daily_snapshot(self, stats: Dict) -> bool:
        """Günlük özet snapshot kaydet"""
        try:
            self.cursor.execute("""
                INSERT INTO daily_snapshots 
                (snapshot_date, total_ads, active_ads, sold_ads, uncertain_ads,
                 avg_price, min_price, max_price)
                VALUES (DATE('now'), ?, ?, ?, ?, ?, ?, ?)
            """, (
                stats.get('total_ads', 0),
                stats.get('active_ads', 0),
                stats.get('sold_ads', 0),
                stats.get('uncertain_ads', 0),
                stats.get('avg_price', 0),
                stats.get('min_price', 0),
                stats.get('max_price', 0)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Snapshot eklenirken hata: {e}")
            return False
    
    def get_trend_data(self, days: int = 30) -> List[Dict]:
        """Son X günün trend verilerini getir"""
        self.cursor.execute("""
            SELECT 
                snapshot_date,
                total_ads,
                active_ads,
                sold_ads,
                avg_price
            FROM daily_snapshots
            WHERE snapshot_date >= DATE('now', ?)
            ORDER BY snapshot_date ASC
        """, (f'-{days} days',))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Genel istatistikleri getir"""
        # Toplam araç sayısı
        self.cursor.execute("SELECT COUNT(*) as total FROM vehicles")
        total = self.cursor.fetchone()['total']
        
        # Aktif/satılan ilanlar (son durum)
        self.cursor.execute("""
            SELECT 
                v.ad_no,
                (SELECT status FROM status_history WHERE ad_no = v.ad_no 
                 ORDER BY check_date DESC LIMIT 1) as last_status
            FROM vehicles v
        """)
        
        statuses = [row['last_status'] for row in self.cursor.fetchall()]
        active_count = statuses.count('active')
        sold_count = statuses.count('sold')
        
        # Ortalama fiyat (her ilanın en son fiyatı)
        self.cursor.execute("""
            SELECT AVG(latest_price) as avg_price
            FROM (
                SELECT ad_no, price as latest_price
                FROM price_history
                WHERE (ad_no, recorded_at) IN (
                    SELECT ad_no, MAX(recorded_at)
                    FROM price_history
                    GROUP BY ad_no
                )
            )
        """)
        
        avg_price_row = self.cursor.fetchone()
        avg_price = avg_price_row['avg_price'] if avg_price_row else 0
        
        return {
            'total_vehicles': total,
            'active_ads': active_count,
            'sold_ads': sold_count,
            'avg_price': round(avg_price, 2) if avg_price else 0
        }
    
    def import_from_json(self, json_path: str = "cars_data.json") -> Tuple[int, int]:
        """
        Mevcut JSON verisini veritabanına aktar
        Returns: (başarılı, başarısız) tuple
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            success_count = 0
            fail_count = 0
            
            for vehicle in data.get('vehicles', []):
                # Kontrol: vehicle dict mi?
                if not isinstance(vehicle, dict):
                    print(f"⚠️  Geçersiz araç verisi atlanıyor: {vehicle}")
                    fail_count += 1
                    continue
                
                ad_no = vehicle.get('adNo')
                if not ad_no:
                    print(f"⚠️  İlan No eksik, atlanıyor")
                    fail_count += 1
                    continue
                
                # Aracı ekle
                if self.insert_vehicle(vehicle):
                    success_count += 1
                    
                    # Fiyat ekle (price integer veya dict olabilir)
                    price_info = vehicle.get('price')
                    if price_info:
                        if isinstance(price_info, dict):
                            # Dict formatı: { amount: 123, currency: 'TRY' }
                            if price_info.get('amount'):
                                self.insert_price(ad_no, price_info['amount'], price_info.get('currency', 'TRY'))
                        elif isinstance(price_info, (int, float)):
                            # Direkt sayı
                            self.insert_price(ad_no, int(price_info), 'TRY')
                    
                    # Durum ekle (varsa)
                    status = vehicle.get('status', 'active')
                    self.insert_status(ad_no, status)
                else:
                    fail_count += 1
            
            print(f"✅ Import tamamlandı: {success_count} başarılı, {fail_count} başarısız")
            return success_count, fail_count
            
        except Exception as e:
            print(f"❌ Import hatası: {e}")
            return 0, 0
    
    def export_to_csv(self, output_path: str = "export.csv") -> bool:
        """Veritabanını CSV'ye aktar"""
        try:
            import csv
            
            self.cursor.execute("""
                SELECT 
                    v.*,
                    (SELECT price FROM price_history WHERE ad_no = v.ad_no 
                     ORDER BY recorded_at DESC LIMIT 1) as current_price,
                    (SELECT status FROM status_history WHERE ad_no = v.ad_no 
                     ORDER BY check_date DESC LIMIT 1) as current_status
                FROM vehicles v
                ORDER BY v.created_at DESC
            """)
            
            rows = self.cursor.fetchall()
            
            if not rows:
                print("⚠️ Export edilecek veri yok")
                return False
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(row) for row in rows])
            
            print(f"✅ Export tamamlandı: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Export hatası: {e}")
            return False


# Kullanım örneği
if __name__ == "__main__":
    print("=" * 70)
    print("🗃️  GALERİ TAKİP - VERİTABANI SİSTEMİ")
    print("=" * 70)
    
    # Veritabanını başlat
    db = GaleriDatabase()
    
    # Mevcut JSON verisini import et
    print("\n📥 JSON verisini import ediliyor...")
    success, fail = db.import_from_json()
    
    # İstatistikleri göster
    print("\n📊 İstatistikler:")
    stats = db.get_statistics()
    print(f"   Toplam araç: {stats['total_vehicles']}")
    print(f"   Aktif ilanlar: {stats['active_ads']}")
    print(f"   Satılan ilanlar: {stats['sold_ads']}")
    print(f"   Ortalama fiyat: {stats['avg_price']:,.0f} TRY")
    
    # Trend verilerini göster
    print("\n📈 Son 7 günlük trend:")
    trends = db.get_trend_data(7)
    for trend in trends:
        print(f"   {trend['snapshot_date']}: {trend['active_ads']} aktif, {trend['sold_ads']} satıldı")
    
    # Bağlantıyı kapat
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ Veritabanı hazır: galeri_takip.db")
    print("=" * 70)
