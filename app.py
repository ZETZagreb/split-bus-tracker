import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# TVOJA BAZA PODATAKA PO GBR-u
BUS_MODELS = {
    "246": "MAN Lion's Regio (ÜL 314)", "248": "MAN Lion's Regio (ÜL 314)", "249": "MAN Lion's Regio (ÜL 314)",
    "250": "MAN Lion's Regio (ÜL 314)", "251": "MAN Lion's Regio (ÜL 314)", "252": "MAN Lion's Regio (ÜL 314)",
    "253": "MAN Lion's Regio (ÜL 314)", "254": "MAN Lion's Regio (ÜL 314)", "263": "Mercedes-Benz O530 Citaro (Facelift)",
    "264": "Mercedes-Benz O530 Citaro (Facelift)", "265": "Mercedes-Benz O530 Citaro (Facelift)", "266": "Mercedes-Benz O530 G Citaro (Facelift)",
    "267": "Mercedes-Benz O530 G Citaro (Facelift)", "268": "Mercedes-Benz O530 G Citaro (Facelift)", "269": "Mercedes-Benz O530 G Citaro (Facelift)",
    "270": "Mercedes-Benz O530 G Citaro (Facelift)", "271": "Mercedes-Benz O530 G Citaro (Facelift)", "272": "Mercedes-Benz O530 G Citaro (Facelift)",
    "273": "Mercedes-Benz O530 G Citaro (Facelift)", "274": "Mercedes-Benz O530 G Citaro (Facelift)", "275": "Mercedes-Benz O530 G Citaro (Facelift)",
    "276": "Irisbus Daily Tourys 50 C15", "277": "Irisbus Daily Tourys 50 C15", "279": "Iveco Daily 50 C18",
    "285": "Irisbus Crossway LE", "286": "Irisbus Crossway LE", "287": "Irisbus Crossway LE", "288": "Irisbus Crossway LE",
    "289": "Irisbus Crossway LE", "290": "Irisbus Crossway", "291": "Irisbus Crossway", "292": "Irisbus Crossway",
    "293": "Irisbus Crossway", "294": "Irisbus Crossway", "295": "Irisbus Crossway", "296": "MAN Lion's City (NL 323)",
    "297": "MAN Lion's City (NL 323)", "298": "MAN Lion's City (NL 323)", "299": "MAN Lion's City (NL 323)",
    "300": "MAN Lion's City (NL 323)", "301": "MAN Lion's City (NL 323)", "307": "Mercedes-Benz O530 G Citaro (Facelift)",
    "308": "Mercedes-Benz O530 G Citaro (Facelift)", "309": "Irisbus Daily 50 C18", "310": "Mercedes-Benz O530 G Citaro C2",
    "311": "Mercedes-Benz O530 G Citaro C2", "312": "Mercedes-Benz O530 G Citaro C2", "313": "Mercedes-Benz O530 G Citaro C2",
    "314": "Mercedes-Benz O530 G Citaro C2", "315": "Mercedes-Benz O530 G Citaro C2", "316": "Mercedes-Benz O530 G Citaro C2",
    "317": "Mercedes-Benz O530 G Citaro C2", "318": "Mercedes-Benz O530 G Citaro C2",
    "001": "MAN Lion's City (NL 323)", "002": "MAN Lion's City (NL 323)", "003": "MAN Lion's City (NL 323)",
    "004": "MAN Lion's City (NL 323)", "005": "MAN Lion's City (NL 323)", "006": "MAN Lion's City (NL 323)",
    "007": "MAN Lion's City (NL 323)", "008": "MAN Lion's City (NL 323)", "009": "MAN Lion's City (NL 323)",
    "010": "MAN Lion's City (NL 323)", "011": "MAN Lion's City (NL 323)", "012": "MAN Lion's City (NL 323)",
    "013": "MAN Lion's City (NL 323)", "014": "MAN Lion's City (NL 323)", "015": "Mercedes-Benz O530 G Citaro C2",
    "016": "Mercedes-Benz O530 G Citaro C2", "017": "Mercedes-Benz O530 G Citaro C2", "018": "Mercedes-Benz O530 G Citaro C2",
    "019": "Mercedes-Benz O530 G Citaro C2", "020": "Mercedes-Benz O530 G Citaro C2", "021": "Mercedes-Benz O530 G Citaro C2",
    "022": "Mercedes-Benz O530 G Citaro C2", "023": "Mercedes-Benz O530 G Citaro C2", "024": "Mercedes-Benz O530 G Citaro C2",
    "025": "Mercedes-Benz O530 G Citaro C2", "026": "Mercedes-Benz O530 G Citaro C2", "027": "Mercedes-Benz O530 G Citaro C2",
    "028": "Mercedes-Benz O530 G Citaro C2", "029": "Mercedes-Benz O530 G Citaro C2", "030": "Mercedes-Benz O530 G Citaro C2",
    "031": "Mercedes-Benz O530 G Citaro C2", "032": "Mercedes-Benz O530 G Citaro C2", "033": "Mercedes-Benz O530 G Citaro C2",
    "034": "Mercedes-Benz O530 G Citaro C2", "035": "Mercedes-Benz O530 G Citaro C2", "036": "Mercedes-Benz O530 G Citaro C2",
    "037": "Mercedes-Benz O530 G Citaro C2", "038": "Mercedes-Benz O530 G Citaro C2", "039": "Mercedes-Benz O530 G Citaro C2",
    "040": "Mercedes-Benz O530 G Citaro C2", "041": "Mercedes-Benz O530 G Citaro C2", "042": "Mercedes-Benz O530 G Citaro C2",
    "043": "Mercedes-Benz O530 G Citaro C2", "044": "Mercedes-Benz O530 G Citaro C2", "045": "Iveco Crossway LE City 12M",
    "046": "Iveco Crossway LE City 12M", "047": "Iveco Crossway LE City 12M", "048": "Iveco Crossway LE City 12M",
    "049": "Iveco Crossway LE City 12M", "050": "Iveco Crossway LE City 12M", "051": "Iveco Crossway LE City 12M",
    "052": "Iveco Crossway LE City 12M", "053": "MAN Lion's City 12C", "054": "MAN Lion's City 12C",
    "055": "MAN Lion's City 12C", "056": "MAN Lion's City 12C", "057": "MAN Lion's City 12C",
    "058": "MAN Lion's City 12C", "059": "MAN Lion's City 12C", "060": "MAN Lion's City 12C",
    "061": "Mercedes-Benz Intouro (III)", "062": "Mercedes-Benz Intouro (III)", "063": "Mercedes-Benz Intouro (III)",
    "064": "Mercedes-Benz Intouro (III)", "065": "Mercedes-Benz Intouro (III)", "066": "Mercedes-Benz Intouro (III)",
    "067": "Mercedes-Benz Intouro (III)", "068": "Mercedes-Benz Intouro (III)", "069": "Iveco Crossway LE City 12M",
    "070": "Iveco Crossway LE City 12M", "071": "Iveco Crossway LE City 12M", "072": "Iveco Crossway LE City 12M",
    "073": "Iveco Crossway LE City 12M", "074": "Iveco Crossway LE City 12M", "075": "Iveco Crossway LE City 12M",
    "076": "Iveco Crossway LE City 12M", "077": "Iveco Daily 70 C21", "078": "Iveco Daily 70 C21",
    "079": "Iveco Daily 70 C21", "080": "Iveco Daily 70 C21", "081": "Iveco Daily 70 C21",
    "082": "Iveco Daily 70 C21", "083": "Mercedes-Benz O530 G Citaro C2", "084": "Mercedes-Benz O530 G Citaro C2",
    "085": "Mercedes-Benz O530 G Citaro C2", "086": "Mercedes-Benz O530 G Citaro C2", "087": "Mercedes-Benz O530 G Citaro C2",
    "088": "Mercedes-Benz O530 G Citaro C2", "089": "Mercedes-Benz O530 G Citaro C2", "090": "Mercedes-Benz O530 G Citaro C2",
    "091": "Mercedes-Benz O530 G Citaro C2", "092": "Mercedes-Benz O530 G Citaro C2", "093": "Otokar Vectio U LE",
    "094": "Otokar Vectio U LE", "095": "Otokar Vectio U LE", "096": "Otokar Vectio U LE",
    "097": "Otokar Vectio U LE", "098": "Otokar Vectio U LE", "099": "Otokar Vectio U LE",
    "100": "Mercedes-Benz Sprinter 519 CDI", "101": "Mercedes-Benz O530 G Citaro C2", "102": "Mercedes-Benz O530 G Citaro C2",
    "103": "Mercedes-Benz O530 G Citaro C2", "104": "Mercedes-Benz O530 G Citaro C2", "105": "Mercedes-Benz O530 G Citaro C2",
    "106": "Mercedes-Benz O530 G Citaro C2", "107": "Mercedes-Benz O530 G Citaro C2", "108": "Mercedes-Benz O530 G Citaro C2",
    "109": "Mercedes-Benz O530 G Citaro C2", "110": "Mercedes-Benz O530 G Citaro C2", "111": "MAN Lion's City (NL 323)",
    "112": "MAN Lion's City (NL 323)", "113": "MAN Lion's City (NL 323)", "114": "MAN Lion's City (NL 323)",
    "115": "MAN Lion's City (NL 323)", "116": "MAN Lion's City (NL 323)", "117": "MAN Lion's City (NL 323)",
    "118": "MAN Lion's City (NL 323)", "119": "Iveco Daily 50C17", "120": "Iveco Daily 50C18",
    "121": "Iveco Daily 50C18", "122": "Iveco Daily 50C18", "123": "Iveco Daily 50C18",
    "124": "Iveco Daily 50C18", "125": "Iveco Daily 50C18", "126": "Iveco Daily 50C18"
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
        output = []

        for bus in vehicles:
            gbr = str(bus.get("garageNumber", "")).zfill(3) if str(bus.get("garageNumber", "")).isdigit() else str(bus.get("garageNumber", ""))
            line = str(bus.get("name", "")).replace("Linija ", "").strip()
            reg = bus.get("registrationNumber") or "N/A"
            lat = bus.get("latitude")
            lon = bus.get("longitude")

            # Dohvati marku iz baze prema GBR-u, ako nema stavi N/A
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

            try:
                supabase.table("bus_logs").insert({
                    "garage_num": gbr,
                    "line": line,
                    "reg": reg,
                    "brand": marka,
                    "date": now.strftime("%d.%m.%Y."),
                    "time": now.strftime("%H:%M"),
                    "lat": lat,
                    "lon": lon
                }).execute()
            except:
                pass

        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
