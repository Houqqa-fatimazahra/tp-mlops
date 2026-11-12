# Fiche modele - detection-fraude (foret du TP 3)
## Usage prevu
Signaler une transaction pour verification humaine. Le client recoit une raison et un contrefactuel.
## Usages exclus
Blocage definitif sans revue humaine (loi 09-08, art. 11). Octroi de credit.
## Donnees
transactions.csv, 5 000 lignes, 11,4 % de fraudes, version DVC du TP 4.
## Performances (test, 1 250 transactions)
F1 0.8636 - precision 0.8769 - rappel 0.8507.
## Explicabilite
SHAP (TreeExplainer) par decision ; graphiques globaux journalises dans MLflow.
Variables les plus influentes : montant, puis anciennete, nuit, freq_24h.
## Equite (groupe A/B fictif du TP)
Fausses alertes : A 1,08 % ; B 2,13 %. Variable proxy identifiee : anciennete.
## Alternatives interpretables mesurees
Logistique + log(montant) : F1 0.8593. EBM : F1 0.8538.
## Limites connues
- Donnees synthetiques (5 000 lignes, 4 variables) : le modele n'a jamais vu de vraies transactions ; ses performances reelles restent a mesurer.
- Environ 15 % des fraudes ne sont pas detectees (rappel 0,85) et 12 % des alertes sont fausses (precision 0,88) : la revue humaine est indispensable.
- Le montant agit par ordre de grandeur et domine l'importance (59 % de la permutation) : un changement d'echelle des montants (inflation, devise, version v2 du TP 4 avec montants x 1,3) deplace tous les seuils ; il faut surveiller la derive et reentrainer.
- Sans contrainte, le risque remonte vers 45 mois d'anciennete (artefact des donnees, non plausible metier) ; la foret n'impose aucune monotonie.
- L'anciennete sert de variable proxy : les clients recents (groupe B fictif) subissent deux fois plus de fausses alertes ; l'ecart doit rester sous surveillance (metrique ecart_fausses_alertes dans MLflow).
- LIME est instable sur l'anciennete et la frequence (changement de signe selon la graine) : seules les explications SHAP, exactes, sont communiquees au client, et seulement les causes stables (montant, nuit).
- Toute variable connue seulement apres la decision (ex. statut_enquete) est interdite : le garde-fou Prefect de l'etape 14 refuse un tel modele.
## Revue
Auteurs : fatima zahra houqqa - revue prevue dans 6 mois (mai 2027).
