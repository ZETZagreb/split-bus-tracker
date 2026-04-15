import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import time

app = Flask(__name__)

# --- KONFIGURACIJA ---
SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Memorija za praćenje intervala od 15 minuta (900 sekundi)
last_saved = {}

def get_croatia_time():
    # Postavlja trenutno vrijeme za Hrvatsku
    return datetime.utcnow() + timedelta(hours=2)

def get_bus_type(gbr):
    try:
        num = int(gbr)
        if 716 <= num <= 725 or 731 <= num <= 750 or 811 <= num <= 830:
            return "cng"
    except:
        pass
    return "diesel"

# --- RUTE ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

@app.route('/api/logs')
def get_logs_data():
    try:
        # Dohvaća zadnjih 200 zapisa za Rijeku iz baze
        res = supabase.table("bus_logs").select("*").eq("city", "Rijeka").order("id", desc=True).limit(200).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    url = "https://cloud.it-sistemi.com/AutotrolejS3/api/v1/vehicle-positions"
    try:
        r = requests.get(url, timeout=10)
        data = r.json().get("data", [])
        now = get_croatia_time()
        current_ts = time.time()
        
        # Praćenje je aktivno do petka u 06:00
        end_time = datetime(2026, 4, 17, 6, 0)
        is_tracking_active = now < end_time

        output = []
        for bus in data:
            gbr = str(bus.get("vehicleNumber", ""))
            line = str(bus.get("lineName", "N/A"))
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            reg = bus.get("licensePlate", "N/A")

            if not gbr or lat is None or lat == 0:
                continue
            
            # Podaci za kartu
            output.append({
                "garageNumber": gbr,
                "name": line,
                "latitude": lat,
                "longitude": lon,
                "type": get_bus_type(gbr),
                "destination": bus.get("destinationName", "N/A"),
                "registration": reg,
                "speed": bus.get("speed", 0)
            })

            # LOGIRANJE U SUPABASE
            if is_tracking_active:
                # Provjera: je li prošlo 15 min ILI je nova linija?
                bus_state = last_saved.get(gbr, {"ts": 0, "line": ""})
                
                if (current_ts - bus_state['ts'] >= 900) or (bus_state['line'] != line):
                    try:
                        supabase.table("bus_logs").insert({
                            "garage_num": gbr,
                            "line": line,
                            "reg": reg,
                            "lat": lat,
                            "lon": lon,
                            "city": "Rijeka",
                            "date": now.strftime("%Y-%m-%d"),
                            "time": now.strftime("%H:%M:%S")
                        }).execute()
                        
                        # Ažuriraj zadnje spremljeno stanje
                        last_saved[gbr] = {"ts": current_ts, "line": line}
                    except Exception as e:
                        print(f"Supabase Error za GBR {gbr}: {e}")

        return jsonify({"vehicles": output})
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    # Render koristi PORT okolišnu varijablu
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
