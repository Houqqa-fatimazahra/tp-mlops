import os
import pandas as pd, joblib, mlflow, mlflow.sklearn
from flaml import AutoML
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
df = pd.read_csv('data/transactions.csv')
X, y = df.drop(columns='fraude'), df['fraude']
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
a = AutoML()
a.fit(Xtr, ytr, task='classification', metric='f1', time_budget=-1,
      max_iter=25, seed=42, verbose=0)                                # budget en essais : reproductible
f1 = f1_score(yte, a.predict(Xte))
print('modele retenu :', a.best_estimator, '| F1 test =', round(f1, 4))
modele = a.model.estimator                                            # le modele sous-jacent (LightGBM, XGBoost...)
joblib.dump(modele, 'models/model_flaml.pkl')
mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000'))
mlflow.set_experiment('tp6-automl-deploiement')
with mlflow.start_run(run_name='flaml-25-essais'):
    mlflow.log_params({'outil': 'flaml', 'max_iter': 25, 'modele': a.best_estimator})
    mlflow.log_metric('f1', f1)
    mlflow.sklearn.log_model(modele, name='model', input_example=Xte[:3],
                             serialization_format='cloudpickle',      # skops refuse LightGBM
                             registered_model_name='fraude-flaml')
