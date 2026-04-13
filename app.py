import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Memorija za praćenje pokreta
active_tracking = {}

# OVDE MOŽEŠ DODATI PRAVI VOZNI RED ZA KLJUČNE LINIJE
# Ako linije nema ovdje, sustav će koristiti "pametno zaokruživanje"
VOZNI_REDOVI = {
    "37": ["07:05", "07:25", "07:45", "08:05", "08:25", "08:45"],
    "6": ["07:00", "07:15", "07:30", "07:45", "08:00"]
}

def odredi_pravi_polazak(linija, trenutno_vrijeme):
    sad = trenutno_vrijeme
    h_m = sad.strftime("%H:%M")
    
    if linija in VOZNI_REDOVI:
        polasci = VOZNI_REDOVI[linija]
        # Tražimo polazak koji je bio najbliži, ali gledamo i kašnjenje
        # Logika: Ako je bus krenuo u 07:14, a polasci su 07:05 i 07:25,
        # razlika do 07:05 je 9 min (kašnjenje), a do 07:25 je 11 min (uranjanje).
        # Sustav bira manju razliku.
        najblizi = min(polasci, key=lambda x: abs((datetime.strptime(x, "%H:%M") - datetime.strptime(h_m, "%H:%M")).total_seconds()))
        return najblizi
    else:
        # Ako nemamo vozni red za tu liniju, zaokruži na najbližih 5 min
        minute = sad.minute
        ostatak = minute % 5
        novo = sad - timedelta(minutes=ostatak) if ostatak < 3 else sad + timedelta(minutes=(5 - ostatak))
        return novo.strftime("%H:%M")

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
        
        now = datetime.now()
        now_date = now.strftime("%d.%m.%Y.")
        
        formatted_vehicles = []
        for bus in vehicles:
            lat, lon = bus.get("latitude"), bus.get("longitude")
            if not lat or not lon: continue

            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            
            if gbr not in active_tracking:
                active_tracking[gbr] = {'lat': lat, 'lon': lon, 'status': 'miruje', 'fixed_dep': '---'}

            # Detekcija pokreta (mora se pomaknuti s mjesta)
            dist = abs(lat - active_tracking[gbr]['lat']) + abs(lon - active_tracking[gbr]['lon'])
            
            if dist > 0.0012: # KRENUO JE
                if active_tracking[gbr]['status'] == 'miruje':
                    # Određujemo polazak prema voznom redu
                    active_tracking[gbr]['fixed_dep'] = odredi_pravi_polazak(line, now)
                    active_tracking[gbr]['status'] = 'u_pokretu'
                active_tracking[gbr]['lat'] = lat
                active_tracking[gbr]['lon'] = lon
            elif dist < 0.0001: # STOJI
                active_tracking[gbr]['status'] = 'miruje'
                active_tracking[gbr]['fixed_dep'] = '---'

            v = {
                "garageNumber": gbr, "latitude": lat, "longitude": lon,
                "name": line, 
                "destinationName": "U vožnji" if active_tracking[gbr]['status'] == 'u_pokretu' else "Na peronu",
                "scheduledDeparture": active_tracking[gbr]['fixed_dep'],
                "registrationNumber": bus.get("registrationNumber") or "N/A"
            }
            formatted_vehicles.append(v)

            if active_tracking[gbr]['status'] == 'u_pokretu':
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr, "line": line, "reg": v["registrationNumber"],
                        "date": now_date, "time": now.strftime("%H:%M"), "lat": lat, "lon": lon,
                        "scheduled_departure_time": str(v["scheduledDeparture"])
                    }).execute()
                except: pass

        return jsonify({"vehicles": formatted_vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
