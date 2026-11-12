import joblib, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
df = pd.read_csv('data/transactions.csv')
rng = np.random.default_rng(1) # resultat de l'enquete, connu APRES coup
df['statut_enquete'] = np.where(rng.random(len(df)) < 0.97, df['fraude'], 1 - df['fraude'])
X, y = df.drop(columns='fraude'), df['fraude']
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
m = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42).fit(Xtr, ytr)
print('F1 avec la colonne :', round(f1_score(yte, m.predict(Xte)), 4))
r = permutation_importance(m, Xte, yte, scoring='f1', n_repeats=5, random_state=0)
print(pd.Series(r.importances_mean, index=X.columns).sort_values(ascending=False).round(3).to_string())
joblib.dump(m, 'models/model_fuite.pkl'); df.to_csv('data/transactions_fuite.csv', index=False)
print('modele et donnees avec fuite ecrits')
