import os
import requests
import time
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
        data = r.json()
        # Izvlačenje liste iz "data" objekta ako postoji
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/stops')
def get_stops():
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/stop?t={ts}"
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
