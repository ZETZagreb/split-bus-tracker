from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    # Pokušavamo dohvatiti podatke
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Logiranje za nas (vidjet ćeš ovo u 'Server log' ako zapne)
        print(f"Dohvaćeno vozila: {len(data)}") 
        
        return jsonify(data)
    except Exception as e:
        print(f"Greška pri dohvaćanju: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)