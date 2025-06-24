import os, math
from flask import Flask, render_template, request, send_from_directory, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p, modele5p

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'), static_folder=os.path.join(BASE_DIR, 'static'))
IMG_DIR = os.path.join(app.static_folder, 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def save_line(temp, filename, xlabel='heures'):
    x = np.arange(len(temp))
    plt.figure(figsize=(10,4))
    plt.plot(x, temp)
    plt.xlabel(xlabel); plt.ylabel('Température (K)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, filename), dpi=150)
    plt.close()

def build_zoom_graphs(temp, base):
    save_line(temp, f"{base}_annee.png")
    save_line(temp[:31*24], f"{base}_janvier.png")
    save_line(temp[:24], f"{base}_jour.png")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/img/<path:fname>')
def static_img(fname):
    return send_from_directory(IMG_DIR, fname)

@app.route('/modele1')
def modele1():
    temps = modele1p.temp()
    save_line(temps, 'modele1.png', xlabel='itérations')
    return render_template('modele1.html')

@app.route('/modele<int:num>')
def modele_n(num):
    if num not in {2,3,4,5}:
        abort(404)
    lat = float(request.args.get('lat', 48.85))
    lon = float(request.args.get('lon', 2.35))
    if num == 5:
        year = int(request.args.get('year', 2024))
    func_map = {2: modele2p.temp,
                3: modele3p.temp,
                4: modele4p.temp,
                5: modele5p.temp}
    if num == 5:
        temps = func_map[num](lat, lon)  # modèle5p ne prend pas encore year, à adapter si besoin
    else:
        temps = func_map[num](lat, lon)
    build_zoom_graphs(temps, f"modele{num}")
    return render_template(f"modele{num}.html", lat=lat, lon=lon)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)