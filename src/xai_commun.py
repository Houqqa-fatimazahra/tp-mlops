import joblib, pandas as pd
from sklearn.model_selection import train_test_split
m = joblib.load('models/model.pkl') # foret du TP 2/3 (300 arbres)
df = pd.read_csv('data/transactions.csv')
X, y = df.drop(columns='fraude'), df['fraude']
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42) # meme decoupage
CAS = pd.DataFrame([{'montant': 1800.0, 'anciennete': 30, 'freq_24h': 4, 'nuit': 1}]) # Mme Benali
