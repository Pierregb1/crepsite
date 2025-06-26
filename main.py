import io, inspect, importlib, matplotlib, matplotlib.pyplot as plt
matplotlib.use("Agg")
from flask import Flask, request, send_file, abort

mods = {
    1: "modele1p",
    2: "modele2p",
    3: "modele3p",
    4: "modele4p",
    5: "modele5p",
}

app = Flask(__name__)

def run_model(mid, lat, lon, year):
    mod = importlib.import_module(mods[mid])
    func = getattr(mod, "temp_backend", None) or getattr(mod, "temp", None)
    if func is None:
        raise AttributeError(f"Aucune fonction temp trouvée dans {mods[mid]}")
    sig = inspect.signature(func)
    kw = {}
    if "lat" in sig.parameters:
        kw["lat"] = lat
    if "lon" in sig.parameters or "long" in sig.parameters:
        kw["lon"] = lon
    if "year" in sig.parameters or "annee" in sig.parameters:
        kw["year"] = year
    return func(**kw)

@app.route("/run")
def run():
    try:
        mid = int(request.args.get("model", 1))
        lat = float(request.args.get("lat", 48.85))
        lon = float(request.args.get("lon", 2.35))
        year = int(request.args.get("year", 2024))
    except (TypeError, ValueError):
        return abort(400, "Paramètres invalides")

    if mid not in mods:
        return abort(400, "Modèle inconnu")

    try:
        T = run_model(mid, lat, lon, year)
    except Exception as e:
        print("ERREUR back‑end:", e)
        return abort(500, str(e))

    fig, ax = plt.subplots(figsize=(8,3))
    ax.plot(T)
    ax.set_title(f"Modèle {mid}")
    ax.set_xlabel("Temps (h)")
    ax.set_ylabel("Température (K)")
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/")
def home():
    return "Backend CREPSITE OK – utilisez /run?model=2&lat=48.85&lon=2.35"

if __name__ == "__main__":
    app.run(debug=True, port=5000)