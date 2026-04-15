import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import time

app = Flask(__name__)

# Supabase
SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

last_saved = {}

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

@app.route('/api/buses/split')
def get_split_buses():
    url = "https://fleet.promet-split.hr/api/vehicles"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        now = get_croatia_time()
        current_ts = time.time()
        output = []

        for bus in data:
            gbr = str(bus.get("label", ""))
            line = str(bus.get("line_name", "N/A"))
            direction = str(bus.get("direction_name", "N/A"))
            lat = bus.get("lat")
            lon = bus.get("lon")
            
            if not gbr or not lat: continue

            output.append({
                "garageNumber": gbr,
                "name": line,
                "latitude": lat,
                "longitude": lon,
                "destination": direction,
                "speed": bus.get("speed", 0)
            })

            # Spremanje u bazu (15 min ili promjena smjera)
            bus_id = f"ST_{gbr}"
            state = last_saved.get(bus_id, {"ts": 0, "direction": ""})
            if (current_ts - state['ts'] >= 900) or (state['direction'] != direction):
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr,
                        "line": line,
                        "direction": direction,
                        "reg": bus.get("plate", "N/A"),
                        "lat": lat,
                        "lon": lon,
                        "city": "Split",
                        "date": now.strftime("%Y-%m-%d"),
                        "time": now.strftime("%H:%M:%S")
                    }).execute()
                    last_saved[bus_id] = {"ts": current_ts, "direction": direction}
                except: pass
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

@app.route('/api/logs')
def get_logs_data():
    try:
        res = supabase.table("bus_logs").select("*").eq("city", "Split").order("id", desc=True).limit(200).execute()
        return jsonify(res.data)
    except: return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
