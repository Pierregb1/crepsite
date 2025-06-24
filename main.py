import os, threading, io
from flask import Flask, request, render_template, send_from_directory, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p

# Modèle 5 : optionnel car dépendances manquantes
try:
    import modele5p
    MODEL5_OK = True
except Exception as e:
    print("Modèle 5 désactivé :", e)
    MODEL5_OK = False

app = Flask(__name__, template_folder="templates", static_folder="static")
IMG_DIR = os.path.join(app.static_folder, "img")
os.makedirs(IMG_DIR, exist_ok=True)

# 🔒 protection contre accès concurrents au même fichier
lock = threading.Lock()

def _save_lineplot(data, fname):
    with lock:
        plt.figure(figsize=(10, 4))
        plt.plot(np.arange(len(data)), data)
        plt.xlabel("Heures")
        plt.ylabel("Température (K)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(IMG_DIR, fname), dpi=140)
        plt.close()

def _zoom_plots(data, base):
    _save_lineplot(data, f"{base}_annee.png")
    _save_lineplot(data[:31*24], f"{base}_janvier.png")
    _save_lineplot(data[:24],     f"{base}_jour.png")

@app.route("/")
def index():
    return render_template("index.html", model5_ok=MODEL5_OK)

@app.route("/static/img/<path:filename>")
def img(filename):
    return send_from_directory(IMG_DIR, filename)

@app.route("/modele1")
def modele1():
    _save_lineplot(modele1p.temp(), "modele1.png")
    return render_template("modele1.html")

@app.route("/modele<int:n>")
def modele_n(n):
    if n not in {2, 3, 4, 5}:
        abort(404)
    if n == 5 and not MODEL5_OK:
        return "Modèle 5 indisponible (dépendances manquantes)", 503

    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    year = int(request.args.get("year", 2024))

    func = {2: modele2p.temp,
            3: modele3p.temp,
            4: modele4p.temp,
            5: modele5p.temp if MODEL5_OK else None}[n]

    try:
        data = func(lat, lon, year) if n == 5 else func(lat, lon)
    except TypeError:
        data = func(lat, lon)

    _zoom_plots(data, f"modele{n}")
    return render_template(f"modele{n}.html",
                           lat=lat, lon=lon, year=year)