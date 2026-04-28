import os
import requests
import time
import urllib3
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Isključivanje upozorenja za SSL certifikate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Headeri koji simuliraju službeni preglednik s tvoje slike
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://fleet.promet-split.hr",
    "Referer": "https://fleet.promet-split.hr/"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ts = int(time.time())
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    try:
        # verify=False rješava potencijalni SSL Error 500
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        
        if r.status_code != 200:
            return jsonify([]), r.status_code
            
        data = r.json()
        # Izdvajanje liste iz "data" omotača
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data if isinstance(data, list) else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stops')
def get_stops():
    url = "https://api.promet-split.hr/Fleet/api/v1/stop"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        data = r.json()
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data)
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
