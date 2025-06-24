from flask import Flask, request, send_from_directory
import matplotlib.pyplot as plt
import numpy as np
import os

from modele1p import temp as model1
from modele2p import temp as model2
from modele3p import temp as model3
from modele4p import temp as model4
from modele5p import temp as model5

app = Flask(__name__)

@app.route("/")
def index():
    links = "".join([f"<li><a href='/modele{i}'>Modèle {i}</a></li>" for i in range(1,6)])
    return f"<h1>Choisissez un modèle</h1><ul>{links}</ul>"

def save_and_plot(model_num, T_values, title):
    plt.figure()
    plt.plot(T_values)
    plt.title(title)
    plt.xlabel("Temps (heures)")
    plt.ylabel("Température (°C)")
    path = f"static/images/modele{model_num}.png"
    plt.savefig(path)
    plt.close()

@app.route("/modele1", methods=["GET", "POST"])
def modele1_route():
    if request.method == "POST":
        T = model1()
        save_and_plot(1, T, "Modèle 1")
    return send_from_directory(".", "modele1.html")

@app.route("/modele2", methods=["GET", "POST"])
def modele2_route():
    if request.method == "POST":
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        T = model2(lat, lon)
        save_and_plot(2, T, "Modèle 2")
    return send_from_directory(".", "modele2.html")

@app.route("/modele3", methods=["GET", "POST"])
def modele3_route():
    if request.method == "POST":
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        T = model3(lat, lon)
        save_and_plot(3, T, "Modèle 3")
    return send_from_directory(".", "modele3.html")

@app.route("/modele4", methods=["GET", "POST"])
def modele4_route():
    if request.method == "POST":
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        T = model4(lat, lon)
        save_and_plot(4, T, "Modèle 4")
    return send_from_directory(".", "modele4.html")

@app.route("/modele5", methods=["GET", "POST"])
def modele5_route():
    if request.method == "POST":
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        annee = int(request.form["annee"])
        T = model5(lat, lon, annee)
        save_and_plot(5, T, "Modèle 5")
    return send_from_directory(".", "modele5.html")

if __name__ == "__main__":
    app.run(debug=True)
