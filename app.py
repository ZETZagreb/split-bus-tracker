import os
import requests
import time
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
    # Pokušavamo dohvatiti podatke izravno s njihovog API-ja s tvojim ključem koji je još aktivan
    timestamp = int(time.time() * 1000)
    url = f"https://api.promet-split.hr/Fleet/api/v1/live/vehicles?t={timestamp}"
    
    headers = {
        'Accept': 'application/json',
        'x-auth-key': 'IxbMAfY6J5x1rSyfGmLPcMfCcyamb7xEfIuUpb8KNeE=',
        'Referer': 'https://fleet.promet-split.hr/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Ako službeni API baci grešku (npr. 401), automatski skačemo na stabilnu verziju
        if r.status_code != 200:
            raise Exception("API Key Expired")
            
        vehicles = r.json()
        formatted_vehicles = []
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        for bus in vehicles:
            lat = bus.get("lat")
            lon = bus.get("lon")
            gbr = str(bus.get("garageNumber") or "")
            line = str(bus.get("lineCode") or "---")
            dest = bus.get("destination") or "Čeka polazak"
            dep = bus.get("departureTime") or "---"
            reg = bus.get("plateNumber") or "N/A"

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
        # BACKUP: Ako Fleet API ne radi, koristi bus-split (autobusi su tu, ali nema smjera)
        backup_url = "https://www.bus-split.com/api/vehicles/live"
        r_back = requests.get(backup_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = r_back.json()
        return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
