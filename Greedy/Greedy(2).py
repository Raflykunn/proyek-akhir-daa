import csv

# 1. Meminta Input dari User lewat Terminal
print("=== INPUT KRITERIA LAPTOP ===")
BUDGET = int(input("Masukkan budget maksimal Anda (Rupiah, misal 10000000): "))
MIN_RAM = int(input("Masukkan minimal RAM yang dibutuhkan (GB, misal 8): "))
MIN_SSD = int(input("Masukkan minimal Storage/SSD yang dibutuhkan (GB, misal 512): "))
print("-" * 40)

laptop_layak = []

# 2. Membaca data dari file CSV
with open('dataset_laptop_lengkap.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        # Konversi data teks dari CSV ke angka agar bisa dicek
        harga = int(row['Harga_Rp'])
        ram = int(row['RAM_GB'])
        ssd = int(row['SSD_GB'])
        skor_utilitas = float(row['Skor_Utilitas'])
        
        # 3. FILTERING: Cek apakah memenuhi syarat budget & spesifikasi
        if harga <= BUDGET and ram >= MIN_RAM and ssd >= MIN_SSD:
            
            # STRATEGI GREEDY: Hitung nilai keuntungan (Skor / Harga)
            density = skor_utilitas / harga
            
            # Simpan data laptop yang lolos seleksi ke dalam list
            laptop_layak.append({
                'nama': row['Nama_Laptop'],
                'harga': harga,
                'cpu': row['CPU'],
                'ram': ram,
                'ssd': ssd,
                'skor': skor_utilitas,
                'density': density
            })

# 4. SELEKSI GREEDY: Cari yang nilai Density-nya paling tinggi
if laptop_layak:
    # Urutkan list berdasarkan density dari yang terbesar ke terkecil
    laptop_layak.sort(key=lambda x: x['density'], reverse=True)
    
    # Elemen pertama (indeks 0) otomatis adalah laptop terbaik versi Greedy
    rekomendasi = laptop_layak[0]
    
    # 5. Tampilkan Hasil
    print("\n=== REKOMENDASI LAPTOP PALING OPTIMAL (GREEDY) ===")
    print(f"Nama Laptop   : {rekomendasi['nama']}")
    print(f"Harga         : Rp {rekomendasi['harga']:,}")
    print(f"Spesifikasi   : CPU -> {rekomendasi['cpu']}")
    print(f"                RAM -> {rekomendasi['ram']} GB")
    print(f"                SSD -> {rekomendasi['ssd']} GB")
    print(f"Skor Utilitas : {rekomendasi['skor']} Poin")
else:
    print("\n[Hasil] Maaf, tidak ada laptop yang memenuhi kriteria budget dan spesifikasi Anda.")