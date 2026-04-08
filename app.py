import os
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    try:
        r = requests.get("https://www.bus-split.com/api/vehicles/live", timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"vehicles": []})

@app.route('/api/routes')
def get_routes():
    try:
        # Ovo je file koji smo vidjeli u F12 Networku
        r = requests.get("https://www.bus-split.com/api/routes.json", timeout=10)
        return jsonify(r.json())
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
