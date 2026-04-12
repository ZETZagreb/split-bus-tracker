import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)

# Tvoji podaci povezani s bazom
SUPABASE_URL = "https://ohxghzlbdflyqjatcwcb.supabase.co"
SUPABASE_KEY = "sb_publishable_hBKMq44_LWLCjlO_PfKQ9Q_yB-mZVDO"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        vehicles = data.get("vehicles", [])
        for bus in vehicles:
            # Spremanje svakog autobusa u Supabase bazu
            try:
                supabase.table("bus_logs").insert({
                    "garage_num": str(bus.get("garageNumber")),
                    "line": str(bus.get("name", "")).replace("Linija ", ""),
                    "reg": str(bus.get("registrationNumber")),
                    "date": now_date,
                    "time": now_time,
                    "lat": bus.get("latitude"),
                    "lon": bus.get("longitude")
                }).execute()
            except:
                pass
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"vehicles": []})

@app.route('/api/full_history/<garage_num>')
def get_full_history(garage_num):
    try:
        response = supabase.table("bus_logs") \
            .select("line, date, time, reg") \
            .eq("garage_num", garage_num) \
            .order("id", desc=True) \
            .limit(200) \
            .execute()
        
        history = []
        last_line = ""
        for r in response.data:
            if r['line'] != last_line:
                history.append(r)
                last_line = r['line']
        return jsonify(history)
    except:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
