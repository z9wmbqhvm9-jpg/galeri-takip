#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Araç Verisi İşleme Scripti
Metin formatında araç bilgisi alıp JSON'a ve Dashboard'a ekler
"""

import json
import os
from datetime import datetime
import re

class VehicleDataProcessor:
    def __init__(self):
        self.data_file = 'cars_data.json'
        self.html_file = 'dashboard_new.html'
        self.load_data()
    
    def load_data(self):
        """Mevcut JSON verilerini yükle"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"vehicles": [], "regions": {
                "Çayırova": [], "Gebze": [], "DerÇiftliği": [], 
                "İzmit": [], "Diğer": []
            }}
    
    def parse_vehicle_data(self, text):
        """Metin formatını parse et ve araç verisi oluştur"""
        lines = text.strip().split('\n')
        vehicle = {}
        inspection = {}
        in_inspection = False
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                if line.lower() == 'hasar:':
                    in_inspection = True
                continue
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if in_inspection:
                # Hasar bilgisini parse et
                if '-' in value:
                    part = value.split('-')[0].strip()
                    status = value.split('-')[1].strip()
                    inspection[part] = status
            else:
                # Temel bilgileri parse et
                if key == 'marka':
                    vehicle['brand'] = value
                elif key == 'model':
                    vehicle['model'] = value
                elif key == 'yıl':
                    vehicle['year'] = int(value) if value.isdigit() else value
                elif key == 'motor':
                    vehicle['engine'] = value
                elif key == 'paket':
                    vehicle['package'] = value
                elif key == 'km':
                    vehicle['km'] = int(value.replace('.', '')) if value.replace('.', '').isdigit() else value
                elif key == 'fiyat':
                    vehicle['price'] = int(value.replace('.', '')) if value.replace('.', '').isdigit() else value
                elif key == 'galeri':
                    vehicle['seller_name'] = value
                elif key == 'bölge':
                    vehicle['region'] = value
                elif key == 'renk':
                    vehicle['color'] = value
                elif key == 'yakıt':
                    vehicle['fuel'] = value
                elif key == 'vites':
                    vehicle['transmission'] = value
                elif key == 'hp':
                    vehicle['hp'] = int(value) if value.isdigit() else value
        
        if inspection:
            vehicle['inspection'] = inspection
        
        return vehicle
    
    def create_vehicle_object(self, parsed_data):
        """Parse edilen veriyi tam vehicle object'e çevir"""
        today = datetime.now().strftime('%Y-%m-%d')
        vehicle_id = str(int(datetime.now().timestamp() * 1000) % 10000000000)
        
        region = parsed_data.get('region', 'Diğer')
        seller = parsed_data.get('seller_name', 'Bilinmiyor')
        
        vehicle = {
            "id": vehicle_id,
            "publishDate": today,
            "daysListed": 0,
            "vehicle": {
                "year": parsed_data.get('year', ''),
                "brand": parsed_data.get('brand', ''),
                "model": parsed_data.get('model', ''),
                "engine": parsed_data.get('engine', ''),
                "package": parsed_data.get('package', ''),
                "fuel": parsed_data.get('fuel', 'Benzin'),
                "transmission": parsed_data.get('transmission', 'Manuel'),
                "km": parsed_data.get('km', 0),
                "hp": parsed_data.get('hp', 0),
                "color": parsed_data.get('color', '')
            },
            "price": parsed_data.get('price', 0),
            "seller": {
                "name": seller,
                "type": "Galeri",
                "phone": "",
                "url": ""
            },
            "location": {
                "city": "Kocaeli",
                "district": region,
                "region": region,
                "neighborhood": ""
            },
            "condition": {
                "status": "İkinci El",
                "heavyDamaged": False,
                "warranty": False,
                "exchange": False
            },
            "description": "",
            "features": [],
            "inspection": parsed_data.get('inspection', {})
        }
        
        return vehicle, region
    
    def add_vehicle(self, vehicle_data_text):
        """Yeni araç ekle"""
        try:
            parsed = self.parse_vehicle_data(vehicle_data_text)
            vehicle, region = self.create_vehicle_object(parsed)
            
            self.data['vehicles'].append(vehicle)
            
            if region in self.data['regions']:
                self.data['regions'][region].append(vehicle['id'])
            else:
                self.data['regions'][region] = [vehicle['id']]
            
            self.save_data()
            return vehicle, region
        except Exception as e:
            return None, str(e)
    
    def save_data(self):
        """JSON verilerini kaydet"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✅ Veriler kaydedildi: {self.data_file}")
    
    def generate_inspection_html(self, inspection):
        """Hasar tablosu HTML'i oluştur"""
        if not inspection:
            inspection = {"Motor": "Orijinal", "Şanzıman": "Orijinal"}
        
        rows = ""
        for part, status in inspection.items():
            status_lower = status.lower()
            
            if 'orijinal' in status_lower:
                badge = '<span class="status-original">Orijinal</span>'
            elif 'boyalı' in status_lower or 'boya' in status_lower:
                badge = '<span class="status-painted">Boyalı</span>'
            elif 'değişti' in status_lower or 'değişen' in status_lower:
                badge = '<span class="status-changed">Değişti</span>'
            else:
                badge = f'<span class="status-original">{status}</span>'
            
            rows += f"""
                                    <tr>
                                        <td>{part}</td>
                                        <td>{badge}</td>
                                    </tr>"""
        
        return rows
    
    def generate_vehicle_card_html(self, vehicle):
        """Araç kartı HTML'i oluştur"""
        v = vehicle['vehicle']
        inspection_rows = self.generate_inspection_html(vehicle.get('inspection', {}))
        
        features_html = ""
        if vehicle.get('features'):
            for feature in vehicle['features']:
                features_html += f'<span class="feature-tag">{feature}</span>'
        
        card_html = f"""
                <div class="vehicle-card">
                    <div class="vehicle-header">
                        <div class="vehicle-title">{v['year']} {v['brand']} {v['model']}</div>
                        <div class="vehicle-location">{vehicle['location']['region']}, {vehicle['location']['city']}</div>
                    </div>
                    <div class="vehicle-body">
                        <div class="info-row">
                            <span class="info-label">Yayın Tarihi:</span>
                            <span class="info-value">{vehicle['publishDate']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">İlanda Gün:</span>
                            <span class="info-value">{vehicle['daysListed']} gün</span>
                        </div>
                        <div class="days-badge">✨ Yeni İlan</div>
                        
                        <div class="info-row" style="margin-top: 15px;">
                            <span class="info-label">Model:</span>
                            <span class="info-value">{v['engine']} {v['package']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Yakıt:</span>
                            <span class="info-value">{v['fuel']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">KM:</span>
                            <span class="info-value">{v['km']:,} km</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Güç:</span>
                            <span class="info-value">{v['hp']} HP</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Renk:</span>
                            <span class="info-value">{v['color']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Durum:</span>
                            <span class="info-value">{vehicle['condition']['status']}</span>
                        </div>
                        
                        {f'<div class="features"><strong style="display: block; margin-bottom: 8px;">Özellikler:</strong>{features_html}</div>' if features_html else ''}
                        
                        <div class="price-tag">{vehicle['price']:,} TL</div>
                        
                        <div class="seller-info">
                            <div class="seller-name">{vehicle['seller']['name']}</div>
                            <div style="margin-bottom: 8px;">{vehicle['seller']['type']}</div>
                            {f'<a href="tel:{vehicle["seller"]["phone"]}" class="seller-phone">📞 {vehicle["seller"]["phone"]}</a>' if vehicle['seller']['phone'] else ''}
                        </div>
                        
                        <!-- HASAR / DURUM ŞEMASI -->
                        <div class="inspection-section">
                            <div class="inspection-title">🔍 Araç Durum Raporu</div>
                            
                            <table class="inspection-table">
                                <thead>
                                    <tr>
                                        <th>Araç Parçası</th>
                                        <th>Durum</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {inspection_rows}
                                </tbody>
                            </table>
                            
                            <div class="legend">
                                <div class="legend-item">
                                    <div class="legend-box" style="background: #10b981;"></div>
                                    <span>Orijinal</span>
                                </div>
                                <div class="legend-item">
                                    <div class="legend-box" style="background: #fbbf24;"></div>
                                    <span>Boyalı</span>
                                </div>
                                <div class="legend-item">
                                    <div class="legend-box" style="background: #ef4444;"></div>
                                    <span>Değişmiş</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""
        
        return card_html
    
    def update_html(self):
        """Dashboard HTML'ini güncelle"""
        # Bölgelere göre araçları grupla
        region_vehicles = {}
        for region in self.data['regions']:
            region_vehicles[region] = []
        
        for vehicle in self.data['vehicles']:
            region = vehicle['location']['region']
            if region not in region_vehicles:
                region_vehicles[region] = []
            region_vehicles[region].append(vehicle)
        
        # HTML şablonunu oluştur
        regions_html = ""
        
        for region, vehicles in region_vehicles.items():
            if vehicles:
                vehicles_grid = ""
                for vehicle in vehicles:
                    vehicles_grid += self.generate_vehicle_card_html(vehicle)
                
                regions_html += f"""
        <!-- {region.upper()} BÖLGESI -->
        <div class="region-container">
            <div class="region-title">📍 {region} Bölgesi</div>
            <div class="vehicles-grid">
                {vehicles_grid}
            </div>
        </div>
        """
            else:
                regions_html += f"""
        <!-- {region.upper()} BÖLGESI -->
        <div class="region-container">
            <div class="region-title">📍 {region} Bölgesi</div>
            <div class="empty-region">
                <p>Bu bölgede henüz araç yok.</p>
            </div>
        </div>
        """
        
        # Toplam araç sayısı
        total_vehicles = len(self.data['vehicles'])
        
        # HTML şablonunu oku ve güncelle
        with open(self.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Placeholder'ları değiştir
        import re
        html_content = re.sub(
            r'<div class="stat-number" id="total-vehicles">.*?</div>',
            f'<div class="stat-number" id="total-vehicles">{total_vehicles}</div>',
            html_content
        )
        
        # Bölgeleri değiştir - <!-- REGION_PLACEHOLDER --> ile başlayan bölümü bul
        pattern = r'<!-- ÇAYIROVA BÖLGESİ -->.*?<!-- DİĞER BÖLGELER -->.*?</div>\s*</div>\s*<script>'
        html_content = re.sub(
            pattern,
            regions_html + '\n    </div>\n    <script>',
            html_content,
            flags=re.DOTALL
        )
        
        # HTML'i kaydet
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard güncellendu: {self.html_file}")


def main():
    processor = VehicleDataProcessor()
    
    print("\n" + "="*60)
    print("🚗 ARAÇ EKLE - Araç Bilgisini Giriniz")
    print("="*60)
    print("Örnek format:")
    print("""
Marka: Toyota
Model: Corolla
Yıl: 2018
Motor: 1.6 Benzin
Paket: Standart
KM: 85000
Fiyat: 450000
Galeri: XYZ Oto
Bölge: Gebze
Renk: Siyah
Yakıt: Benzin
Vites: Otomatik
HP: 120

Hasar:
- Motor: Orijinal
- Şanzıman: Orijinal
- Ön Tampon: Boyalı
- Kaput: Değişti
    """)
    print("="*60)
    print("Bitirmek için boş satır bırak ve Enter bas\n")
    
    lines = []
    while True:
        try:
            line = input()
            if not line.strip():
                if lines:
                    break
            else:
                lines.append(line)
        except EOFError:
            break
    
    if not lines:
        print("❌ Veri girilmedi.")
        return
    
    vehicle_text = '\n'.join(lines)
    
    vehicle, region = processor.add_vehicle(vehicle_text)
    
    if vehicle:
        print("\n✅ Araç başarıyla eklendi!")
        print(f"   Marka: {vehicle['vehicle']['brand']} {vehicle['vehicle']['model']}")
        print(f"   Yıl: {vehicle['vehicle']['year']}")
        print(f"   Fiyat: {vehicle['price']:,} TL")
        print(f"   Bölge: {region}")
        
        processor.update_html()
        print("\n✅ Dashboard güncellendu!")
        print(f"📊 Toplam araç: {len(processor.data['vehicles'])}")
    else:
        print(f"\n❌ Hata: {region}")


if __name__ == "__main__":
    main()
