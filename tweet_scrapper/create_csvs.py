from typing import List

import os
import pandas as pd
import csv

from tweet_scrapper.constants import (CANDIDATES_USERNAMES,
                                      CANDIDATES_TWEET_CSVS,
                                      get_last_update_timestamp,
                                      update_last_update_timestamp)
from tweet_scrapper.tweet import get_tweet_type
from tweet_scrapper.user_tweets import (get_user_tweets,
                                        get_candidates_user_ids)


TWEET_CSV_HEADER = ['username', 'id', 'datetime', 'type', 'text']
_TWEET_CSV_HEADER_DTYPES = [str, int, str, str, str]
TWEET_CSV_HEADER_DTYPES = {col: dtype for (col, dtype)
                           in zip(TWEET_CSV_HEADER, _TWEET_CSV_HEADER_DTYPES)}


CANDIDATES_USER_IDS = get_candidates_user_ids()


def _merge_tweet_dfs(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    concatenated = pd.concat(dfs, ignore_index=True)
    concatenated.sort_values(by='datetime', inplace=True, ascending=False)
    filtered = concatenated.drop_duplicates(subset='id', keep='first')
    if concatenated.shape[0] > filtered.shape[0]:
        print('WARNING - Some duplicates were filtered out')
    return filtered


def update_candidate_csv(username: str,
                         last_update_timestamp: str):
    user_id = CANDIDATES_USER_IDS[username]

    if os.path.isfile(CANDIDATES_TWEET_CSVS[username]):
        df = pd.read_csv(CANDIDATES_TWEET_CSVS[username],
                         header=0,
                         dtype=TWEET_CSV_HEADER_DTYPES)
    else:
        df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype
                           in TWEET_CSV_HEADER_DTYPES.items()})
        last_update_timestamp = None

    tweets = get_user_tweets(user_id, after_date=last_update_timestamp)
    print(f'fetched {len(tweets)} new tweets')

    if tweets:
        new_df = pd.DataFrame(
            data=[{
                'username': username,
                'id': tweet.id,
                'datetime': tweet.created_at,
                'text': tweet.text,
                'type': get_tweet_type(tweet).value
            } for tweet in tweets]
        ).astype(TWEET_CSV_HEADER_DTYPES)

        merged_df = _merge_tweet_dfs([df, new_df])

        merged_df.to_csv(CANDIDATES_TWEET_CSVS[username],
                         index=False,
                         quoting=csv.QUOTE_NONNUMERIC)


def do_update():
    last_update_timestamp = get_last_update_timestamp()
    print(last_update_timestamp)
    for username in CANDIDATES_USERNAMES:
        print(f'getting tweets of {username}')
        update_candidate_csv(username,
                             last_update_timestamp=last_update_timestamp)
    update_last_update_timestamp()


if __name__ == '__main__':
    do_update()
