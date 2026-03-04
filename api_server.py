"""
Basit API Server - Araç durumunu güncelleme
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path
from database import GaleriDatabase

app = Flask(__name__)
CORS(app)  # Tarayıcıdan AJAX çağrıları için

db = GaleriDatabase()

@app.route('/api/mark-sold', methods=['POST'])
def mark_sold():
    """Aracı satıldı olarak işaretle"""
    try:
        data = request.json
        ad_no = data.get('adNo')
        
        if not ad_no:
            return jsonify({'success': False, 'error': 'İlan No gerekli'}), 400
        
        # JSON dosyasını güncelle
        json_path = Path('cars_data.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                cars_data = json.load(f)
            
            # Aracı bul ve durumunu güncelle
            updated = False
            for vehicle in cars_data.get('vehicles', []):
                v_ad_no = vehicle.get('adNo') or vehicle.get('ilan_no') or vehicle.get('İlan No')
                if str(v_ad_no) == str(ad_no):
                    vehicle['status'] = 'sold'
                    updated = True
                    break
            
            if updated:
                # JSON'u kaydet
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(cars_data, f, ensure_ascii=False, indent=2)
                
                # Veritabanını güncelle
                db.connect()
                db.cursor.execute("""
                    INSERT INTO status_history (ad_no, status, note)
                    VALUES (?, 'sold', 'Manuel olarak satıldı işaretlendi')
                """, (ad_no,))
                db.conn.commit()
                db.close()
                
                return jsonify({'success': True, 'message': 'Araç satıldı olarak işaretlendi'})
            else:
                return jsonify({'success': False, 'error': 'Araç bulunamadı'}), 404
        else:
            return jsonify({'success': False, 'error': 'Veri dosyası bulunamadı'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mark-active', methods=['POST'])
def mark_active():
    """Aracı aktif olarak işaretle"""
    try:
        data = request.json
        ad_no = data.get('adNo')
        
        if not ad_no:
            return jsonify({'success': False, 'error': 'İlan No gerekli'}), 400
        
        # JSON dosyasını güncelle
        json_path = Path('cars_data.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                cars_data = json.load(f)
            
            # Aracı bul ve durumunu güncelle
            updated = False
            for vehicle in cars_data.get('vehicles', []):
                v_ad_no = vehicle.get('adNo') or vehicle.get('ilan_no') or vehicle.get('İlan No')
                if str(v_ad_no) == str(ad_no):
                    vehicle['status'] = 'active'
                    updated = True
                    break
            
            if updated:
                # JSON'u kaydet
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(cars_data, f, ensure_ascii=False, indent=2)
                
                # Veritabanını güncelle
                db.connect()
                db.cursor.execute("""
                    INSERT INTO status_history (ad_no, status, note)
                    VALUES (?, 'active', 'Manuel olarak aktif işaretlendi')
                """, (ad_no,))
                db.conn.commit()
                db.close()
                
                return jsonify({'success': True, 'message': 'Araç aktif olarak işaretlendi'})
            else:
                return jsonify({'success': False, 'error': 'Araç bulunamadı'}), 404
        else:
            return jsonify({'success': False, 'error': 'Veri dosyası bulunamadı'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/add-vehicle', methods=['POST'])
def add_vehicle():
    """Yeni araç ekle"""
    try:
        vehicle_data = request.json
        
        if not vehicle_data:
            return jsonify({'success': False, 'error': 'Araç verisi gerekli'}), 400
        
        # Zorunlu alanları kontrol et
        required_fields = ['vehicle', 'price', 'seller', 'location']
        for field in required_fields:
            if field not in vehicle_data:
                return jsonify({'success': False, 'error': f'{field} alanı gerekli'}), 400
        
        # JSON dosyasını güncelle
        json_path = Path('cars_data.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                cars_data = json.load(f)
        else:
            cars_data = {'vehicles': []}
        
        # Araç verisine varsayılan değerler ekle
        if 'status' not in vehicle_data:
            vehicle_data['status'] = 'active'
        
        if 'daysListed' not in vehicle_data:
            vehicle_data['daysListed'] = 0
        
        # Aracı listeye ekle
        cars_data['vehicles'].append(vehicle_data)
        
        # JSON'u kaydet
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cars_data, f, ensure_ascii=False, indent=2)
        
        # Veritabanına ekle
        try:
            db.connect()
            db.cursor.execute("""
                INSERT INTO vehicles (
                    ad_no, brand, model, year, engine, transmission, 
                    fuel_type, body_type, color, km, gallery, region, ad_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_data.get('adNo'),
                vehicle_data['vehicle'].get('brand'),
                vehicle_data['vehicle'].get('model'),
                vehicle_data['vehicle'].get('year'),
                vehicle_data['vehicle'].get('engine'),
                vehicle_data['vehicle'].get('transmission'),
                vehicle_data['vehicle'].get('fuel'),
                vehicle_data['vehicle'].get('body_type'),
                vehicle_data['vehicle'].get('color'),
                vehicle_data['vehicle'].get('km'),
                vehicle_data['seller'].get('name'),
                vehicle_data['location'].get('region'),
                vehicle_data.get('adUrl')
            ))
            
            # Fiyat geçmişine ekle
            db.cursor.execute("""
                INSERT INTO price_history (ad_no, price, currency)
                VALUES (?, ?, 'TRY')
            """, (vehicle_data.get('adNo'), vehicle_data.get('price')))
            
            db.conn.commit()
            db.close()
        except Exception as db_error:
            print(f"Veritabanı hatası: {db_error}")
            # JSON eklendi ama DB eklenmedi, yine de başarılı say
        
        return jsonify({
            'success': True, 
            'message': 'Araç başarıyla eklendi',
            'vehicleCount': len(cars_data['vehicles'])
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 API Server başlatılıyor...")
    print("📍 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
