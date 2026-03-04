import json

path = 'analysis_dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "const brand = (vehicle?.vehicle?.brand || 'Bilinmiyor').trim();",
    "const brand = String(vehicle?.vehicle?.brand || vehicle?.Marka || 'Bilinmiyor').trim();"
)

text = text.replace(
    "const pkg = (vehicle?.vehicle?.package || '-').trim() || '-';",
    "const pkg = String(vehicle?.vehicle?.package || vehicle?.Paket || '-').trim() || '-';"
)

text = text.replace(
    "const year = Number(vehicle?.vehicle?.year) || '-';",
    "const year = Number(vehicle?.vehicle?.year || vehicle?.['Yıl']) || '-';"
)

price_old = """        function getPrice(vehicle) {
            const directNumeric = Number(vehicle?.price);
            if (Number.isFinite(directNumeric) && directNumeric > 0) return directNumeric;

            const amountNumeric = Number(vehicle?.price?.amount);
            if (Number.isFinite(amountNumeric) && amountNumeric > 0) return amountNumeric;

            const nestedNumeric = Number(vehicle?.vehicle?.price);
            if (Number.isFinite(nestedNumeric) && nestedNumeric > 0) return nestedNumeric;

            const raw = String(vehicle?.price ?? vehicle?.price?.amount ?? vehicle?.vehicle?.price ?? '').trim();
            if (raw) {
                const normalized = Number(raw.replace(/[^\\d]/g, ''));
                if (Number.isFinite(normalized) && normalized > 0) return normalized;
            }

            return 0;
        }"""

price_new = """        function getPrice(vehicle) {
            const keysToTry = ['price', 'Fiyat'];
            for (const key of keysToTry) {
                const val = vehicle?.[key] || (vehicle?.vehicle && vehicle.vehicle[key]);
                if (!val) continue;

                if (typeof val === 'number') return val;
                
                if (typeof val === 'object' && val.amount) {
                    return Number(val.amount);
                }

                if (typeof val === 'string') {
                    const normalized = Number(val.replace(/[^\\d]/g, ''));
                    if (Number.isFinite(normalized) && normalized > 0) return normalized;
                }
            }
            return 0;
        }"""

text = text.replace(price_old, price_new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch applied to analysis_dashboard.html")
