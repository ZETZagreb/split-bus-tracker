import os
import sqlite3
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Kreiranje baze podataka za povijest ako ne postoji
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
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fleet.promet-split.hr/'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        # LOGIRANJE: Spremi trenutno stanje svakog busa u bazu
        conn = sqlite3.connect('bus_history.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for bus in data.get("vehicles", []):
            line_num = str(bus.get("name", "")).replace("Linija ", "")
            c.execute("INSERT INTO logs (garage_num, line, reg, time, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
                      (bus.get("garageNumber"), line_num, bus.get("registrationNumber"), now, bus.get("latitude"), bus.get("longitude")))
        
        conn.commit()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"vehicles": []})

# NOVO: Ruta za pregled povijesti određenog busa
@app.route('/api/history/<garage_num>')
def get_history(garage_num):
    conn = sqlite3.connect('bus_history.db')
    c = conn.cursor()
    c.execute("SELECT line, time FROM logs WHERE garage_num = ? ORDER BY time DESC LIMIT 50", (garage_num,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"line": r[0], "time": r[1]} for r in row])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
