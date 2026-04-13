import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://split.prometko.si/api/direct/vehicles"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        vehicles = data if isinstance(data, list) else data.get("vehicles", [])
        
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        formatted_vehicles = []
        
        for bus in vehicles:
            gbr = str(bus.get("garage_number") or bus.get("id") or "")
            line = str(bus.get("line_name") or bus.get("line_code") or "---").replace("Linija ", "").strip()
            dest = bus.get("destination") or bus.get("direction_name") or "U pripremi"
            dep = bus.get("scheduled_departure") or bus.get("departure") or "---"
            lat = bus.get("lat") or bus.get("latitude")
            lon = bus.get("lon") or bus.get("longitude")
            reg = bus.get("plate_number") or "N/A"

            v = {
                "garageNumber": gbr,
                "latitude": lat,
                "longitude": lon,
                "registrationNumber": reg,
                "name": line,
                "destinationName": dest,
                "scheduledDeparture": dep
            }
            
            if lat and lon:
                formatted_vehicles.append(v)
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr, "line": line, "reg": reg,
                        "date": now_date, "time": now_time, "lat": lat, "lon": lon,
                        "trip_id": str(bus.get("trip_id") or ""),
                        "scheduled_departure_time": str(dep), "direction": str(dest)
                    }).execute()
                except:
                    continue
                
        return jsonify({"vehicles": formatted_vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
