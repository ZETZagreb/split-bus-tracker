import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Memorija za praćenje polaska i smjera
trip_memory = {}

# Ovdje definiramo stvarne intervale (ovo simulira pravi vozni red)
# Za 37 znamo da ide svakih 20 min, za gradske svakih 15 itd.
VOZNI_RED_LOGIKA = {
    "37": 20, "60": 30, "1": 15, "9": 15, "3": 15, "6": 15, "default": 20
}

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

def odredi_stvarni_polazak(linija, sad):
    interval = VOZNI_RED_LOGIKA.get(linija, VOZNI_RED_LOGIKA["default"])
    # Tražimo zadnji puni polazak (npr. ako je sad 20:38, a ide svakih 20 min, polazak je bio 20:20)
    ukupno_minuta = sad.hour * 60 + sad.minute
    zadnji_polazak_minuta = (ukupno_minuta // interval) * interval
    
    h = zadnji_polazak_minuta // 60
    m = zadnji_polazak_minuta % 60
    return f"{h:02d}:{m:02d}"

def detektiraj_smjer(linija, lat, lon, stara_lokacija):
    if not stara_lokacija:
        return "U vožnji"
    
    stari_lat, stari_lon = stara_lokacija
    # Primjer za liniju 37: Ako longitude raste, ide prema Splitu, ako opada prema Trogiru
    if linija == "37":
        return "Split" if lon > stari_lon else "Trogir"
    
    # Općenita logika za ostale (zapad/istok)
    if lon > stari_lon: return "Smjer Istok/Split"
    if lon < stari_lon: return "Smjer Zapad/Van grada"
    
    return "U vožnji"

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        vehicles = r.json().get("vehicles", [])
        now = get_croatia_time()
        current_gbrs = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            lat, lon = bus.get("latitude"), bus.get("longitude")
            current_gbrs.append(gbr)

            # Ako je bus novi u memoriji
            if gbr not in trip_memory:
                # Izračunaj polazak unazad (ne "sad", nego kad je stvarno trebao krenuti)
                polazak = odredi_stvarni_polazak(line, now)
                trip_memory[gbr] = {
                    'dep': polazak, 
                    'line': line, 
                    'last_loc': (lat, lon),
                    'dir': "Detekcija..."
                }
            else:
                # Ažuriraj smjer na temelju kretanja
                novi_smjer = detektiraj_smjer(line, lat, lon, trip_memory[gbr]['last_loc'])
                trip_memory[gbr]['dir'] = novi_smjer
                trip_memory[gbr]['last_loc'] = (lat, lon)

            bus['scheduledDeparture'] = trip_memory[gbr]['dep']
            bus['destinationName'] = trip_memory[gbr]['dir']

        # Čišćenje memorije
        for key in list(trip_memory.keys()):
            if key not in current_gbrs: del trip_memory[key]

        return jsonify({"vehicles": vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
