import os
from typing import Set

import pandas as pd

from tweet_scrapper.dates import get_date_now

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'data')

CANDIDATES_LIST_CSV = os.path.join(DATA_DIR, 'candidates.csv')

TWEETS_DIR = os.path.join(DATA_DIR, 'scrapped_tweets')

LAST_UPDATE_FILE = os.path.join(DATA_DIR, 'last_update.txt')


def get_last_update_timestamp() -> str:
    with open(LAST_UPDATE_FILE, 'r') as last_update_file:
        content = last_update_file.read()
        return content.replace(' ', '').replace('\n', '')


def update_last_update_timestamp() -> str:
    now = get_date_now()
    with open(LAST_UPDATE_FILE, 'w') as last_update_file:
        last_update_file.write(now)
    return now


def get_candidate_usernames() -> Set[str]:
    df = pd.read_csv(CANDIDATES_LIST_CSV, header=0)
    usernames = set(df.twitter_username)
    return {username.replace('@', '') for username in usernames}


CANDIDATES_USERNAMES = get_candidate_usernames()


def get_candidate_tweets_csv(username: str) -> str:
    return os.path.join(
        TWEETS_DIR,
        f"{username.replace('@', '')}.csv")


CANDIDATES_TWEET_CSVS = {
    username: get_candidate_tweets_csv(username)
    for username in CANDIDATES_USERNAMES
}
