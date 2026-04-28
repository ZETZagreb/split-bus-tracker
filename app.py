import os
import requests
import time
import urllib3
from flask import Flask, render_template, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Session pamti kolačiće koji se generiraju tijekom negotiate poziva
s = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fleet.promet-split.hr/",
    "Origin": "https://fleet.promet-split.hr",
    "X-Requested-With": "XMLHttpRequest"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ts = int(time.time() * 1000)
    try:
        # 1. SignalR Negotiate (POST zahtjev)
        neg_url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles/negotiate?negotiateVersion=1&t={ts}"
        s.post(neg_url, headers=HEADERS, verify=False, timeout=10)
        
        # 2. Inicijalizacija sesije
        s.get(f"https://api.promet-split.hr/Fleet/api/v1/session?t={ts}", headers=HEADERS, verify=False, timeout=10)
        
        # 3. Finalni dohvat vozila
        veh_url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
        r = s.get(veh_url, headers=HEADERS, verify=False, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            return jsonify(data['data'] if isinstance(data, dict) and 'data' in data else data)
        
        return jsonify([]), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
