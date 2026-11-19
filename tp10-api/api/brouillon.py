# BROUILLON VOLONTAIREMENT VULNERABLE : NE JAMAIS DEPLOYER
# Chaque faille porte le numero de la bonne pratique du cours qui la corrige.
import logging

import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
journal = logging.getLogger("brouillon")
modele = joblib.load("models/model.pkl")
app = FastAPI(title="Brouillon vulnerable", debug=False)   # FAILLE 6 : erreurs detaillees
CLE_API = "admin"                                # FAILLES 2 et 3 : cle faible, ecrite dans le code


@app.post("/v1/predict")
def predict(donnees: dict, x_api_key: str = Header(None)):   # FAILLE 4 : aucun schema
    if x_api_key != CLE_API:
        raise HTTPException(status_code=401, detail="cle invalide")
    journal.info("cle=%s donnees=%s", x_api_key, donnees)   # FAILLE 8 : secret au journal
    X = pd.DataFrame([donnees])[["montant", "anciennete", "freq_24h", "nuit"]]
    p = float(modele.predict_proba(X)[0, 1])
    return {"fraude": p > 0.5, "probabilite": round(p, 4)}

# FAILLE 1 : lance en HTTP.  FAILLE 5 : aucune limite de debit.
# FAILLE 7 : l'image Docker (Dockerfile.mauvais) tourne en root.
