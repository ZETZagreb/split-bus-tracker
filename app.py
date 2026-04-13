import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import math

app = Flask(__name__)

# Supabase setup
SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# DEFINICIJA LINIJA (Terminali i Odredišta)
# Format: "Linija": {"start": (lat, lon), "cilj_ime": "Odredište", "interval": minute}
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
    # Izračun zračne udaljenosti u km
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def odredi_polazak_po_lokaciji(linija, lat, lon, sad):
    data = LINIJE_DATA.get(linija, LINIJE_DATA["default"])
    start_lat, start_lon = data["start"]
    
    # Koliko je bus udaljen od starta (km)
    dist = haversine(lat, lon, start_lat, start_lon)
    
    # Pretpostavljena prosječna brzina u gradu je 25 km/h (uključujući stanice)
    minuta_od_starta = (dist / 25) * 60
    
    # Stvarno vrijeme kretanja (Sad minus procijenjeno vrijeme puta)
    vrijeme_kretanja = sad - timedelta(minutes=minuta_od_starta)
    
    # Zaokruži na najbliži polazak prema intervalu te linije
    interval = data["interval"]
    zaokruzene_minute = (vrijeme_kretanja.minute // interval) * interval
    return vrijeme_kretanja.replace(minute=zaokruzene_minute).strftime("%H:%M")

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        vehicles = r.json().get("vehicles", [])
        now = get_croatia_time()
        current_gbrs = []
        output = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            lat, lon = bus.get("latitude"), bus.get("longitude")
            if not gbr or not lat: continue
            current_gbrs.append(gbr)

            # 1. SMJER (Samo odredišta te linije)
            l_data = LINIJE_DATA.get(line, LINIJE_DATA["default"])
            if gbr not in trip_memory:
                # Prva detekcija
                dep = odredi_polazak_po_lokaciji(line, lat, lon, now)
                trip_memory[gbr] = {'dep': dep, 'last_lon': lon, 'dir': l_data["odredista"][0]}
            else:
                # Ako se udaljava od starta, ide prema odredištu [1], ako se približava prema [0]
                dist_now = haversine(lat, lon, l_data["start"][0], l_data["start"][1])
                dist_old = haversine(trip_memory[gbr]['last_lat'], trip_memory[gbr]['last_lon'], l_data["start"][0], l_data["start"][1]) if 'last_lat' in trip_memory[gbr] else dist_now
                
                if dist_now > dist_old + 0.05: # Miče se od starta
                    trip_memory[gbr]['dir'] = l_data["odredista"][1]
                elif dist_now < dist_old - 0.05: # Vraća se prema startu
                    trip_memory[gbr]['dir'] = l_data["odredista"][0]

            trip_memory[gbr]['last_lat'] = lat
            trip_memory[gbr]['last_lon'] = lon

            output.append({
                "garageNumber": gbr, "latitude": lat, "longitude": lon, "name": line,
                "destinationName": trip_memory[gbr]['dir'],
                "scheduledDeparture": trip_memory[gbr]['dep']
            })
        
        # Ovdje bi išao i Supabase insert po potrebi...
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
