from flask import Flask, request, send_file, render_template_string
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from modele1p import temp as model1
from modele2p import temp as model2
from modele3p import temp as model3
from modele4p import temp as model4
from modele5p import temp as model5

app = Flask(__name__)
IMG_FOLDER = "static/img"

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/modele<int:model_id>", methods=["GET", "POST"])
def run_model(model_id):
    lat = request.form.get("lat", type=float, default=48.85)
    lon = request.form.get("lon", type=float, default=2.35)
    year = request.form.get("year", type=int, default=2020)

    figpaths = []
    if model_id == 1:
        T = model1()
        fig, ax = plt.subplots()
        ax.plot(T)
        ax.set_title("Modèle 1")
        path = f"{IMG_FOLDER}/modele1.png"
        fig.savefig(path)
        plt.close(fig)
        figpaths = [path]
    elif model_id in [2, 3, 4, 5]:
        model_func = [None, None, model2, model3, model4, model5][model_id]
        T_full = model_func(lat, lon)
        if model_id == 5:
            T_full = model_func(lat, lon, year)
        zooms = {
            "an": slice(None),
            "jan": slice(0, 31 * 24),
            "jour": slice(0, 24)
        }
        figpaths = []
        for zname, zrange in zooms.items():
            fig, ax = plt.subplots()
            ax.plot(T_full[zrange])
            ax.set_title(f"Modèle {model_id} - Zoom {zname}")
            path = f"{IMG_FOLDER}/modele{model_id}_{zname}.png"
            fig.savefig(path)
            figpaths.append(path)
            plt.close(fig)

    html = open(f"modele{model_id}.html", encoding="utf-8").read()
    # Inject paths in the HTML
    for i, tag in enumerate(["an", "jan", "jour"]):
        if i < len(figpaths):
            html = html.replace(f"{{{{img_{tag}}}}}", figpaths[i])
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)