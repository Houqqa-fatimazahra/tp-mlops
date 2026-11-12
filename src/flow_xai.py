import sys, joblib, pandas as pd
from prefect import flow, task, get_run_logger
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
AUTORISEES = {'montant', 'anciennete', 'freq_24h', 'nuit'} # connues au moment de la decision
@task
def expliquer(modele, donnees):
    m, df = joblib.load(modele), pd.read_csv(donnees)
    X, y = df.drop(columns='fraude'), df['fraude']
    _, Xte, _, yte = train_test_split(X, y, test_size=0.25, random_state=42)
    r = permutation_importance(m, Xte, yte, scoring='f1', n_repeats=5, random_state=0)
    return pd.Series(r.importances_mean, index=X.columns).sort_values(ascending=False)
@task
def controler(imp):
    log = get_run_logger()
    log.info('importances : ' + ', '.join(f'{k} {v:.3f}' for k, v in imp.items()))
    interdites = set(imp.index) - AUTORISEES
    if interdites: # garde-fou 1 : variable inconnue a la decision
        raise ValueError(f'variables non autorisees : {sorted(interdites)}')
    part = imp.iloc[0] / imp.clip(lower=0).sum()
    if part > 0.6: # garde-fou 2 : une variable ecrase les autres
        raise ValueError(f'{imp.index[0]} represente {part:.0%} de l importance')
    log.info(f'explications plausibles : {imp.index[0]} en tete ({part:.0%})')
@flow(name='controle-explicabilite')
def controle(modele='models/model.pkl', donnees='data/transactions.csv'):
    controler(expliquer(modele, donnees))
if __name__ == '__main__':
    controle(*sys.argv[1:])
