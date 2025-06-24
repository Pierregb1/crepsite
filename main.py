import os
from flask import Flask, request, render_template, send_from_directory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p, modele5p

app = Flask(__name__, static_folder="static", template_folder="templates")

IMG_DIR = os.path.join(app.static_folder, "img")
os.makedirs(IMG_DIR, exist_ok=True)

def _save_graph(y, fname, xlabel="Heures"):
    plt.figure(figsize=(10,4))
    x = np.arange(len(y))
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel("Température (K)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=150)
    plt.close()

def _build_graphs(temp, base):
    _save_graph(temp, f"{base}_annee.png")
    _save_graph(temp[:31*24], f"{base}_janvier.png")
    _save_graph(temp[:24], f"{base}_jour.png")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/img/<path:filename>")
def img(filename):
    return send_from_directory(IMG_DIR, filename)

@app.route("/modele1")
def modele1():
    temps = modele1p.temp()
    _save_graph(temps, "modele1.png")
    return render_template("modele1.html")

@app.route("/modele<int:n>")
def modele_n(n):
    if n not in {2,3,4,5}:
        return "Modèle inconnu", 404
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    func_map = {2: modele2p.temp,
                3: modele3p.temp,
                4: modele4p.temp,
                5: modele5p.temp}
    temps = func_map[n](lat, lon)
    _build_graphs(temps, f"modele{n}")
    return render_template(f"modele{n}.html")

if __name__ == "__main__":
    app.run(debug=True)