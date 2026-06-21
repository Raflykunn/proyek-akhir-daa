import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import sys
import io

# Konfigurasi UTF-8 untuk Windows console agar terhindar dari UnicodeEncodeError
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET_COUNT = 240
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# Kata kunci untuk menyaring aksesoris, komponen PC, tablet, dll.
IGNORE_KEYWORDS = [
    "adapter", "adaptor", "tas ", "sleeve", "mouse", "keyboard", "charger", "kabel", "power bank", 
    "backpack", "universal", "tinta", "cartridge", "headset", "headphone", "earphone", "proyektor", 
    "projector", "ram memory", "ssd storage", "flashdisk", "vga", "sodimm", "kingston", "fury impact", 
    "crucial", "corsair", "lexar", "adata", "samsung 9", "gigabyte vga", "msi vga", "asus vga", 
    "rog ally", "lenovo legion go", "nintendo", "playstation", "xbox", "gamepad", "joystick", 
    "tablet", "tab ", "ipad", "monitor", "display", "screen"
]

def clean_name(title):
    m = re.search(r'\b(Intel|AMD|Ryzen|Core|Celeron|Pentium|Athlon|N100|N150|N200|N300|N305|N355|Ultra)\b', title, re.I)
    name = title[:m.start()].strip() if m else " ".join(title.split()[:5])
    return re.sub(r'[\s\-\–\—\[\(\{]+$', '', name).strip()

def clean_price(price_str):
    price_str = price_str.replace('–', '-').replace('—', '-')
    first_price = price_str.split('-')[0] if '-' in price_str else price_str
    digits = re.sub(r'\D', '', re.sub(r'\.00\b', '', first_price))
    return int(digits) if digits else 0

def estimate_battery(battery_str, title):
    m_hours = re.search(r'(\d+(?:\.\d+)?)\s*(?:jam|hour|hr|s\b)', battery_str, re.I)
    if m_hours:
        return float(m_hours.group(1))
    
    m_wh = re.search(r'(\d+)\s*(?:Wh|wh)', battery_str)
    wh = float(m_wh.group(1)) if m_wh else None
    
    t_low = title.lower()
    is_gaming = any(x in t_low for x in ["rtx", "gtx", "gaming", "rog", "tuf", "loq", "legion", "victus", "nitro"]) or re.search(r'\b\d{4}h[sx]?\b', t_low)
    
    if wh:
        if is_gaming:
            return 4.5 if wh <= 50 else 6.5 if wh <= 75 else 8.5
        return 5.5 if wh <= 40 else 7.5 if wh <= 55 else 9.5
    return 5.0 if is_gaming else 7.0

def main():
    print("=== PROGRAM LAPTOP SCRAPER & UTILITY CALCULATOR (ELS.id) ===")
    session = requests.Session()
    session.headers.update(HEADERS)
    
    product_links = []
    page = 1
    
    print("\n[1] Mengumpulkan link produk dari katalog...")
    while len(product_links) < TARGET_COUNT + 40:
        url = "https://els.id/product-category/laptop/" if page == 1 else f"https://els.id/product-category/laptop/page/{page}/"
        try:
            res = session.get(url, timeout=10)
            if res.status_code != 200:
                break
            
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.find_all(class_="product-wrapper")
            if not cards:
                break
                
            for card in cards:
                title_el = card.find(class_="product-title")
                price_el = card.find(class_="price")
                if title_el and price_el:
                    link_el = title_el.find("a")
                    if link_el:
                        raw_title = link_el.get_text(strip=True)
                        
                        # Filter aksesoris & komponen berdasarkan judul
                        if any(x in raw_title.lower() for x in IGNORE_KEYWORDS):
                            continue
                            
                        # Dapatkan harga dan filter laptop murah (aksesoris)
                        ins_el = price_el.find("ins")
                        harga_rp = clean_price(ins_el.get_text(strip=True) if ins_el else price_el.get_text(strip=True))
                        if harga_rp < 3000000:
                            continue
                            
                        product_links.append({"title": raw_title, "price": harga_rp, "url": link_el.get("href")})
            
            page += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Error katalog halaman {page}: {e}")
            break
            
    print(f"\n[2] Berhasil mengumpulkan {len(product_links)} link laptop. Mulai mengunduh spesifikasi detail...")
    scraped_data = []
    
    for idx, item in enumerate(product_links):
        if len(scraped_data) >= TARGET_COUNT:
            break
            
        try:
            time.sleep(1.0)
            res = session.get(item["url"], timeout=10)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            desc_panel = soup.find(id="tab-description") or soup.find(class_=re.compile("description", re.I))
            if not desc_panel:
                continue
                
            specs = {"processor": "", "memory": "", "storage": "", "battery": ""}
            for line in desc_panel.get_text().split("\n"):
                line = line.strip()
                if ":" in line:
                    k, v = [x.strip() for x in line.split(":", 1)]
                    k_low = k.lower()
                    if any(x in k_low for x in ["processor", "prosesor", "cpu"]): specs["processor"] = v
                    elif any(x in k_low for x in ["memory", "ram"]): specs["memory"] = v
                    elif any(x in k_low for x in ["storage", "ssd", "hdd"]): specs["storage"] = v
                    elif any(x in k_low for x in ["battery", "baterry", "baterai"]): specs["battery"] = v
            
            # Fallback jika data kosong di deskripsi detail
            if not specs["processor"]:
                m = re.search(r'\b(i[3579]|Ryzen\s+[3579]|Ultra\s+[579]|Celeron|Pentium|N100|N150|N200)\b.*?(?=\s+\d+GB)', item["title"], re.I)
                specs["processor"] = m.group(0) if m else "Intel Core i3"
            
            # Parsing angka spesifikasi
            ram_gb = int(re.search(r'(\d+)\s*GB', specs["memory"], re.I).group(1)) if re.search(r'(\d+)\s*GB', specs["memory"], re.I) else 8
            
            m_tb = re.search(r'(\d+)\s*TB', specs["storage"], re.I)
            m_gb = re.search(r'(\d+)\s*GB', specs["storage"], re.I)
            ssd_gb = int(m_tb.group(1)) * 1000 if m_tb else int(m_gb.group(1)) if m_gb else 512
            
            baterai_jam = estimate_battery(specs["battery"], item["title"])
            
            # Konversi ke skor
            cpu_low = specs["processor"].lower()
            skor_cpu = 100 if any(x in cpu_low for x in ["i7", "ryzen 7", "ultra 7", "core 7", "i9", "ryzen 9", "ultra 9"]) else 80 if any(x in cpu_low for x in ["i5", "ryzen 5", "ultra 5", "core 5"]) else 60
            skor_ram = 40 if ram_gb <= 4 else 70 if ram_gb <= 8 else 80 if ram_gb <= 12 else 90 if ram_gb <= 16 else 95 if ram_gb <= 24 else 100
            skor_ssd = 40 if ssd_gb <= 128 else 60 if ssd_gb <= 256 else 80 if ssd_gb <= 512 else 100
            skor_baterai = 60 if baterai_jam < 6 else 80 if baterai_jam <= 8 else 100
            
            # Hitung Skor Utilitas
            skor_utilitas = round((0.4 * skor_cpu) + (0.3 * skor_ram) + (0.2 * skor_ssd) + (0.1 * skor_baterai), 2)
            
            nama_laptop = clean_name(item["title"])
            scraped_data.append({
                "Nama_Laptop": nama_laptop,
                "Harga_Rp": item["price"],
                "CPU": specs["processor"],
                "RAM_GB": ram_gb,
                "SSD_GB": ssd_gb,
                "Baterai_Jam": baterai_jam,
                "Skor_CPU": skor_cpu,
                "Skor_RAM": skor_ram,
                "Skor_SSD": skor_ssd,
                "Skor_Baterai": skor_baterai,
                "Skor_Utilitas": skor_utilitas
            })
            
            print(f"  -> Sukses [{len(scraped_data)}/{TARGET_COUNT}]: {nama_laptop.encode('ascii', errors='replace').decode('ascii')} | Rp{item['price']:,} | Utilitas: {skor_utilitas}")
        except Exception as e:
            continue
            
    # Langkah 3: Ekspor data ke CSV
    print("\n[3] Mengekspor hasil scraping...")
    df = pd.DataFrame(scraped_data).head(TARGET_COUNT)
    df.insert(0, "ID", range(1, len(df) + 1))
    
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    csv_path_1 = os.path.join(BASE_DIR, "dataset_laptop.csv")
    csv_path_2 = os.path.join(BASE_DIR, "dataset_laptop_lengkap.csv")
    
    df[["ID", "Nama_Laptop", "Harga_Rp", "Skor_Utilitas"]].to_csv(csv_path_1, index=False, encoding="utf-8")
    df.to_csv(csv_path_2, index=False, encoding="utf-8")
    print("Selesai! File 'dataset_laptop.csv' dan 'dataset_laptop_lengkap.csv' berhasil diperbarui.")

if __name__ == "__main__":
    main()
