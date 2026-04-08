from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses')
def get_buses():
    try:
        # Pokušaj dohvatiti prave podatke
        response = requests.get("https://najava.promet-split.hr/api/get-all-vehicles", timeout=5)
        data = response.json()
    except:
        data = {"vehicles": []}

    # FORSIRAMO TESTNI BUS (uvijek će biti tu, čak i ako API ne radi)
    test_bus = {
        "id": "test-999",
        "name": "999",
        "garageNumber": "TEST",
        "registrationNumber": "ST-MOD-AI",
        "latitude": 43.5147,
        "longitude": 16.4435
    }
    
    # Ako nema pravih buseva, stvori listu s ovim jednim
    if not data.get('vehicles'):
        data['vehicles'] = [test_bus]
    else:
        # Ako ima pravih, samo mu dodaj i ovaj naš testni na vrh
        data['vehicles'].append(test_bus)
        
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
