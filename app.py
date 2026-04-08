import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    try:
        url = "https://najava.promet-split.hr/api/get-all-vehicles"
        response = requests.get(url, timeout=10)
        data = response.json()

        # TESTNA LOGIKA: Ako nema pravih buseva, dodajemo jedan lažni
        if not data.get('vehicles'):
            data['vehicles'] = [{
                "id": "test-123",
                "name": "TEST",
                "garageNumber": "999",
                "registrationNumber": "ST 0000 TEST",
                "latitude": 43.5100,  # Lokacija negdje kod općine
                "longitude": 16.4400
            }]
            
        return jsonify(data)
    except Exception as e:
        # Čak i ako se API skroz sruši, poslat ćemo testni bus da vidiš da aplikacija radi
        test_data = {
            "vehicles": [{
                "id": "test-123",
                "name": "ERROR-TEST",
                "garageNumber": "ERR",
                "latitude": 43.5100,
                "longitude": 16.4400
            }]
        }
        return jsonify(test_data)

if __name__ == '__main__':
    app.run(debug=True)
