"""
Back-end CREPSITE – appelle chaque modèle avec
les bons paramètres puis renvoie un PNG.
Compatible Render (Flask + Gunicorn).
"""
import io, os, importlib
from flask import Flask, request, send_file, abort
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────
# import des modèles
import modele1p, modele2p, modele3p, modele4p, modele5p
# ─────────────────────────────────────────────────────────────

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
#  WRAPPERS pour transformer (lat, lon, year)
#  en arguments attendus par chaque temp() original
# ─────────────────────────────────────────────────────────────
def run_model1():
    return modele1p.temp()                       # aucune entrée

def run_model2(lat, lon):
    P = modele2p.annee(modele2p.chaque_jour(lat, lon))
    return modele2p.temp(P)

def run_model3(lat, lon):
    P = modele3p.annee(modele3p.chaque_jour(lat, lon))
    return modele3p.temp(P)

def run_model4(lat, lon, year):
    P   = modele4p.annee(modele4p.chaque_jour(lat, lon))
    v   = modele4p.get_daily_wind_speed(lat, lon,
                                        f"{year}0101", f"{year}1231")
    Alb = modele4p.get_mean_albedo(lat, lon)
    return modele4p.temp(P, v, Alb)

def run_model5(lat, lon, year):
    return modele5p.temp(lat=lat, long=lon)      # modèle 5 gère l’année lui-même
# ─────────────────────────────────────────────────────────────

DISPATCH = {
    1: run_model1,
    2: run_model2,
    3: run_model3,
    4: run_model4,
    5: run_model5
}

@app.route("/")
def home():
    return ("Backend CREPSITE opérationnel – "
            "utilise /run?model=2&lat=48.85&lon=2.35&year=2024")

@app.route("/run")
def run():
    try:
        model = int(request.args.get("model", 1))
        if model not in DISPATCH:
            return abort(400, "Modèle inconnu")
        lat  = float(request.args.get("lat", 48.85))
        lon  = float(request.args.get("lon", 2.35))
        year = int(request.args.get("year", 2024))

        # Appel du wrapper approprié
        if model == 1:
            T = run_model1()
        elif model == 2:
            T = run_model2(lat, lon)
        elif model == 3:
            T = run_model3(lat, lon)
        elif model == 4:
            T = run_model4(lat, lon, year)
        elif model == 5:
            T = run_model5(lat, lon, year)

    except Exception as e:
        # journalise l’erreur côté serveur
        print("[ERREUR]", e)
        return abort(500, "Erreur interne : "+str(e))

    # ───── Génération du graphique PNG ─────
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(T)
    ax.set_title(f"Modèle {model}")
    ax.set_xlabel("Temps (h)")
    ax.set_ylabel("Température (K)")
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
