import subprocess, sys, json, yaml, joblib, mlflow, mlflow.sklearn

P = yaml.safe_load(open('params.yaml'))
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment('tp2-pipeline')

# execution PARENTE : elle regroupe tout le pipeline
with mlflow.start_run(run_name='pipeline'):

    for etape in ['preparer', 'entrainer', 'evaluer']:
        # execution ENFANT : une par etape
        with mlflow.start_run(run_name=etape, nested=True):
            # check=True : si une etape plante, tout le pipeline s'arrete
            subprocess.run([sys.executable, f'src/{etape}.py'], check=True)

    # journalisation dans le parent, apres les trois etapes
    mets = json.load(open('reports/metrics.json'))
    mlflow.log_params({**P['preparation'], **P['entrainement']})
    mlflow.log_metrics(mets)
    mlflow.log_artifact('reports/confusion.png')

    seuil = P['validation']['seuil_f1']

    # REGLE DE VALIDATION : le modele n'est enregistre que s'il passe le seuil
    if mets['f1'] >= seuil:
        mlflow.sklearn.log_model(joblib.load('models/model.pkl'), name='model',
                                 registered_model_name='fraude-tp2',
                                 skops_trusted_types=['sklearn.tree._tree.Tree'])
        print(f"modele accepte (F1 {mets['f1']} >= {seuil}) et enregistre")
    else:
        mlflow.set_tag('statut', 'refuse')   # trace visible dans MLflow
        raise SystemExit(f"modele refuse : F1 {mets['f1']} < seuil {seuil}")
