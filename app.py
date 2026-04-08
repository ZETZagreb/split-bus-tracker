import os
from flask import Flask, render_template, jsonify
import requests

# Govorimo serveru točno gdje da traži HTML
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    url = "https://www.bus-split.com/api/vehicles/live"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    # Render koristi PORT varijablu, pa je ovo sigurnije
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
