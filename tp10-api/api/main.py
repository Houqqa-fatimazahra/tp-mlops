import logging
import time
import uuid

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

VERSION_MODELE = "1.0.0"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
journal = logging.getLogger("fraude-api")
modele = joblib.load("models/model.pkl")              # charge une seule fois, au demarrage
app = FastAPI(title="API de detection de fraude", version=VERSION_MODELE)


class Transaction(BaseModel):                         # ce que l'API accepte
    model_config = ConfigDict(extra="forbid")         # champ inconnu = requete refusee
    montant: float = Field(gt=0, le=1_000_000, description="montant en MAD")
    anciennete: int = Field(ge=0, le=600, description="anciennete du compte, en mois")
    freq_24h: int = Field(ge=0, le=500, description="operations sur les 24 dernieres heures")
    nuit: int = Field(ge=0, le=1, description="1 si l'operation a lieu la nuit")


class Prediction(BaseModel):                          # ce que l'API renvoie
    fraude: bool
    probabilite: float
    version_modele: str
    id_requete: str


@app.get("/health")
def health():
    return {"statut": "ok", "modele_charge": modele is not None}


@app.get("/v1/model-info")
def model_info():
    return {"version_modele": VERSION_MODELE, "variables": list(modele.feature_names_in_)}


@app.post("/v1/predict", response_model=Prediction)
def predict(t: Transaction):
    debut = time.perf_counter()
    X = pd.DataFrame([t.model_dump()])
    p = float(modele.predict_proba(X)[0, 1])
    rid = uuid.uuid4().hex[:8]
    duree = (time.perf_counter() - debut) * 1000
    journal.info("prediction id=%s version=%s proba=%.4f duree_ms=%.1f",
                 rid, VERSION_MODELE, p, duree)       # aucune donnee personnelle
    return Prediction(fraude=p > 0.5, probabilite=round(p, 4),
                      version_modele=VERSION_MODELE, id_requete=rid)
