from flask import Flask, request, send_file
import os
import uuid
from Code_complet_V1 import run_model as model1
from Code_complet_V2 import run_model as model2
from Code_complet_V3_1 import run_model as model3
from modele_4_version_api_nasa import run_model as model4
from modele_5_cmv2 import run_model as model5

app = Flask(__name__)

@app.route("/")
def home():
    return "Serveur Flask pour CREPSITE"

@app.route("/run", methods=["GET"])
def run_model():
    modele = request.args.get("modele")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    annee = request.args.get("annee", type=int)
    uid = str(uuid.uuid4())
    output_path = f"{uid}.png"

    try:
        if modele == "1":
            model1(output_path)
        elif modele == "2":
            model2(lat, lon, output_path)
        elif modele == "3":
            model3(lat, lon, output_path)
        elif modele == "4":
            model4(lat, lon, output_path)
        elif modele == "5":
            model5(lat, lon, annee, output_path)
        else:
            return "Modèle inconnu", 400
    except Exception as e:
        return f"Erreur : {e}", 500

    return send_file(output_path, mimetype='image/png')
