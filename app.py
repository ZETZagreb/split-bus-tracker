import os
import sqlite3
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('bus_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  garage_num TEXT, line TEXT, reg TEXT, 
                  date TEXT, time TEXT, lat REAL, lon REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fleet.promet-split.hr/'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        conn = sqlite3.connect('bus_history.db', timeout=10)
        c = conn.cursor()
        now_date = datetime.now().strftime("%d.%m.%Y.")
        now_time = datetime.now().strftime("%H:%M")
        
        for bus in data.get("vehicles", []):
            gbr = bus.get("garageNumber")
            line = str(bus.get("name", "")).replace("Linija ", "")
            reg = bus.get("registrationNumber")
            c.execute("INSERT INTO logs (garage_num, line, reg, date, time, lat, lon) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (gbr, line, reg, now_date, now_time, bus.get("latitude"), bus.get("longitude")))
        
        conn.commit()
        conn.close()
        return jsonify(data)
    except:
        return jsonify({"vehicles": []})

@app.route('/api/full_history/<garage_num>')
def get_full_history(garage_num):
    conn = sqlite3.connect('bus_history.db')
    c = conn.cursor()
    # Dohvaća apsolutno sve zapise za taj gbr kroz sve dane
    c.execute("SELECT line, date, time, reg FROM logs WHERE garage_num = ? ORDER BY id DESC", (garage_num,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    last_line = ""
    for r in rows:
        # Prikazujemo samo promjene linija da lista ne bude kilometarska
        if r[0] != last_line:
            history.append({"line": r[0], "date": r[1], "time": r[2], "reg": r[3]})
            last_line = r[0]
            
    return jsonify(history)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
