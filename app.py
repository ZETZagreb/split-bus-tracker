from flask import Flask, render_template

app = Flask(__name__)

# Glavna ruta koja samo učitava tvoju mapu
@app.route('/')
def index():
    return render_template('index.html')

# Ova ruta nam više ne treba za podatke jer ih JS vuče direktno,
# ali je ostavljamo praznu da ne baca greške ako je negdje ostao stari link.
@app.route('/api/buses')
def get_buses():
    return {"vehicles": []}

if __name__ == '__main__':
    app.run(debug=True)
