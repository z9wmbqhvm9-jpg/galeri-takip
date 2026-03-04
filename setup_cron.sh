#!/bin/bash
# Cron job kurulum scripti - Her 3 saatte otomatik kontrol

SCRIPT_PATH="/Volumes/AS1000_Plus/galeri/galeri.py"
LOG_PATH="/Volumes/AS1000_Plus/galeri/cron.log"

# Mevcut crontab'ı al, galeri ile ilgili satırları sil, yenisini ekle
(crontab -l 2>/dev/null | grep -v "galeri.py"; echo "0 */3 * * * /usr/bin/python3 $SCRIPT_PATH kontrol >> $LOG_PATH 2>&1") | crontab -

echo "✅ Cron job kuruldu!"
echo "📅 Her 3 saatte bir kontrol yapılacak (00:00, 03:00, 06:00, ...)"
echo "📝 Log dosyası: $LOG_PATH"
echo ""
echo "Cron job'u kaldırmak için:"
echo "  crontab -e  # ve galeri.py satırını silin"
