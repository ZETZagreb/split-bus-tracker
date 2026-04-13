import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import math

app = Flask(__name__)

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LINIJE_DATA = {
    "37": {"start": (43.514, 16.443), "odredista": ["Split", "Trogir"], "interval": 20},
    "60": {"start": (43.506, 16.441), "odredista": ["Split", "Omiš"], "interval": 30},
    "1":  {"start": (43.514, 16.443), "odredista": ["Starine", "HNK"], "interval": 15},
    "9":  {"start": (43.514, 16.443), "odredista": ["Trajektna Luka", "Brda"], "interval": 15},
    "default": {"start": (43.514, 16.443), "odredista": ["Centar", "Periferija"], "interval": 15}
}

trip_memory = {}

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def odredi_precizni_polazak(linija, lat, lon, sad):
    data = LINIJE_DATA.get(linija, LINIJE_DATA["default"])
    dist = haversine(lat, lon, data["start"][0], data["start"][1])
    minuta_od_starta = (dist / 22) * 60
    vrijeme_kretanja = sad - timedelta(minutes=minuta_od_starta)
    interval = data["interval"]
    offset = (vrijeme_kretanja.minute % interval)
    if offset > (interval / 2):
        zaokruzene_minute = (vrijeme_kretanja.minute // interval + 1) * interval
    else:
        zaokruzene_minute = (vrijeme_kretanja.minute // interval) * interval
    polazak_vrijeme = vrijeme_kretanja.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=zaokruzene_minute)
    return polazak_vrijeme.strftime("%H:%M")

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
        output = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            lat, lon = bus.get("latitude"), bus.get("longitude")
            reg = bus.get("registrationNumber") or "N/A"
            
            if not gbr or not lat: continue
            current_gbrs.append(gbr)

            l_data = LINIJE_DATA.get(line, LINIJE_DATA["default"])
            
            if gbr not in trip_memory or trip_memory[gbr].get('line') != line:
                dep = odredi_precizni_polazak(line, lat, lon, now)
                trip_memory[gbr] = {
                    'dep': dep, 
                    'line': line,
                    'last_lat': lat, 
                    'last_lon': lon, 
                    'dir': l_data["odredista"][0],
                    'reg': reg
                }
            else:
                dist_now = haversine(lat, lon, l_data["start"][0], l_data["start"][1])
                dist_old = haversine(trip_memory[gbr]['last_lat'], trip_memory[gbr]['last_lon'], l_data["start"][0], l_data["start"][1])
                
                if dist_now > dist_old + 0.005:
                    trip_memory[gbr]['dir'] = l_data["odredista"][1]
                elif dist_now < dist_old - 0.005:
                    trip_memory[gbr]['dir'] = l_data["odredista"][0]

            trip_memory[gbr]['last_lat'] = lat
            trip_memory[gbr]['last_lon'] = lon

            v = {
                "garageNumber": gbr,
                "latitude": lat,
                "longitude": lon,
                "name": line,
                "destinationName": trip_memory[gbr]['dir'],
                "scheduledDeparture": trip_memory[gbr]['dep'],
                "registrationNumber": reg
            }
            output.append(v)

            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr,
                    "line": line,
                    "reg": reg,
                    "date": now.strftime("%d.%m.%Y."),
                    "time": now.strftime("%H:%M"),
                    "lat": lat,
                    "lon": lon,
                    "scheduled_departure_time": v["scheduled_departure_time"] if "scheduled_departure_time" in v else v["scheduledDeparture"],
                    "direction": v["destinationName"]
                }).execute()
            except:
                pass

        for k in list(trip_memory.keys()):
            if k not in current_gbrs:
                del trip_memory[k]

        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
