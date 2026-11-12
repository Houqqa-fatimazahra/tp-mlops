import h2o, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from h2o.automl import H2OAutoML
from sklearn.model_selection import train_test_split
h2o.init(url='http://127.0.0.1:54321') # plateforme H2O du TP 6
df = pd.read_csv('data/transactions.csv')
tr, te = train_test_split(df, test_size=0.25, random_state=42)
htr, hte = h2o.H2OFrame(tr), h2o.H2OFrame(te)
for f in (htr, hte): f['fraude'] = f['fraude'].asfactor()
aml = H2OAutoML(max_models=10, seed=42, exclude_algos=['DeepLearning'], sort_metric='AUC')
aml.train(y='fraude', training_frame=htr) # meme recherche qu'au TP 6
xgb = aml.get_best_model(algorithm='xgboost') # SHAP : modeles a base d'arbres
if xgb is None: # XGBoost absent de H2O sous Windows (constate au TP 6) : meilleur GBM
    print('XGBoost indisponible sur cette plateforme : on explique le meilleur GBM')
    xgb = aml.get_best_model(algorithm='gbm')
print('modele explique :', xgb.model_id)
print(xgb.varimp(use_pandas=True)[['variable', 'scaled_importance']].round(3).to_string(index=False))
cas = h2o.H2OFrame(pd.DataFrame([{'montant': 1800.0, 'anciennete': 30, 'freq_24h': 4, 'nuit': 1}]))
contrib = xgb.predict_contributions(cas).as_data_frame().round(3) # SHAP, en log-cote
print('Mme Benali (log-cote) :', contrib.iloc[0].to_dict())
print('P(fraude) =', round(xgb.predict(cas).as_data_frame()['p1'][0], 3))
import shap # graphique SHAP depuis les contributions H2O
c = xgb.predict_contributions(hte.drop('fraude')).as_data_frame()
X = te.drop(columns='fraude')
e = shap.Explanation(values=c[X.columns].values, base_values=c['BiasTerm'].values, data=X.values,
                     feature_names=list(X.columns))
shap.plots.beeswarm(e, show=False); plt.savefig('reports/h2o_shap.png', dpi=110, bbox_inches='tight')
print('graphique ecrit')
