import csv
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def load_data():
    laptops = []
    with open('dataset_laptop_lengkap.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            laptops.append({
                'nama': row['Nama_Laptop'],
                'harga': int(row['Harga_Rp']),
                'cpu': row['CPU'],
                'ram': int(row['RAM_GB']),
                'ssd': int(row['SSD_GB']),
                'skor': float(row['Skor_Utilitas'])
            })
    return laptops

def run_dp(budget, min_ram, min_ssd, cari_cpu):
    laptops = load_data()
    UNIT = 100_000
    W = budget // UNIT
    
    dp = [0.0] * (W + 1)
    dp_pilih = [None] * (W + 1)
    
    start_time = time.perf_counter()
    
    for laptop in laptops:
        if laptop['ram'] < min_ram or laptop['ssd'] < min_ssd:
            continue
        if cari_cpu and cari_cpu not in laptop['cpu'].lower():
            continue
            
        bobot = laptop['harga'] // UNIT
        nilai = laptop['skor']
        
        # DP Iterasi (1 Barang Knapsack)
        for b in range(W, bobot - 1, -1):
            if nilai > dp[b]:
                dp[b] = nilai
                dp_pilih[b] = laptop
                
    rekomendasi = dp_pilih[W]
    end_time = time.perf_counter()
    
    return {
        'rekomendasi': rekomendasi,
        'waktu_eksekusi': (end_time - start_time) * 1000 # in ms
    }

def run_greedy(budget, min_ram, min_ssd, cari_cpu):
    laptops = load_data()
    laptop_layak = []
    
    start_time = time.perf_counter()
    
    for laptop in laptops:
        if laptop['harga'] <= budget and laptop['ram'] >= min_ram and laptop['ssd'] >= min_ssd:
            if cari_cpu and cari_cpu not in laptop['cpu'].lower():
                continue
            laptop_layak.append(laptop)
            
    rekomendasi = None
    if laptop_layak:
        # Sortir berdasarkan skor untuk mencari nilai optimal lokal/global
        laptop_layak.sort(key=lambda x: x['skor'], reverse=True)
        rekomendasi = laptop_layak[0]
        
    end_time = time.perf_counter()
    
    return {
        'rekomendasi': rekomendasi,
        'waktu_eksekusi': (end_time - start_time) * 1000 # in ms
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    budget = int(data.get('budget', 0))
    min_ram = int(data.get('min_ram', 0))
    min_ssd = int(data.get('min_ssd', 0))
    cari_cpu = data.get('cari_cpu', '').lower()
    
    res_dp = run_dp(budget, min_ram, min_ssd, cari_cpu)
    res_greedy = run_greedy(budget, min_ram, min_ssd, cari_cpu)
    
    return jsonify({
        'dp': res_dp,
        'greedy': res_greedy
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
