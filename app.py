import csv
import time
import threading
import subprocess
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'dataset_laptop_lengkap.csv')

IS_SCRAPING = False

def load_data():
    laptops = []
    with open(DATA_PATH, mode='r', encoding='utf-8') as file:
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

def get_form_options():
    try:
        laptops = load_data()
    except FileNotFoundError:
        return {"min_price": 0, "rams": [], "ssds": [], "cpus": []}
        
    min_price = min((laptop['harga'] for laptop in laptops), default=0)
    rams = sorted(list(set(laptop['ram'] for laptop in laptops)))
    ssds = sorted(list(set(laptop['ssd'] for laptop in laptops)))
    
    cpu_keywords = ["Core i3", "Core i5", "Core i7", "Core i9", "Core Ultra 5", "Core Ultra 7", "Ryzen 3", "Ryzen 5", "Ryzen 7", "Ryzen 9", "Celeron", "Snapdragon", "Athlon"]
    found_cpus = set()
    for laptop in laptops:
        for kw in cpu_keywords:
            if kw.lower() in laptop['cpu'].lower():
                found_cpus.add(kw)
    cpus = sorted(list(found_cpus))
    
    return {"min_price": min_price, "rams": rams, "ssds": ssds, "cpus": cpus}

def run_dp(budget, selected_rams, selected_ssds, selected_cpus):
    laptops = load_data()
    UNIT = 100_000
    W = budget // UNIT
    
    dp = [0.0] * (W + 1)
    dp_pilih = [None] * (W + 1)
    
    start_time = time.perf_counter()
    
    for laptop in laptops:
        if selected_rams and laptop['ram'] not in selected_rams:
            continue
        if selected_ssds and laptop['ssd'] not in selected_ssds:
            continue
        if selected_cpus:
            if not any(cpu_kw.lower() in laptop['cpu'].lower() for cpu_kw in selected_cpus):
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

def run_greedy(budget, selected_rams, selected_ssds, selected_cpus):
    laptops = load_data()
    laptop_layak = []
    
    start_time = time.perf_counter()
    
    for laptop in laptops:
        if laptop['harga'] > budget:
            continue
        if selected_rams and laptop['ram'] not in selected_rams:
            continue
        if selected_ssds and laptop['ssd'] not in selected_ssds:
            continue
        if selected_cpus:
            if not any(cpu_kw.lower() in laptop['cpu'].lower() for cpu_kw in selected_cpus):
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
    options = get_form_options()
    return render_template('index.html', options=options)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    budget = int(data.get('budget', 0))
    selected_rams = [int(r) for r in data.get('rams', [])]
    selected_ssds = [int(s) for s in data.get('ssds', [])]
    selected_cpus = data.get('cpus', [])
    
    res_dp = run_dp(budget, selected_rams, selected_ssds, selected_cpus)
    res_greedy = run_greedy(budget, selected_rams, selected_ssds, selected_cpus)
    
    return jsonify({
        'dp': res_dp,
        'greedy': res_greedy
    })

def run_scraper_bg():
    global IS_SCRAPING
    IS_SCRAPING = True
    try:
        scraper_path = os.path.join(BASE_DIR, 'scraper.py')
        subprocess.run(['python', scraper_path])
    finally:
        IS_SCRAPING = False

@app.route('/data')
def data():
    try:
        laptops = load_data()
    except FileNotFoundError:
        laptops = []
    return render_template('data.html', laptops=laptops)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    global IS_SCRAPING
    if IS_SCRAPING:
        return jsonify({"message": "Proses scraping sedang berjalan."}), 400
        
    thread = threading.Thread(target=run_scraper_bg)
    thread.start()
    return jsonify({"message": "Proses scraping dimulai. Silakan tunggu sekitar 5-10 menit. Anda bisa melakukan aktivitas lain."})

@app.route('/scrape-status', methods=['GET'])
def scrape_status():
    return jsonify({"is_scraping": IS_SCRAPING})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
