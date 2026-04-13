import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lokalna memorija za trajanje sesije (GBR -> {'dep': '07:05', 'active': True})
trip_memory = {}

def get_croatia_time():
    # Prilagodba za našu vremensku zonu (UTC+2)
    return datetime.utcnow() + timedelta(hours=2)

def odredi_najbolji_polazak(linija, trenutno_vrijeme):
    sad = trenutno_vrijeme
    # Interval polazaka svakih 5 minuta
    intervali = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    polasci = [f"{h:02d}:{m:02d}" for h in range(5, 24) for m in intervali]
            
    najbolji_termin = "---"
    minimalna_razlika = 999
    
    for p in polasci:
        vrijeme_p = datetime.strptime(p, "%H:%M").replace(year=sad.year, month=sad.month, day=sad.day)
        razlika = (sad - vrijeme_p).total_seconds() / 60
        
        # Gledamo polaske unutar zadnjih 20 min (kašnjenje) ili 5 min unaprijed
        if -5 <= razlika <= 20:
            if abs(razlika) < minimalna_razlika:
                minimalna_razlika = abs(razlika)
                najbolji_termin = p
                
    return najbolji_termin

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        vehicles = r.json().get("vehicles", [])
        
        now = get_croatia_time()
        now_date = now.strftime("%d.%m.%Y.")
        now_time_str = now.strftime("%H:%M")
        
        formatted_vehicles = []
        current_gbrs = []

        for bus in vehicles:
            lat, lon = bus.get("latitude"), bus.get("longitude")
            if not lat or not lon: continue

            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            current_gbrs.append(gbr)

            # LOGIKA MEMORIJE:
            # Ako bus već ima zapisan polazak od ranije, koristi njega. 
            # Ako nema (tek je krenuo), izračunaj novi.
            if gbr not in trip_memory or trip_memory[gbr]['line'] != line:
                # Provjeri je li bus u pokretu (na osnovu API-ja ili jednostavne detekcije)
                # Ovdje pretpostavljamo da je bus aktivan ako je u listi
                novi_dep = odredi_najbolji_polazak(line, now)
                trip_memory[gbr] = {'dep': novi_dep, 'line': line, 'last_seen': now}
            
            # Ažuriraj vrijeme zadnjeg viđenja
            trip_memory[gbr]['last_seen'] = now

            v = {
                "garageNumber": gbr, "latitude": lat, "longitude": lon,
                "name": line,
                "destinationName": "U prometu",
                "scheduledDeparture": trip_memory[gbr]['dep'],
                "registrationNumber": bus.get("registrationNumber") or "N/A"
            }
            formatted_vehicles.append(v)

            # Upis u Supabase
            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr, "line": line, "reg": v["registrationNumber"],
                    "date": now_date, "time": now_time_str, "lat": lat, "lon": lon,
                    "scheduled_departure_time": str(v["scheduledDeparture"]),
                    "direction": "U prometu"
                }).execute()
            except: pass

        # Čišćenje memorije: obriši buseve koji više nisu na mapi (završili rutu)
        for gbr_key in list(trip_memory.keys()):
            if gbr_key not in current_gbrs:
                del trip_memory[gbr_key]

        return jsonify({"vehicles": formatted_vehicles})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
