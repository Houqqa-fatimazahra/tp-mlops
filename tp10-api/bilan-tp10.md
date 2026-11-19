# TP 10 - Bilan

## Mesures (etapes 6 et 7)

| Mesure                          | req/s | mediane    | p95        |
|---------------------------------|-------|------------|------------|
| Modele charge une seule fois    | 17    | 55.9 ms    | 77.0 ms    |
| Modele recharge a chaque appel  | 5     | 199.8 ms   | 240.0 ms   |
| 1 processus, 20 clients         | 17    | 1193.7 ms  | 1448.0 ms  |
| 2 processus, 20 clients         | 32    | 613.7 ms   | 1021.9 ms  |

Rapport des medianes (etape 6) : 199.8 / 55.9 = 3.6 fois plus lent quand le modele est recharge.
Etape 7 : 2 processus = 1.9 fois plus de debit, mediane divisee par 1.9.
(Mesures faites sur http://127.0.0.1 : sous Windows, "localhost" essaie d'abord IPv6 et ajoute
environ 2 s par nouvelle connexion, ce qui fausse la mesure.)

## Securite (etapes 9 a 16)

| Pratique             | Attaque            | Brouillon                                    | Version securisee                              |
|----------------------|--------------------|----------------------------------------------|------------------------------------------------|
| 1 HTTPS              | espion             | cle `X-API-Key: admin` et dossier lus en clair | octets chiffres (TLS), reponse 0.8899 quand meme |
| 2 Cle d'API          | dictionnaire       | cle trouvee en 11 essais (`admin`)           | 14 essais, 14 x 401                            |
| 3 Secrets            | docker history     | `ENV API_KEY=k3y-ex3mple-2026` + printenv    | aucune ligne, printenv vide (code 1)           |
| 4 Validation         | entrees piegees    | 3 x 200 absurdes + 3 x 500                   | 6 x 422 avant le modele                        |
| 5 Limite de debit    | 100 requetes       | 100 x 200 en 7.3 s                           | 60 x 200 + 40 x 429 en 6.2 s                   |
| 6 Erreurs discretes  | montant = abc      | 500, 5182 caracteres (chemin, ligne, libs)   | 422, 151 caracteres ; brouillon corrige : 21   |
| 7 Sans privileges    | touch dans models/ | `root`, modele_pirate.pkl cree               | `app`, Permission denied                       |
| 8 Journal            | lecture des logs   | `cle=admin donnees={...}` a chaque appel     | id, version, proba, duree ; 401/422/429 visibles |
