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
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"vehicles": []})

# NOVA RUTA: Dohvaća stanice za određenu liniju s bus-split.com
@app.route('/api/stops/<line_id>')
def get_stops(line_id):
    # Pokušavamo dohvatiti detalje rute (ovo je standardni endpoint za bus-split)
    url = f"https://www.bus-split.com/api/lines/{line_id}/stops"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        return jsonify(r.json())
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
