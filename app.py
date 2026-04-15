import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/split')
def get_split_buses():
    url = "https://fleet.promet-split.hr/api/vehicles"
    try:
        # Uzimamo podatke direktno s izvora koji si tražio
        r = requests.get(url, timeout=10)
        data = r.json()
        
        output = []
        for bus in data:
            # Čitamo točno ono što stranica šalje
            output.append({
                "garageNumber": str(bus.get("label", "")),
                "name": str(bus.get("line_name", "N/A")),
                "latitude": bus.get("lat"),
                "longitude": bus.get("lon"),
                "destination": str(bus.get("direction_name", "N/A")),
                "speed": bus.get("speed", 0)
            })
        return jsonify({"vehicles": output})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
