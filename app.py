import os
import requests
import time
import urllib3
from flask import Flask, render_template, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Koristimo Session objekt da bi zadržali kolačiće (cookies)
session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://fleet.promet-split.hr",
    "Referer": "https://fleet.promet-split.hr/",
    "Connection": "keep-alive"
}

def ensure_session():
    """Simulira inicijalni poziv sesije koji vidimo na slici"""
    try:
        ts = int(time.time() * 1000)
        # Pozivamo session endpoint koji se vidi na slici image_30f7d1.png
        session.get(f"https://api.promet-split.hr/Fleet/api/v1/session?t={ts}", 
                    headers=HEADERS, verify=False, timeout=10)
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    ensure_session() # Osvježavamo sesiju prije svakog poziva
    
    ts = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={ts}"
    
    try:
        r = session.get(url, headers=HEADERS, timeout=15, verify=False)
        
        # Ako je i dalje 401, probali smo sve s ove strane
        if r.status_code == 401:
            return jsonify({"error": "Unauthorized"}), 401
            
        data = r.json()
        if isinstance(data, dict) and 'data' in data:
            return jsonify(data['data'])
        return jsonify(data if isinstance(data, list) else [])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
