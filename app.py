import os
import requests
import time
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Ključno: dopušta tvojoj stranici da primi podatke

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fleet.promet-split.hr/",
    "Accept": "application/json"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        # Novi API šalje listu unutar "data" polja ili direktno kao listu
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data if isinstance(data, list) else [])
    except Exception as e:
        print(f"Greška na serveru: {e}")
        return jsonify([]), 500

@app.route('/api/stops')
def get_stops():
    url = "https://api.promet-split.hr/Fleet/api/v1/stop"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data)
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
