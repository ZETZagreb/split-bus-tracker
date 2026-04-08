import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://najava.promet-split.hr/api/get-all-vehicles"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Dodajemo 'headers' da tvoj server glumi obični preglednik
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status koda: {response.status_code}") # Ovo ćemo vidjeti u Logs
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e), "note": "Server ne moze doci do Prometa"}), 500

if __name__ == '__main__':
    app.run(debug=True)
