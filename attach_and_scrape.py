from chrome_scraper import connect_to_chrome, scrape_gallery, update_database, generate_dashboard
import json, sys

url = "https://www.sahibinden.com/otomobil/kocaeli-cayirova/galeriden"
pages = 400

print('→ Chrome debug bağlanıyor...')
browser = connect_to_chrome()
if not browser:
    print('❌ Chrome debug portuna bağlanılamadı (9222). Tarayıcıyı --remote-debugging-port=9222 ile başlattığından emin ol).')
    sys.exit(1)

print('→ Tarama başlatılıyor (sayfa sayisi:', pages, ')')
data = scrape_gallery(browser, url, pages)
print('\n→ Tarama tamamlandı, kayıt sayısı =', len(data))

# Veritabanını güncelle
update_database(url, data)

# JSON kaydet
with open('all_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('→ all_data.json kaydedildi')

# Dashboard oluştur
try:
    generate_dashboard('dashboard.html')
    print('→ dashboard.html oluşturuldu')
except Exception as e:
    print('⚠️ Dashboard oluşturulurken hata:', e)

print('Bitti')
