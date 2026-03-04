import os
import time
import subprocess

def run_merge_script():
    # merge_and_backup_all_vehicles.py dosyasını çalıştır
    result = subprocess.run([
        os.sys.executable, 'merge_and_backup_all_vehicles.py'
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

def main():
    while True:
        run_merge_script()
        print("Otomatik yedekleme ve birleştirme tamamlandı. 24 saat sonra tekrar çalışacak.")
        time.sleep(24 * 60 * 60)  # 24 saat bekle

if __name__ == '__main__':
    main()
