import os
import requests
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://fleet.promet-split.hr/"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"error": "Offline"}), 500

@app.route('/api/stops')
def get_stops():
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/stop?t={ts}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"error": "Offline"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
