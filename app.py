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

def zaokruzi_na_polazak(vrijeme_obj):
    """Zaokružuje trenutno vrijeme na najbližih 5 minuta (standard polazaka)"""
    minute = vrijeme_obj.minute
    ostatak = minute % 5
    if ostatak < 3:
        novo_vrijeme = vrijeme_obj - timedelta(minutes=ostatak)
    else:
        novo_vrijeme = vrijeme_obj + timedelta(minutes=(5 - ostatak))
    return novo_vrijeme.strftime("%H:%M")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        vehicles = r.json().get("vehicles", [])
        
        now = datetime.now()
        now_date = now.strftime("%d.%m.%Y.")
        
        formatted_vehicles = []
        for bus in vehicles:
            lat, lon = bus.get("latitude"), bus.get("longitude")
            if not lat or not lon: continue

            gbr = str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            
            # Dohvat originalnih podataka ako postoje
            dest = bus.get("destinationName")
            dep = bus.get("scheduledDeparture")

            if gbr not in active_tracking:
                active_tracking[gbr] = {'lat': lat, 'lon': lon, 'status': 'miruje', 'fixed_dep': '---'}

            # Detekcija pokreta
            dist = abs(lat - active_tracking[gbr]['lat']) + abs(lon - active_tracking[gbr]['lon'])
            
            if dist > 0.0012: # Bus je krenuo
                if active_tracking[gbr]['status'] == 'miruje':
                    # Tek sad fiksiramo polazak na najbliži termin voznog reda
                    active_tracking[gbr]['fixed_dep'] = zaokruzi_na_polazak(now)
                    active_tracking[gbr]['status'] = 'u_pokretu'
                active_tracking[gbr]['lat'] = lat
                active_tracking[gbr]['lon'] = lon
            elif dist < 0.0001: # Bus stoji na peronu ili u garaži
                active_tracking[gbr]['status'] = 'miruje'
                active_tracking[gbr]['fixed_dep'] = '---'

            # Određivanje prikaza
            final_dest = dest if (dest and dest != "null") else ("U vožnji" if active_tracking[gbr]['status'] == 'u_pokretu' else "Na peronu / Čeka")
            final_dep = dep if (dep and dep != "null") else active_tracking[gbr]['fixed_dep']

            v = {
                "garageNumber": gbr, "latitude": lat, "longitude": lon,
                "name": line, "destinationName": final_dest, "scheduledDeparture": final_dep,
                "registrationNumber": bus.get("registrationNumber") or "N/A"
            }
            formatted_vehicles.append(v)

            # UPIS U BAZU: Samo ako je prepoznat polazak i kretanje
            if active_tracking[gbr]['status'] == 'u_pokretu':
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr, "line": line, "reg": v["registrationNumber"],
                        "date": now_date, "time": now.strftime("%H:%M"), "lat": lat, "lon": lon,
                        "scheduled_departure_time": str(final_dep), "direction": str(final_dest)
                    }).execute()
                except: pass

        return jsonify({"vehicles": formatted_vehicles})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
