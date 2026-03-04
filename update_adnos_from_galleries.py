#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import chrome_scraper as cs


def load_cars(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_cars(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_text(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def parse_int(value):
    if value is None:
        return None
    text = re.sub(r'[^0-9]', '', str(value))
    if not text:
        return None
    return int(text)


def extract_brand_model(scraped):
    brand = scraped.get('Marka', '')
    model = scraped.get('Model', '')
    series = scraped.get('Seri', '')
    if not model and series:
        model = series
    return brand, model


def match_score(car, scraped):
    v = car.get('vehicle', {})
    car_brand = normalize_text(v.get('brand'))
    car_model = normalize_text(v.get('model'))
    car_year = str(v.get('year', '')).strip()

    scr_brand, scr_model = extract_brand_model(scraped)
    scr_brand_n = normalize_text(scr_brand)
    scr_model_n = normalize_text(scr_model)
    scr_year = str(scraped.get('Yıl', '')).strip()

    if not scr_brand_n or not scr_model_n or not scr_year:
        return -1

    if car_brand != scr_brand_n:
        return -1

    if car_model != scr_model_n and car_model not in scr_model_n and scr_model_n not in car_model:
        return -1

    if car_year != scr_year:
        return -1

    score = 8

    car_km = parse_int(v.get('km'))
    scr_km = parse_int(scraped.get('KM') or scraped.get('Kilometre'))
    if car_km is not None and scr_km is not None:
        diff = abs(car_km - scr_km)
        if diff <= 5000:
            score += 2
        elif diff <= 20000:
            score += 1

    car_price = parse_int(car.get('price'))
    scr_price = parse_int(scraped.get('Fiyat'))
    if car_price is not None and scr_price is not None and scr_price > 0:
        ratio = abs(car_price - scr_price) / scr_price
        if ratio <= 0.05:
            score += 2
        elif ratio <= 0.10:
            score += 1

    return score


def build_gallery_list(cars_data):
    urls = set()
    for item in cars_data.get('vehicles', []):
        url = (item.get('seller') or {}).get('url')
        if url:
            urls.add(url)
    return sorted(urls)


def scrape_all_galleries(gallery_urls, pages):
    cs.start_chrome_debug()
    browser = cs.connect_to_chrome()
    if not browser:
        raise RuntimeError('Chrome debug connection failed')

    scraped = []
    for url in gallery_urls:
        try:
            data = cs.scrape_gallery(browser, url, pages)
            for row in data:
                row['__gallery_url'] = url
            scraped.extend(data)
        except Exception as exc:
            print(f'Galeri hatasi: {url} -> {exc}')

    return scraped


def update_adnos(cars_data, scraped):
    by_gallery = {}
    for row in scraped:
        gal_url = row.get('__gallery_url')
        if not gal_url:
            continue
        by_gallery.setdefault(gal_url, []).append(row)

    updates = {}
    for item in cars_data.get('vehicles', []):
        ad_no = str(item.get('adNo', ''))
        if not ad_no.startswith('194'):
            continue

        gal_url = (item.get('seller') or {}).get('url')
        candidates = by_gallery.get(gal_url, [])
        if not candidates:
            continue

        best = None
        best_score = -1
        for row in candidates:
            score = match_score(item, row)
            if score > best_score:
                best_score = score
                best = row

        if not best or best_score < 8:
            continue

        new_ad = str(best.get('ilan_no', '')).strip()
        new_url = str(best.get('url', '')).strip()
        if not new_ad or new_ad == ad_no:
            continue

        updates[ad_no] = {
            'new_ad': new_ad,
            'url': new_url,
        }

        item['adNo'] = new_ad
        item['id'] = new_ad
        if new_url:
            item['adUrl'] = new_url

    regions = cars_data.get('regions', {})
    for region, ad_list in regions.items():
        new_list = []
        for ad in ad_list:
            ad_str = str(ad)
            if ad_str in updates:
                new_list.append(updates[ad_str]['new_ad'])
            else:
                new_list.append(ad_str)
        regions[region] = new_list

    return updates


def main():
    parser = argparse.ArgumentParser(description='Update ad numbers from gallery pages')
    parser.add_argument('--cars', default='cars_data.json', help='Cars data JSON path')
    parser.add_argument('--pages', type=int, default=10, help='Pages per gallery')
    parser.add_argument('--dry-run', action='store_true', help='Do not write output')
    args = parser.parse_args()

    cars_path = Path(args.cars)
    cars_data = load_cars(cars_path)

    gallery_urls = build_gallery_list(cars_data)
    if not gallery_urls:
        print('No gallery URLs found in cars_data.json')
        return

    print(f'{len(gallery_urls)} galeri taranacak...')
    scraped = scrape_all_galleries(gallery_urls, args.pages)
    print(f'{len(scraped)} ilan cekildi')

    updates = update_adnos(cars_data, scraped)
    print(f'{len(updates)} ilan no guncellendi')
    for old, data in updates.items():
        print(f'{old} -> {data["new_ad"]}')

    if args.dry_run:
        print('Dry-run tamamlandi, dosya yazilmadi')
        return

    save_cars(cars_path, cars_data)
    print('cars_data.json guncellendi')


if __name__ == '__main__':
    main()
