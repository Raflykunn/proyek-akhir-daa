# Sistem Rekomendasi Laptop (Proyek DAA)

Sistem rekomendasi laptop ini adalah proyek mata kuliah Desain dan Analisis Algoritma (DAA). Proyek ini bertujuan untuk membandingkan performa pencarian rekomendasi laptop yang paling optimal berdasarkan budget dan spesifikasi minimum (RAM, SSD, CPU) menggunakan algoritma **Dynamic Programming (0/1 Knapsack)** dan **Greedy**. 

Data spesifikasi laptop dikumpulkan melalui teknik web scraping dan disimpan di dalam file CSV, kemudian dianalisis menggunakan kedua algoritma di atas untuk menampilkan hasil rekomendasi terbaik beserta perbandingan waktu eksekusinya.

## Fitur Utama

- **Web Scraping Laptop**: Mengambil data spesifikasi dan harga laptop terkini (menggunakan `scraper.py`).
- **Dynamic Programming (0/1 Knapsack)**: Mencari laptop optimal dengan mengevaluasi semua kemungkinan untuk budget yang diberikan (solusi optimal terjamin).
- **Greedy Approach**: Mencari laptop optimal berdasarkan perbandingan nilai skor utilitas tertinggi untuk menemukan solusi terbaik dengan cepat.
- **Antarmuka Web**: Dilengkapi dengan UI berbasis Flask untuk memudahkan pengguna memasukkan kriteria dan melihat perbandingan performa.
- **Versi CLI**: Algoritma juga dapat dijalankan langsung secara interaktif melalui terminal.

## Struktur Direktori

- `app.py`: File utama aplikasi web (Flask) yang menyediakan antarmuka dan REST API lokal.
- `scraper.py`: Script Python untuk melakukan proses web scraping katalog laptop online.
- `dataset_laptop.csv` & `dataset_laptop_lengkap.csv`: File dataset berisi nama laptop, harga, spesifikasi detail, dan hasil perhitungan skor utilitas.
- `DP/implementasi_dp.py`: Kode implementasi interaktif algoritma Dynamic Programming di terminal (CLI).
- `Greedy/implementasi_greedy.py`: Kode implementasi interaktif algoritma Greedy di terminal (CLI).
- `templates/`: Berisi file HTML antarmuka pengguna web.

## Instalasi dan Panduan Penggunaan

### 1. Persiapan
Pastikan **Python 3.8+** sudah terinstal di komputer Anda.

### 2. Install Dependensi
Buka terminal/command prompt dan jalankan perintah berikut di direktori proyek:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi Web (Flask)
Untuk menjalankan antarmuka web yang interaktif:
```bash
python app.py
```
Setelah server berjalan, buka web browser dan kunjungi `http://127.0.0.1:5000`.

### 4. Menjalankan Algoritma via CLI (Terminal)
Jika Anda ingin menjalankan algoritma tanpa web interface:
- Untuk **Dynamic Programming**:
  ```bash
  python DP/implementasi_dp.py
  ```
- Untuk **Greedy**:
  ```bash
  python Greedy/implementasi_greedy.py
  ```

### 5. Memperbarui Dataset (Opsional)
Jika Anda ingin melakukan proses web scraping ulang untuk mendapatkan data dan harga laptop terbaru, Anda dapat menjalankan script scraper. Pastikan Anda memiliki koneksi internet yang stabil:
```bash
python scraper.py
```
*Catatan: Proses scraping dapat memakan waktu beberapa menit karena ada jeda request untuk mencegah server blocking.*
