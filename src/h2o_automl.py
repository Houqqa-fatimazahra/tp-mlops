import os
import h2o, pandas as pd, mlflow, mlflow.h2o
from h2o.automl import H2OAutoML
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
h2o.init(url='http://127.0.0.1:54321')                                # la plateforme du terminal 1
df = pd.read_csv('data/transactions.csv')
tr, te = train_test_split(df, test_size=0.25, random_state=42)        # decoupage des TP 1 a 5
htr = h2o.H2OFrame(tr, destination_frame='fraude_train')
hte = h2o.H2OFrame(te, destination_frame='fraude_test')
for f in (htr, hte):
    f['fraude'] = f['fraude'].asfactor()                              # classification, pas regression
aml = H2OAutoML(max_models=10, seed=42,                               # budget en modeles : reproductible
                exclude_algos=['DeepLearning'],                       # non reproductible par defaut
                sort_metric='AUC')
aml.train(y='fraude', training_frame=htr)
print('projet AutoML :', aml.project_name)                            # pour le retrouver dans H2O Flow
lb = aml.leaderboard.as_data_frame()
print(lb[['model_id', 'auc', 'logloss']].head(8).to_string(index=False))
pred = aml.leader.predict(hte).as_data_frame()['predict'].astype(int)
f1 = f1_score(te['fraude'], pred)
print('modele retenu :', aml.leader.model_id, '| F1 test =', round(f1, 4))
mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000'))
mlflow.set_experiment('tp6-automl-deploiement')
with mlflow.start_run(run_name='h2o-automl-10-modeles'):
    mlflow.log_params({'outil': 'h2o', 'max_models': 10, 'modele': aml.leader.model_id})
    mlflow.log_metric('f1', f1)
    mlflow.h2o.log_model(aml.leader, name='model', input_example=te.drop(columns='fraude').head(3),
                         registered_model_name='fraude-h2o')
