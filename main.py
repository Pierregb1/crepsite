import os
from flask import Flask, request, render_template_string, send_from_directory, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p
try:
    import modele5p
    MODEL5_OK = True
except Exception as e:
    print("Modèle 5 indisponible :", e)
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
    return render_template_string(open("index.html").read())

@app.route("/static/img/<path:f>")
def img(f):
    return send_from_directory(IMG_DIR, f)

@app.route("/modele1")
def m1():
    save_plot(modele1p.temp(), "modele1.png")
    return render_template_string(open("modele1.html").read())

@app.route("/modele2")
def m2():
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    data = modele2p.temp(lat, lon)
    zoom_plots(data, "modele2")
    return render_template_string(open("modele2.html").read())

@app.route("/modele3")
def m3():
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    data = modele3p.temp(lat, lon)
    zoom_plots(data, "modele3")
    return render_template_string(open("modele3.html").read())

@app.route("/modele4")
def m4():
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    data = modele4p.temp(lat, lon)
    zoom_plots(data, "modele4")
    return render_template_string(open("modele4.html").read())

@app.route("/modele5")
def m5():
    if not MODEL5_OK:
        return "Modèle 5 indisponible", 503
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    year = int(request.args.get("year", 2024))
    try:
        data = modele5p.temp(lat, lon, year)
    except TypeError:
        data = modele5p.temp(lat, lon)
    zoom_plots(data, "modele5")
    return render_template_string(open("modele5.html").read())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")