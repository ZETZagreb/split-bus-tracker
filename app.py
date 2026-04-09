import os
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    # Dodajemo headers da izgledamo kao prava stranica s tvoje slike
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"vehicles": []})

# Ova ruta izvlači "Detalje putovanja" sa slike koju si poslao
@app.route('/api/fleet_details/<trip_id>')
def get_fleet_details(trip_id):
    url = f"https://www.bus-split.com/api/trip-details/{trip_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers)
        return jsonify(r.json())
    except:
        return jsonify({"stops": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
