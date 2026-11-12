import socket
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

VERSION = "1.0"                                      # version du service
HOTE = socket.gethostname()                          # nom du conteneur qui repond
modele = joblib.load("models/model.pkl")             # charge une seule fois, au demarrage

app = FastAPI(title="API de detection de fraude")


class Transaction(BaseModel):                        # les 4 entrees attendues
    montant: float
    anciennete: int
    freq_24h: int
    nuit: int


@app.get("/health")
def health():                                        # le service est-il pret ?
    return {"statut": "ok", "version": VERSION, "hote": HOTE}


@app.post("/predict")
def predict(t: Transaction):
    X = pd.DataFrame([t.model_dump()])
    p = float(modele.predict_proba(X)[0, 1])
    return {"fraude": p > 0.5, "probabilite": round(p, 4), "version": VERSION, "hote": HOTE}
