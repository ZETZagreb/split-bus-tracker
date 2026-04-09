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

# Ova ruta sada traži stanice za BILO KOJU liniju (ID) koju klikneš
@app.route('/api/route_details/<line_id>')
def get_route_details(line_id):
    url = f"https://www.bus-split.com/api/route-stops/{line_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"stops": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
