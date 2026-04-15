import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import time

app = Flask(__name__)

# Supabase login
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

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    url = "https://cloud.it-sistemi.com/AutotrolejS3/api/v1/vehicle-positions"
    try:
        r = requests.get(url, timeout=10)
        vehicles = r.json().get("data", [])
        now = get_croatia_time()
        current_ts = time.time()
        
        output = []
        for bus in vehicles:
            gbr = str(bus.get("vehicleNumber", ""))
            line = str(bus.get("lineName", "N/A"))
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            reg = bus.get("licensePlate", "N/A")
            dest = bus.get("destinationName", "N/A")

            if not gbr or lat is None: continue
            
            output.append({"garageNumber": gbr, "name": line, "latitude": lat, "longitude": lon})

            # Zapiši svakih 15 min ili kod promjene linije
            if gbr not in last_saved or (current_ts - last_saved[gbr]['ts'] >= 900) or (last_saved[gbr]['line'] != line):
                try:
                    # Šaljemo točno ono što tvoja baza sada ima + nove stupce
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr,
                        "line": line,
                        "reg": reg,
                        "lat": lat,
                        "lon": lon,
                        "city": "Rijeka",
                        "date": now.strftime("%Y-%m-%d"),
                        "time": now.strftime("%H:%M:%S"),
                        "direction": dest # Spremit ćemo odredište u tvoj 'direction' stupac
                    }).execute()
                    
                    last_saved[gbr] = {"ts": current_ts, "line": line}
                except Exception as e:
                    print(f"Baza odbila: {e}")

        return jsonify({"vehicles": output})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

@app.route('/api/logs')
def get_logs_data():
    try:
        res = supabase.table("bus_logs").select("*").eq("city", "Rijeka").order("id", desc=True).limit(200).execute()
        return jsonify(res.data)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
