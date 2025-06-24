import os, io
from flask import Flask, request, render_template, send_from_directory, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import modele1p, modele2p, modele3p, modele4p, modele5p

app = Flask(__name__, template_folder="templates", static_folder="static")
IMG_DIR = os.path.join(app.static_folder, "img")
os.makedirs(IMG_DIR, exist_ok=True)

def save_lineplot(data, fname, xlabel="Heures", ylabel="Température (K)"):
    plt.figure(figsize=(10,4))
    x = np.arange(len(data))
    plt.plot(x, data)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=150)
    plt.close()

def generate_zoom_plots(data, base):
    save_lineplot(data, f"{base}_annee.png")
    save_lineplot(data[:31*24], f"{base}_janvier.png")
    save_lineplot(data[:24], f"{base}_jour.png")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/img/<path:filename>")
def img(filename):
    return send_from_directory(IMG_DIR, filename)

@app.route("/modele1")
def modele1():
    temps = modele1p.temp()
    save_lineplot(temps, "modele1.png")
    return render_template("modele1.html")

@app.route("/modele<int:n>")
def modele_n(n):
    if n not in {2,3,4,5}:
        return abort(404)
    lat = float(request.args.get("lat", "48.85"))
    lon = float(request.args.get("lon", "2.35"))
    if n == 5:
        year = int(request.args.get("year", "2024"))
    func_map = {2: modele2p.temp,
                3: modele3p.temp,
                4: modele4p.temp,
                5: modele5p.temp}
    if n ==5:
        try:
            temps = func_map[n](lat, lon, year)  # expecting year param
        except TypeError:
            temps = func_map[n](lat, lon)  # fallback
    else:
        temps = func_map[n](lat, lon)
    generate_zoom_plots(temps, f"modele{n}")
    return render_template(f"modele{n}.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")