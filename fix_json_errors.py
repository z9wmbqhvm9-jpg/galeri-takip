import re

# 1. Dosyayı oku
with open('cars_data.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 2. Hatalı satırları düzelt
# publishDate satırındaki hatalı `,`n    "daysListed": 1,` ifadesini düzelt
raw = re.sub(r',`n\s+"daysListed":\s*([0-9]+),', r', "daysListed": \1,', raw)

# 3. Sonundaki fazladan kodu ve hatalı satırları kaldır
# JSON dosyasının sonunu doğru kapat
if '"engine":' in raw:
    # Fazladan kodu ve hatalı satırları kaldırmak için son geçerli JSON kapanışını bul
    idx = raw.rfind('}')
    raw = raw[:idx+1]

# 4. Dosyayı kaydet
with open('cars_data_fixed.json', 'w', encoding='utf-8') as f:
    f.write(raw)

print('cars_data_fixed.json dosyası otomatik olarak düzeltildi.')
