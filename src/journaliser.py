import json, os, mlflow
mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000'))
mlflow.set_experiment('tp8-explicabilite')
with mlflow.start_run(run_name='xai-foret-v1'):
    for f in ['shap_global.png', 'shap_benali.png', 'shap_montant.png', 'pdp_ice.png', 'monotonie.png']:
        mlflow.log_artifact('reports/' + f, artifact_path='explications')
    mlflow.log_metrics({'f1': json.load(open('reports/metrics.json'))['f1'],
                        'ecart_fausses_alertes': 0.0105}) # l'equite devient une metrique
    mlflow.log_artifact('MODEL_CARD.md')
    mlflow.set_tag('revue', 'a valider par le metier')
print('explications et fiche modele journalisees')
