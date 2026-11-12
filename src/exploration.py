import pandas as pd

df = pd.read_excel('data/brut/ref-des-medicaments-cnops-2014.xlsx')

print('Dimensions :', df.shape)
print('\nColonnes :', list(df.columns))
print('\nValeurs manquantes :\n', df.isna().sum())
print('\nCible :\n', df['PRINCEPS_GENERIQUE'].value_counts())
print('\nTaux de remboursement :\n', df['TAUX_REMBOURSEMENT'].value_counts())
print('\nPrix public (PPV) :\n', df['PPV'].describe())
print('\nMolecules differentes (DCI1) :', df['DCI1'].nunique())
