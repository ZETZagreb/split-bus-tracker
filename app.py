import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = r.json()
        vehicles = data.get("vehicles", [])
        now = get_croatia_time()
        output = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            reg = bus.get("registrationNumber") or "N/A"
            marka = bus.get("modelName") or "N/A"
            lat = bus.get("latitude")
            lon = bus.get("longitude")

            if not gbr or not lat: continue

            v = {
                "garageNumber": gbr,
                "name": line,
                "registrationNumber": reg,
                "brand": marka,
                "latitude": lat,
                "longitude": lon
            }
            output.append(v)

            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr,
                    "line": line,
                    "reg": reg,
                    "brand": marka,
                    "date": now.strftime("%d.%m.%Y."),
                    "time": now.strftime("%H:%M"),
                    "lat": lat,
                    "lon": lon
                }).execute()
            except:
                pass

        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
