import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import time

app = Flask(__name__)

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/split')
def get_split_buses():
    # Ovo je direktni izvor podataka koji koristi njihova stranica
    url = "https://fleet.promet-split.hr/api/vehicles"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        output = []
        for bus in data:
            gbr = str(bus.get("label", ""))
            line = str(bus.get("line_name", "N/A"))
            lat = bus.get("lat")
            lon = bus.get("lon")
            # Točan smjer i polazak direktno iz izvora
            direction = str(bus.get("direction_name", "N/A"))
            
            if not gbr or lat is None: continue

            output.append({
                "garageNumber": gbr,
                "name": line,
                "latitude": lat,
                "longitude": lon,
                "destination": direction, # Polazak/Smjer
                "speed": bus.get("speed", 0)
            })

        return jsonify({"vehicles": output})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
