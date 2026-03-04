from datetime import datetime

test_date = '22.02.2026'
print(f"Test: {test_date}")

for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
    try:
        pub_dt = datetime.strptime(test_date, fmt)
        result = pub_dt.strftime("%Y-%m-%d")
        print(f"✓ Format {fmt} başarılı: {result}")
        break
    except Exception as e:
        print(f"✗ Format {fmt} hata: {str(e)[:30]}")
