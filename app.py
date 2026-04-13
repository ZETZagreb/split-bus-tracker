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
    # Koristimo API koji koristi njihova mobilna mapa (stabilniji je)
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        vehicles = data.get("vehicles", [])
        
        formatted_vehicles = []
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        for bus in vehicles:
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            gbr = str(bus.get("garageNumber") or "")
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            
            # Ako nema smjera u feedu, provjeravamo alternative
            dest = bus.get("destinationName") or bus.get("directionName") or "Čeka polazak"
            dep = bus.get("scheduledDeparture") or "---"
            reg = bus.get("registrationNumber") or "N/A"

            if lat and lon:
                v = {
                    "garageNumber": gbr,
                    "latitude": lat,
                    "longitude": lon,
                    "registrationNumber": reg,
                    "name": line,
                    "destinationName": dest,
                    "scheduledDeparture": dep
                }
                formatted_vehicles.append(v)
                
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr, "line": line, "reg": reg,
                        "date": now_date, "time": now_time, "lat": lat, "lon": lon,
                        "trip_id": str(bus.get("tripId") or ""),
                        "scheduled_departure_time": str(dep), "direction": str(dest)
                    }).execute()
                except:
                    continue
                    
        return jsonify({"vehicles": formatted_vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
