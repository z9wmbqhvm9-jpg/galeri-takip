import json
import os

BASE = r'c:\Users\batuh\OneDrive\Masaüstü\galeritakip-main'
files = [
    'all_data.json', 'all_data_backup_before_clear.json', 'bot_state.json',
    'cars_data.json', 'cars_data_backup_before_clear.json', 'cars_data_cleaned.json',
    'cars_data_dashboard_ready.json', 'cars_data_final.json', 'cars_data_final_invalid.json',
    'cars_data_firstblock.json', 'cars_data_fixed.json', 'cars_data_fixed_clean.json',
    'cars_data_secondblock_invalid.json', 'check_report_20260225_050617.json',
    'ilan_sonuc.json', 'rich_data_input.json'
]

report = []
for f in files:
    path = os.path.join(BASE, f)
    if not os.path.exists(path):
        report.append(f"{f}: YOK")
        continue
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, list):
            report.append(f"{f}: LISTE {len(data)} kayit")
        elif isinstance(data, dict):
            vlist = data.get('vehicles', [])
            if vlist:
                report.append(f"{f}: DICT vehicles={len(vlist)}")
            else:
                report.append(f"{f}: DICT keys={list(data.keys())[:3]} (no vehicles)")
        else:
            report.append(f"{f}: diger tip")
    except Exception as e:
        report.append(f"{f}: HATA {str(e)[:60]}")

with open(os.path.join(BASE, 'scan_report.txt'), 'w', encoding='utf-8') as out:
    out.write('\n'.join(report))
print('\n'.join(report))
