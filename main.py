import os
from flask import Flask, request, render_template, send_from_directory, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p
try:
    import modele5p
    MODEL5_OK = True
except Exception as e:
    print("Modèle 5 désactivé :", e)
    MODEL5_OK = False

app = Flask(__name__, template_folder=".", static_folder="static")
IMG_DIR = os.path.join(app.static_folder, "img")
os.makedirs(IMG_DIR, exist_ok=True)

def save_plot(data, name):
    plt.figure(figsize=(10,4))
    plt.plot(np.arange(len(data)), data)
    plt.xlabel("Temps (h)")
    plt.ylabel("Température (K)")
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(os.path.join(IMG_DIR, name), dpi=140)
    plt.close()

def zoom_plots(data, base):
    save_plot(data, f"{base}_annee.png")
    save_plot(data[:31*24], f"{base}_janvier.png")
    save_plot(data[:24], f"{base}_jour.png")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/img/<path:f>")
def img(f):
    return send_from_directory(IMG_DIR, f)

@app.route("/modele1")
def m1():
    save_plot(modele1p.temp(), "modele1.png")
    return render_template("modele1.html")

@app.route("/modele<int:n>")
def mN(n):
    if n not in {2,3,4,5}: abort(404)
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    year = int(request.args.get("year", 2024))
    if n==2:
        data = modele2p.temp(lat, lon)
    elif n==3:
        data = modele3p.temp(lat, lon)
    elif n==4:
        data = modele4p.temp(lat, lon)
    elif n==5 and MODEL5_OK:
        try:
            data = modele5p.temp(lat, lon, year)
        except TypeError:
            data = modele5p.temp(lat, lon)
    else:
        return "Modèle 5 indisponible", 503
    zoom_plots(data, f"modele{n}")
    return render_template(f"modele{n}.html", lat=lat, lon=lon, year=year)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")