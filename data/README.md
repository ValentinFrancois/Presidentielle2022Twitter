# Infos

# Candidats:
Voir `candidats.csvs`

/!\ Emmanuel Macron a deux comptes (le deuxième: `@avecvous`) car on lui a 
interdit en mars d'utiliser son compte de président pour la campagne. Comme il 
avait commencé à utiliser sur son compte `@EmmanuelMacron`, il y a des 
tweets de campagne sur les deux comptes donc le mieux est probablement de 
concaténer les deux CSVs (fournis séparément).

### Colonnes probablement les plus utiles:
- `datetime`: j'ai extrait tous les tweets disponibles avec la version 
  gratuite de l'API Twitter (~ les 3200 derniers tweets). Beaucoup 
  remontent à avant le début de la campagne présidentielle 2022, il faut 
  donc filtrer les tweets à partir du 1er janvier 2022 ou n'importe quelle 
  autre date qui vous semble pertinente.
- `own_text`: en gros le texte que le/la candidat/e a vraiment écrit 
  (excluant par exemple le texte des retweets ou des tweets cités)
- `cleaned_text`: la même chose mais nettoyée pour ne conserver que les mots 
  d'intérêt (pas de stop words, pas de hashtags qui ne sont pas des noms 
  communs, pas de usernames, pas d'emojis etc.). Utile pour faire des 
  nuages de mots par exemple (penser à lemmizer les mots avant).


### Détails:
- `username`: username de/de la candidat/e
- `id`: ID unique du tweet (dans l'API tweeter)
- `datetime`: timestamp du tweet
- `type`: 
  - `'normal'`: tweet de base
  - `'retweet'`: retweet (pas de texte ajouté)
  - `'quoting'`: tweet cité, incorpore un autre tweet et ajoute du text ou du 
    multimedia (= retweet + contenu ajouté)
  - `'reply'`: tweet en réponse à un autre tweet
  - théoriquement un tweet peut à la fois une réponse ET un tweet cité ; 
    dans ce cas il sera classé ici en `'reply'`
- `text`: texte brut du tweet extrait tel quel via l'API tweeter ; en 
  particulier, contient les liens http des tweets référencés (tweets cités 
  et retweets) et les @username des personnes citées dans les réponses
- `has_referenced_tweet`: `True`/`False` ; `True` si le tweet est du type 
  `retweet`/`quoting`/`reply`, `False` si le tweet est du type `normal`
- `referenced_tweet_found`: `True`/`False` ; parfois le tweet référencé a 
  été supprimé entre temps, dans ce cas cette colonne sera `False`
- `referenced_tweet_id` ID unique du tweet référencé
- `referenced_tweet_text`: texte brut du tweet référencé
- `referenced_tweet_datetime`: timestamp du tweet référencé
- `referenced_tweet_author_id`: ID unique de l'auteur/trice du tweet référencé
- `referenced_tweet_author_name`: Nom choisi par l'auteur/trice du tweet 
  référencé
- `referenced_tweet_author_username`: username de l'auteur/trice du tweet référencé
- `own_text`: texte du tweet postprocessed pour enlever les parties du 
  texte brut qui n'ont pas été écrites par l'auteur/trice (par exemple les 
  usernames des personnes à qui iel répond ou les liens http vers les 
  tweets cités). Pour les tweets de type `retweet`, cette colonne est 
  forcément vide. Pour les tweets de type `quoting`, elle peut être vide 
  mais devrait contenir du texte la plupart du temps.
  Pour
- `cleaned_text`: postprocessing de `own_text` qui:
  - supprime emojis
  - supprime la ponctuation
  - supprime les guillemets
  - supprime les hashtags (sauf si c'est un nom commum, exemple: 
    `'#présidentielle'` -> `'présidentielle'` mais `'#Mélenchon'` -> `''`)
  - supprime les @username
  - supprime les URL
  - supprime les parenthèses, les crochets
  - remplace les majuscules par des minuscules
  - supprime les stop words ('et', 'le', 'ou' etc.)
  - ce traitement est imparfait et je n'ai pas eu le temps de le vérifier, 
    libre à vous de faire votre propre nettoyage en partant de `own_text`


### CSVs à ouvrir de préférence sous python avec `pandas`:
```python
from typing import Dict
import os
import pandas as pd

TWEET_CSV_HEADER = [
    'username', 'id', 'datetime', 'type', 'text',
    'has_referenced_tweet', 'referenced_tweet_found',
    'referenced_tweet_id', 'referenced_tweet_text',
    'referenced_tweet_datetime',
    'referenced_tweet_author_id', 'referenced_tweet_author_name',
    'referenced_tweet_author_username', 'own_text', 'cleaned_text'
]

_TWEET_CSV_HEADER_DTYPES = [str, str, str, str, str,
                            bool, bool,
                            str, str,
                            str,
                            str, str,
                            str, str, str]

if len(TWEET_CSV_HEADER) != len(_TWEET_CSV_HEADER_DTYPES):
    raise ValueError('tweet headers & types lengths do not match')

TWEET_CSV_HEADER_DTYPES = {col: dtype for (col, dtype)
                           in zip(TWEET_CSV_HEADER, _TWEET_CSV_HEADER_DTYPES)}


def read_postprocessed_csvs(csvs_dir: str) -> Dict[str, pd.DataFrame]:
    csvs = {}
    for csv_filename in os.listdir(csvs_dir):
        username = csv_filename.rstrip('.csv')
        csv_path = os.path.join(csvs_dir, csv_filename)
        df = pd.read_csv(csv_path,
                         header=0,
                         dtype=TWEET_CSV_HEADER_DTYPES)
        csvs[username] = df
    return csvs
```