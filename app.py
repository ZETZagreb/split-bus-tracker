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
    # Službeni Fleet API
    url = "https://fleet.promet-split.hr/api/v1/vehicles"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        fleet_data = r.json()
        
        # Pretvaramo Fleet format u tvoj format za mapu
        formatted_vehicles = []
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        for bus in fleet_data:
            # Fleet koristi 'lat'/'lon' i 'garageNumber'
            v = {
                "garageNumber": str(bus.get("garageNumber", "")),
                "latitude": bus.get("lat"),
                "longitude": bus.get("lon"),
                "registrationNumber": bus.get("plateNumber", "N/A"),
                "name": str(bus.get("lineCode", "N/A")),
                "destinationName": bus.get("destination", "U prometu"),
                "scheduledDeparture": bus.get("departureTime", "---")
            }
            formatted_vehicles.append(v)

            # SPREMANJE U SUPABASE
            try:
                supabase.table("bus_logs").insert({
                    "garage_num": v["garageNumber"],
                    "line": v["name"],
                    "reg": v["registrationNumber"],
                    "date": now_date,
                    "time": now_time,
                    "lat": v["latitude"],
                    "lon": v["longitude"],
                    "trip_id": str(bus.get("tripId", "N/A")),
                    "scheduled_departure_time": str(v["scheduledDeparture"]),
                    "direction": str(v["destinationName"])
                }).execute()
            except:
                continue
                
        return jsonify({"vehicles": formatted_vehicles})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
