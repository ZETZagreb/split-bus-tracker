import os
import sqlite3
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Inicijalizacija baze podataka za praćenje povijesti
def init_db():
    conn = sqlite3.connect('bus_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  garage_num TEXT, line TEXT, reg TEXT, 
                  time TEXT, lat REAL, lon REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://fleet.promet-split.hr/'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        # Logiranje u bazu podataka
        conn = sqlite3.connect('bus_history.db')
        c = conn.cursor()
        now = datetime.now().strftime("%H:%M:%S")
        
        for bus in data.get("vehicles", []):
            gbr = bus.get("garageNumber")
            line = str(bus.get("name", "")).replace("Linija ", "")
            reg = bus.get("registrationNumber")
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            
            # Spremi u bazu
            c.execute("INSERT INTO logs (garage_num, line, reg, time, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
                      (gbr, line, reg, now, lat, lon))
        
        conn.commit()
        conn.close()
        return jsonify(data)
    except:
        return jsonify({"vehicles": []})

@app.route('/api/history/<garage_num>')
def get_history(garage_num):
    conn = sqlite3.connect('bus_history.db')
    c = conn.cursor()
    # Dohvaća zadnjih 100 zapisa za taj bus
    c.execute("SELECT line, time, reg FROM logs WHERE garage_num = ? ORDER BY id DESC LIMIT 100", (garage_num,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    last_line = ""
    for r in rows:
        # Prikazujemo samo kad bus promijeni liniju da ne bude pretrpano
        if r[0] != last_line:
            history.append({"line": r[0], "time": r[1], "reg": r[2]})
            last_line = r[0]
            
    return jsonify(history)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
