import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client
import time

app = Flask(__name__)

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Praćenje zadnjeg spremanja u bazu
last_db_save = {}

BUS_MODELS = {
    "246": "MAN Lion's Regio", "248": "MAN Lion's Regio", "249": "MAN Lion's Regio",
    "250": "MAN Lion's Regio", "251": "MAN Lion's Regio", "252": "MAN Lion's Regio",
    "253": "MAN Lion's Regio", "254": "MAN Lion's Regio", "263": "MB Citaro (Facelift)",
    "264": "MB Citaro (Facelift)", "265": "MB Citaro (Facelift)", "266": "MB Citaro G (Facelift)",
    "267": "MB Citaro G (Facelift)", "268": "MB Citaro G (Facelift)", "269": "MB Citaro G (Facelift)",
    "270": "MB Citaro G (Facelift)", "271": "MB Citaro G (Facelift)", "272": "MB Citaro G (Facelift)",
    "273": "MB Citaro G (Facelift)", "274": "MB Citaro G (Facelift)", "275": "MB Citaro G (Facelift)",
    "276": "Irisbus Daily", "277": "Irisbus Daily", "279": "Iveco Daily",
    "285": "Irisbus Crossway LE", "286": "Irisbus Crossway LE", "287": "Irisbus Crossway LE",
    "288": "Irisbus Crossway LE", "289": "Irisbus Crossway LE", "290": "Irisbus Crossway",
    "291": "Irisbus Crossway", "292": "Irisbus Crossway", "293": "Irisbus Crossway",
    "294": "Irisbus Crossway", "295": "Irisbus Crossway", "296": "MAN Lion's City",
    "297": "MAN Lion's City", "298": "MAN Lion's City", "299": "MAN Lion's City",
    "300": "MAN Lion's City", "301": "MAN Lion's City", "307": "MB Citaro G (Facelift)",
    "308": "MB Citaro G (Facelift)", "309": "Irisbus Daily", "310": "MB Citaro C2 G",
    "311": "MB Citaro C2 G", "312": "MB Citaro C2 G", "313": "MB Citaro C2 G",
    "314": "MB Citaro C2 G", "315": "MB Citaro C2 G", "316": "MB Citaro C2 G",
    "317": "MB Citaro C2 G", "318": "MB Citaro C2 G",
    "001": "MAN Lion's City", "002": "MAN Lion's City", "003": "MAN Lion's City",
    "004": "MAN Lion's City", "005": "MAN Lion's City", "006": "MAN Lion's City",
    "007": "MAN Lion's City", "008": "MAN Lion's City", "009": "MAN Lion's City",
    "010": "MAN Lion's City", "011": "MAN Lion's City", "012": "MAN Lion's City",
    "013": "MAN Lion's City", "014": "MAN Lion's City", "015": "MB Citaro C2 G",
    "016": "MB Citaro C2 G", "017": "MB Citaro C2 G", "018": "MB Citaro C2 G",
    "019": "MB Citaro C2 G", "020": "MB Citaro C2 G", "021": "MB Citaro C2 G",
    "022": "MB Citaro C2 G", "023": "MB Citaro C2 G", "024": "MB Citaro C2 G",
    "025": "MB Citaro C2 G", "026": "MB Citaro C2 G", "027": "MB Citaro C2 G",
    "028": "MB Citaro C2 G", "029": "MB Citaro C2 G", "030": "MB Citaro C2 G",
    "031": "MB Citaro C2 G", "032": "MB Citaro C2 G", "033": "MB Citaro C2 G",
    "034": "MB Citaro C2 G", "035": "MB Citaro C2 G", "036": "MB Citaro C2 G",
    "037": "MB Citaro C2 G", "038": "MB Citaro C2 G", "039": "MB Citaro C2 G",
    "040": "MB Citaro C2 G", "041": "MB Citaro C2 G", "042": "MB Citaro C2 G",
    "043": "MB Citaro C2 G", "044": "MB Citaro C2 G", "045": "Iveco Crossway LE",
    "046": "Iveco Crossway LE", "047": "Iveco Crossway LE", "048": "Iveco Crossway LE",
    "049": "Iveco Crossway LE", "050": "Iveco Crossway LE", "051": "Iveco Crossway LE",
    "052": "Iveco Crossway LE", "053": "MAN Lion's City 12C", "054": "MAN Lion's City 12C",
    "055": "MAN Lion's City 12C", "056": "MAN Lion's City 12C", "057": "MAN Lion's City 12C",
    "058": "MAN Lion's City 12C", "059": "MAN Lion's City 12C", "060": "MAN Lion's City 12C",
    "061": "MB Intouro (III)", "062": "MB Intouro (III)", "063": "MB Intouro (III)",
    "064": "MB Intouro (III)", "065": "MB Intouro (III)", "066": "MB Intouro (III)",
    "067": "MB Intouro (III)", "068": "MB Intouro (III)", "069": "Iveco Crossway LE",
    "070": "Iveco Crossway LE", "071": "Iveco Crossway LE", "072": "Iveco Crossway LE",
    "073": "Iveco Crossway LE", "074": "Iveco Crossway LE", "075": "Iveco Crossway LE",
    "076": "Iveco Crossway LE", "077": "Iveco Daily 70 C21", "078": "Iveco Daily 70 C21",
    "079": "Iveco Daily 70 C21", "080": "Iveco Daily 70 C21", "081": "Iveco Daily 70 C21",
    "082": "Iveco Daily 70 C21", "083": "MB Citaro C2 G", "084": "MB Citaro C2 G",
    "085": "MB Citaro C2 G", "086": "MB Citaro C2 G", "087": "MB Citaro C2 G",
    "088": "MB Citaro C2 G", "089": "MB Citaro C2 G", "090": "MB Citaro C2 G",
    "091": "MB Citaro C2 G", "092": "MB Citaro C2 G", "093": "Otokar Vectio U LE",
    "094": "Otokar Vectio U LE", "095": "Otokar Vectio U LE", "096": "Otokar Vectio U LE",
    "097": "Otokar Vectio U LE", "098": "Otokar Vectio U LE", "099": "Otokar Vectio U LE",
    "100": "MB Sprinter", "101": "MB Citaro C2 G", "102": "MB Citaro C2 G",
    "103": "MB Citaro C2 G", "104": "MB Citaro C2 G", "105": "MB Citaro C2 G",
    "106": "MB Citaro C2 G", "107": "MB Citaro C2 G", "108": "MB Citaro C2 G",
    "109": "MB Citaro C2 G", "110": "MB Citaro C2 G", "111": "MAN Lion's City",
    "112": "MAN Lion's City", "113": "MAN Lion's City", "114": "MAN Lion's City",
    "115": "MAN Lion's City", "116": "MAN Lion's City", "117": "MAN Lion's City",
    "118": "MAN Lion's City", "119": "Iveco Daily", "120": "Iveco Daily",
    "121": "Iveco Daily", "122": "Iveco Daily", "123": "Iveco Daily",
    "124": "Iveco Daily", "125": "Iveco Daily", "126": "Iveco Daily"
}

def get_croatia_time():
    return datetime.utcnow() + timedelta(hours=2)

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
        now_ts = time.time()
        output = []

        for bus in vehicles:
            raw_gbr = str(bus.get("garageNumber", ""))
            gbr = raw_gbr.zfill(3) if raw_gbr.isdigit() else raw_gbr
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            reg = bus.get("registrationNumber") or "N/A"
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            marka = BUS_MODELS.get(gbr, "N/A")

            if not gbr or not lat: continue

            v = {
                "garageNumber": gbr,
                "name": line,
                "registrationNumber": reg,
                "brand": marka,
                "latitude": lat,
                "longitude": lon
            }
            output.append(v)

            # SPREMANJE U BAZU (Svakih 60s)
            if gbr not in last_db_save or (now_ts - last_db_save[gbr]) > 60:
                try:
                    supabase.table("bus_logs").insert({
                        "garage_num": gbr, "line": line, "reg": reg, "brand": marka,
                        "date": now.strftime("%d.%m.%Y."), "time": now.strftime("%H:%M"),
                        "lat": lat, "lon": lon
                    }).execute()
                    last_db_save[gbr] = now_ts
                except: pass

        # Zahtjev dolazi od browsera -> vrati JSON
        if request.headers.get('Accept') and 'application/json' in request.headers.get('Accept'):
            return jsonify({"vehicles": output})
        
        # Zahtjev dolazi od Cronjoba -> vrati samo OK (da ne bude "output too large")
        return "OK", 200
    except:
        return "Error", 500

from flask import request # Dodajemo ovo na vrh kod uvoza
