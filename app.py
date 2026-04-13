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
    # Koristimo najstabilniji izvor za lokaciju
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        vehicles = data.get("vehicles", [])
        
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        formatted_vehicles = []
        for bus in vehicles:
            # Čišćenje i mapiranje
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            
            # Ako API ne šalje smjer, stavljamo "Čeka polazak" umjesto "U prometu"
            dest = bus.get("destinationName")
            if not dest or dest == "" or dest == "null":
                dest = "Čeka polazak / Indisponiran"
                
            dep = bus.get("scheduledDeparture") or "---"
            
            v = {
                "garageNumber": gbr,
                "latitude": bus.get("latitude"),
                "longitude": bus.get("longitude"),
                "registrationNumber": bus.get("registrationNumber") or "N/A",
                "name": line,
                "destinationName": dest,
                "scheduledDeparture": dep
            }
            
            if v["latitude"] and v["longitude"]:
                formatted_vehicles.append(v)
                # Arhiviranje u bazu
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr,
                        "line": line,
                        "reg": v["registrationNumber"],
                        "date": now_date,
                        "time": now_time,
                        "lat": v["latitude"],
                        "lon": v["longitude"],
                        "trip_id": str(bus.get("tripId") or ""),
                        "scheduled_departure_time": str(dep),
                        "direction": str(dest)
                    }).execute()
                except:
                    continue
                    
        return jsonify({"vehicles": formatted_vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
