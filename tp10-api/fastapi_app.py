import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API de detection de fraude")
modele = joblib.load("models/model.pkl")              # charge une seule fois


class Transaction(BaseModel):                         # le schema d'entree
    montant: float
    anciennete: int
    freq_24h: int
    nuit: int


@app.get("/health")
def health():
    return {"statut": "ok"}


@app.post("/predict")
def predict(t: Transaction):
    X = pd.DataFrame([t.model_dump()])
    p = float(modele.predict_proba(X)[0, 1])
    return {"fraude": p > 0.5, "probabilite": round(p, 4)}
