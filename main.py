
import importlib, inspect, io, uuid, os
from flask import Flask, request, send_file, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Dynamic import map
models = {
    1: ("modele1p", None),
    2: ("modele2p", None),
    3: ("modele3p", None),
    4: ("modele4p", None),
    5: ("modele5p", None),
}

app = Flask(__name__)

def call_temp(mod, lat=None, lon=None, year=None):
    if not hasattr(mod, "temp"):
        # fallback: search for any function starting with temp
        func = getattr(mod, "run_model", None) or getattr(mod, "run", None)
    else:
        func = mod.temp
    if func is None:
        raise AttributeError("Pas de fonction temp trouvée")
    sig = inspect.signature(func)
    params = sig.parameters
    args = []
    if "lat" in params or "latitude" in params or len(params)==1 and list(params)[0]!="self":
        if lat is not None:
            args.append(lat)
    if ("lon" in params or "long" in params):
        if lon is not None:
            args.append(lon)
    if "year" in params or "annee" in params:
        if year is not None:
            args.append(year)
    return func(*args)

@app.route("/")
def index():
    return "Backend CREPSITE - utilisez /run?model=2&lat=48.85&lon=2.35 etc."

@app.route("/run")
def run():
    try:
        m = int(request.args.get("model") or request.args.get("modele"))
    except:
        return abort(400, "Paramètre model manquant")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    year = request.args.get("year", type=int) or request.args.get("annee", type=int)
    if m not in models:
        return abort(400, "Modèle inexistant")
    mod_name, mod_obj = models[m]
    if mod_obj is None:
        mod_obj = importlib.import_module(mod_name)
        models[m] = (mod_name, mod_obj)
    try:
        T = call_temp(mod_obj, lat, lon, year)
    except Exception as e:
        return abort(500, f"Erreur appel modèle: {e}")
    # generate plot
    fig, ax = plt.subplots(figsize=(8,3))
    ax.plot(T)
    ax.set_xlabel("Temps (h)")
    ax.set_ylabel("Température (K)")
    ax.set_title(f"Modèle {m}")
    img = io.BytesIO()
    fig.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
