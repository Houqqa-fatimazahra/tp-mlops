import sys, json, subprocess, mlflow, mlflow.sklearn, pandas as pd
import matplotlib; matplotlib.use('Agg')          # pas de fenetre graphique : on enregistre juste l'image
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (f1_score, precision_score, recall_score,
                             roc_auc_score, ConfusionMatrixDisplay)

# Les reglages viennent de la ligne de commande : python src/train_complet.py 200 8
# sys.argv[1] = nombre d'arbres, sys.argv[2] = profondeur maximale
n_estimators = int(sys.argv[1]); max_depth = int(sys.argv[2])

# On se connecte au serveur MLflow et on range les executions dans l'experience tp3-registre
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment('tp3-registre')

# Chargement des donnees et decoupage train/test (meme graine 42 qu'aux TP 1 et 2)
df = pd.read_csv('data/transactions.csv')
X, y = df.drop(columns='fraude'), df['fraude']
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

# Tout ce qui est dans ce bloc "with" est enregistre dans UNE execution MLflow
with mlflow.start_run(run_name=f'rf-{n_estimators}-{max_depth}'):

    # Entrainement de la foret aleatoire, puis predictions sur le jeu de test
    m = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                               random_state=42).fit(Xtr, ytr)
    pred = m.predict(Xte)                 # classe predite : 0 ou 1
    proba = m.predict_proba(Xte)[:, 1]    # probabilite de fraude (sert au calcul de l'AUC)

    # ESSENTIEL 1 : les parametres et les metriques
    mlflow.log_params({'n_estimators': n_estimators, 'max_depth': max_depth})
    mlflow.log_metrics({'f1': f1_score(yte, pred),
                        'precision': precision_score(yte, pred),
                        'recall': recall_score(yte, pred),
                        'roc_auc': roc_auc_score(yte, proba)})

    # ESSENTIEL 2 : la tracabilite. Le commit Git dit QUELLE version du code a produit ce modele
    commit = subprocess.getoutput('git rev-parse --short HEAD')
    mlflow.set_tags({'auteur': 'Fatima Zahra Houqqa', 'commit': commit,
                     'jeu_de_donnees': 'transactions v1'})

    # ESSENTIEL 3 : artefact 1 = la matrice de confusion (image)
    ConfusionMatrixDisplay.from_predictions(yte, pred)
    plt.savefig('reports/confusion.png', dpi=110, bbox_inches='tight')
    mlflow.log_artifact('reports/confusion.png')

    # ESSENTIEL 4 : artefact 2 = l'importance de chaque variable (fichier JSON)
    imp = dict(zip(X.columns, m.feature_importances_.round(4)))
    json.dump(imp, open('reports/importances.json', 'w'), indent=2)
    mlflow.log_artifact('reports/importances.json')

    # ESSENTIEL 5 : le modele packag?. input_example permet a MLflow de deduire la SIGNATURE
    # (nom et type de chaque colonne attendue). skops_trusted_types : meme raison qu'au TP 2.
    mlflow.sklearn.log_model(m, name='model', input_example=Xte[:3],
                             skops_trusted_types=['sklearn.tree._tree.Tree'])

    print('F1 =', round(f1_score(yte, pred), 4))
