import os
import requests
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fleet.promet-split.hr/"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ts = int(time.time() * 1000)
    url_v1 = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    url_old = f"https://fleet.promet-split.hr/api/get-positions?t={ts}"
    
    try:
        r = requests.get(url_v1, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('data') or (isinstance(data, list) and len(data) > 0):
                return jsonify(data)
        
        r = requests.get(url_old, headers=HEADERS, timeout=5)
        return jsonify(r.json())
    except:
        try:
            r = requests.get(url_old, headers=HEADERS, timeout=5)
            return jsonify(r.json())
        except:
            return jsonify({"error": "Offline"}), 500

@app.route('/api/stops')
def get_stops():
    url = "https://fleet.promet-split.hr/api/get-stops"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        return jsonify(r.json())
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
