import os
import requests
import time
import urllib3
from flask import Flask, render_template, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

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
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    try:
        # Čisti GET zahtjev koji je najčešće vraćao podatke
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        
        if r.status_code == 200:
            data = r.json()
            # Vraćamo listu vozila (unutar 'data' polja ili direktno)
            if isinstance(data, dict) and 'data' in data:
                return jsonify(data['data'])
            return jsonify(data if isinstance(data, list) else [])
            
        return jsonify([]), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
