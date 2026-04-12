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
    # Koristimo API koji napaja njihovu Fleet mapu
    url = "https://fleet.promet-split.hr/api/v1/vehicles"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        vehicles = r.json()
        
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        for bus in vehicles:
            # Fleet API obično koristi 'lineCode' ili 'route'
            line = str(bus.get("lineCode") or bus.get("lineName") or "N/A")
            gbr = str(bus.get("garageNumber") or bus.get("id"))
            
            # Ključna polja koja tražiš (ovako ih šalje Fleet sustav)
            direction = bus.get("destination") or bus.get("direction") or "Čeka polazak"
            sch_dep = bus.get("departureTime") or bus.get("scheduledTime") or "---"
            t_id = bus.get("tripId") or "N/A"

            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr,
                    "line": line,
                    "reg": str(bus.get("plateNumber") or bus.get("registration")),
                    "date": now_date,
                    "time": now_time,
                    "lat": bus.get("latitude"),
                    "lon": bus.get("longitude"),
                    "trip_id": str(t_id),
                    "scheduled_departure_time": str(sch_dep),
                    "direction": str(direction)
                }).execute()
            except:
                continue
                
        return jsonify({"vehicles": vehicles})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
