from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
BENALI = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}


def test_health():                            # le service repond et le modele est charge
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["modele_charge"]


def test_prediction_benali():                 # cas nominal : la valeur du TP 8
    r = client.post("/v1/predict", json=BENALI)
    assert r.status_code == 200
    assert r.json()["probabilite"] == 0.8899
    assert r.json()["version_modele"] == "1.0.0"


def test_montant_negatif():                   # validation : borne
    r = client.post("/v1/predict", json=dict(BENALI, montant=-5))
    assert r.status_code == 422


def test_champ_manquant():                    # validation : champ obligatoire
    corps = {k: v for k, v in BENALI.items() if k != "nuit"}
    assert client.post("/v1/predict", json=corps).status_code == 422


def test_champ_inconnu():                     # validation : rien de plus que le contrat
    r = client.post("/v1/predict", json=dict(BENALI, pays="MA"))
    assert r.status_code == 422
