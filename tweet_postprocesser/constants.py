import os

from tweet_scrapper.constants import CANDIDATES_TWEET_CSVS, DATA_DIR
from tweet_scrapper.create_csvs import TWEET_CSV_HEADER_DTYPES

TWEETS_DIR = os.path.join(DATA_DIR, 'postprocessed_tweets')
REAL_WORDS_JSON = os.path.join(DATA_DIR, 'real_words.json')

POSTPROCESSED_COLUMN_HEADERS = [
    # for quoted tweets: get rid of quoted text (so it can be '')
    # for normal tweets: nothing changed
    # for retweets: ''
    # for replies: text without the @usernames of the users being replied to
    'own_text',
    # cleaned from links, usernames, emojis, punctuation etc.
    'cleaned_text'
]

_POSTPROCESSED_COLUMN_HEADER_DTYPES = [str, str]

POSTPROCESSED_TWEET_HEADER_DTYPES = TWEET_CSV_HEADER_DTYPES.copy()
POSTPROCESSED_TWEET_HEADER_DTYPES.update({
    col: dtype for (col, dtype)
    in zip(POSTPROCESSED_COLUMN_HEADERS, _POSTPROCESSED_COLUMN_HEADER_DTYPES)
})

POSTPROCESSED_TWEET_CSVS = {}
for candidate, path in CANDIDATES_TWEET_CSVS.items():
    scrapped_tweets_dir, filename = os.path.split(path)
    postprocessed_tweets_dir = os.path.join(
        os.path.dirname(scrapped_tweets_dir), TWEETS_DIR)
    POSTPROCESSED_TWEET_CSVS[candidate] = os.path.join(
        postprocessed_tweets_dir, filename)
