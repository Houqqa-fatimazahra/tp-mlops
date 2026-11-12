import sys
import time
import pandas as pd
import mlflow

from flaml import AutoML
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score


# récupérer le budget depuis la commande
budget = int(sys.argv[1]) if len(sys.argv) > 1 else 60


# charger les données
df = pd.read_csv("data/transactions.csv")


# séparer les variables et la cible
X = df.drop(columns="fraude")
y = df["fraude"]


# séparation apprentissage / test
Xtr, Xte, ytr, yte = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42
)


# démarrage du chronomètre
t0 = time.time()


# création du modèle AutoML
automl = AutoML()


# recherche automatique
automl.fit(
    Xtr,
    ytr,
    task="classification",
    metric="f1",
    time_budget=budget,
    verbose=0
)


# durée
duree = round(time.time() - t0, 1)


# prédiction
pred = automl.predict(Xte)


# calcul F1
f1 = f1_score(yte, pred)


# afficher le résultat
print(
    "budget", budget,
    "s | modele", automl.best_estimator,
    "| F1", round(f1, 4)
)

print("config :", automl.best_config)


# connexion MLflow
mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)

mlflow.set_experiment(
    "tp5-automl"
)


# sauvegarder l'expérience dans MLflow
with mlflow.start_run(
    run_name=f"flaml-{budget}s"
):

    mlflow.log_params(
        {
            "outil": "flaml",
            "budget_s": budget,
            "modele_retenu": automl.best_estimator
        }
    )

    mlflow.log_metrics(
        {
            "f1": f1,
            "duree_s": duree
        }
    )