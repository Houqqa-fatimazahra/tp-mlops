import yaml, pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier

# lit les reglages d'entrainement depuis params.yaml
p = yaml.safe_load(open('params.yaml'))['entrainement']

# ESSENTIEL : entree = sortie de l'etape 2, jamais le fichier brut
tr = pd.read_csv('data/prepare/train.csv')
X, y = tr.drop(columns='fraude'), tr['fraude']

m = RandomForestClassifier(n_estimators=p['n_estimators'],
                           max_depth=p['max_depth'],
                           random_state=42).fit(X, y)

# sortie : l'artefact modele
joblib.dump(m, 'models/model.pkl')
print('entrainement : modele ecrit dans models/model.pkl')
