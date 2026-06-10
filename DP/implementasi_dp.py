import csv

# 1. Input dari User
print("=== INPUT KRITERIA LAPTOP ===")
BUDGET   = int(input("Masukkan budget maksimal (Rupiah, misal 10000000): "))
MIN_RAM  = int(input("Masukkan minimal RAM (GB, misal 8): "))
MIN_SSD  = int(input("Masukkan minimal SSD (GB, misal 512): "))
CARI_CPU = input("Cari keyword CPU (opsional, lewati dengan Enter, misal 'i5' atau 'Ryzen 5'): ").lower()
print("-" * 40)

# 2. Baca dataset
semua_laptop = []
with open('dataset_laptop_lengkap.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        semua_laptop.append({
            'nama'  : row['Nama_Laptop'],
            'harga' : int(row['Harga_Rp']),
            'cpu'   : row['CPU'],
            'ram'   : int(row['RAM_GB']),
            'ssd'   : int(row['SSD_GB']),
            'skor'  : float(row['Skor_Utilitas'])
        })

# 3. DYNAMIC PROGRAMMING — 0/1 Knapsack
# Setiap laptop = 1 item, bobot = harga, nilai = skor utilitas
# dp[b] = skor utilitas tertinggi yang bisa dicapai dengan budget b
# Granularitas: 1 unit = 100.000 Rupiah agar tabel tidak terlalu besar

UNIT = 100_000
W    = BUDGET // UNIT          # kapasitas knapsack dalam satuan unit

# Inisialisasi tabel DP
dp       = [0.0]  * (W + 1)   # dp[b] = skor terbaik untuk budget b unit
dp_pilih = [None] * (W + 1)   # laptop yang dipilih untuk tiap kapasitas b

for laptop in semua_laptop:
    # Filter spesifikasi minimum sebelum masuk DP
    if laptop['ram'] < MIN_RAM or laptop['ssd'] < MIN_SSD:
        continue
        
    if CARI_CPU and CARI_CPU not in laptop['cpu'].lower():
        continue

    bobot = laptop['harga'] // UNIT   # bobot laptop dalam satuan unit
    nilai = laptop['skor']            # nilai = skor utilitas

    # Iterasi untuk DP 1 Barang (karena user hanya butuh 1 laptop)
    # Membandingkan apakah skor laptop ini lebih baik dari yang sudah ada di budget b
    for b in range(W, bobot - 1, -1):
        if nilai > dp[b]:
            dp[b]       = nilai
            dp_pilih[b] = laptop

# 4. Ambil hasil: laptop terpilih pada kapasitas penuh (W)
rekomendasi = dp_pilih[W]

# 5. Tampilkan Hasil
print("\n=== REKOMENDASI LAPTOP TERBAIK SESUAI BUDGET (DYNAMIC PROGRAMMING) ===")
if rekomendasi:
    print(f"Nama Laptop   : {rekomendasi['nama']}")
    print(f"Harga         : Rp {rekomendasi['harga']:,}")
    print(f"Sisa Budget   : Rp {BUDGET - rekomendasi['harga']:,}")
    print(f"Spesifikasi   : CPU -> {rekomendasi['cpu']}")
    print(f"                RAM -> {rekomendasi['ram']} GB")
    print(f"                SSD -> {rekomendasi['ssd']} GB")
    print(f"Skor Utilitas : {rekomendasi['skor']} Poin")
else:
    print("[Hasil] Maaf, tidak ada laptop yang memenuhi kriteria Anda.")
