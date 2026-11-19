import joblib
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)
modele = joblib.load("models/model.pkl")              # charge une seule fois


@app.get("/health")
def health():
    return jsonify(statut="ok")


@app.post("/predict")
def predict():
    donnees = request.get_json()                      # le corps JSON de la requete
    X = pd.DataFrame([donnees])[["montant", "anciennete", "freq_24h", "nuit"]]
    p = float(modele.predict_proba(X)[0, 1])
    return jsonify(fraude=p > 0.5, probabilite=round(p, 4))
