import logging
import os
import secrets
import time
import uuid
from collections import defaultdict, deque

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

VERSION_MODELE = "1.0.0"
CLE_API = os.environ["API_KEY"]                       # secret lu dans l'environnement
LIMITE = int(os.getenv("LIMITE_PAR_MINUTE", "60"))    # requetes par minute et par cle
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


schema_cle = APIKeyHeader(name="X-API-Key", auto_error=False)   # cle dans l'en-tete X-API-Key


def verifier_cle(cle: str | None = Security(schema_cle)):
    if not cle or not secrets.compare_digest(cle, CLE_API):     # comparaison a temps constant
        raise HTTPException(status_code=401, detail="cle d'API absente ou invalide")
    return cle


appels = defaultdict(deque)                           # heures des derniers appels, par cle


def limiter_debit(cle: str = Depends(verifier_cle)):
    maintenant = time.time()
    fenetre = appels[cle]
    while fenetre and maintenant - fenetre[0] > 60:   # on oublie les appels > 1 minute
        fenetre.popleft()
    if len(fenetre) >= LIMITE:
        raise HTTPException(status_code=429,
                            detail="trop de requetes, reessayez dans une minute")
    fenetre.append(maintenant)


@app.get("/health")
def health():
    return {"statut": "ok", "modele_charge": modele is not None}


@app.get("/v1/model-info", dependencies=[Depends(limiter_debit)])
def model_info():
    return {"version_modele": VERSION_MODELE, "variables": list(modele.feature_names_in_)}


@app.post("/v1/predict", response_model=Prediction, dependencies=[Depends(limiter_debit)])
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
