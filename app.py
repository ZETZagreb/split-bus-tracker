import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')

# Supabase konekcija
SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Memorija za praćenje buseva
trip_memory = {}

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

def izracunaj_polazak_unazad(linija, sad):
    """
    Automatski izračunava najbliži prošli polazak.
    Za 37 koristi interval od 20 min, za ostale 15 min.
    """
    minute = sad.minute
    # Linija 37: polasci na :00, :20, :40
    if linija == "37":
        interval = 20
    else:
        # Većina ostalih linija ide svakih 15 ili 30 min
        interval = 15
        
    zadnji_polazak_minute = (minute // interval) * interval
    return f"{sad.hour:02d}:{zadnji_polazak_minute:02d}"

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
        
        current_gbrs = []
        formatted_vehicles = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            
            if not gbr or not lat: continue
            current_gbrs.append(gbr)

            # Ako bus tek uđe u vidno polje, odredi mu polazak i smjer
            if gbr not in trip_memory:
                polazak = izracunaj_polazak_unazad(line, now)
                trip_memory[gbr] = {
                    'dep': polazak, 
                    'last_lon': lon,
                    'dir': "U vožnji"
                }
            
            # Dinamička detekcija smjera (Istok-Zapad)
            stari_lon = trip_memory[gbr].get('last_lon', lon)
            if lon > stari_lon + 0.0001:
                trip_memory[gbr]['dir'] = "Split / Istok"
            elif lon < stari_lon - 0.0001:
                trip_memory[gbr]['dir'] = "Trogir/Omiš/Zapad"
            
            trip_memory[gbr]['last_lon'] = lon

            # Pakiranje podataka za frontend
            v = {
                "garageNumber": gbr,
                "latitude": lat,
                "longitude": lon,
                "name": line,
                "destinationName": trip_memory[gbr]['dir'],
                "scheduledDeparture": trip_memory[gbr]['dep'],
                "registrationNumber": bus.get("registrationNumber") or "N/A"
            }
            formatted_vehicles.append(v)

            # Upis u Supabase logove
            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr,
                    "line": line,
                    "reg": v["registrationNumber"],
                    "date": now.strftime("%d.%m.%Y."),
                    "time": now.strftime("%H:%M"),
                    "lat": lat,
                    "lon": lon,
                    "scheduled_departure_time": v["scheduledDeparture"],
                    "direction": v["destinationName"]
                }).execute()
            except:
                pass

        # Brisanje buseva koji više nisu aktivni
        for k in list(trip_memory.keys()):
            if k not in current_gbrs:
                del trip_memory[k]

        return jsonify({"vehicles": formatted_vehicles})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
