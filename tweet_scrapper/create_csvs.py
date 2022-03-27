import csv
import os
from typing import List

import pandas as pd

from tweet_scrapper.constants import (CANDIDATES_TWEET_CSVS,
                                      CANDIDATES_USERNAMES,
                                      get_last_update_timestamp,
                                      update_last_update_timestamp)
from tweet_scrapper.parse_tweet import (TweetType,
                                        get_referenced_tweet_and_user,
                                        get_tweet_type)
from tweet_scrapper.user_tweets import get_candidates_user_ids, get_user_tweets

TWEET_CSV_HEADER = [
    'username', 'id', 'datetime', 'type', 'text',
    'has_referenced_tweet', 'referenced_tweet_found',
    'referenced_tweet_id', 'referenced_tweet_text',
    'referenced_tweet_datetime',
    'referenced_tweet_author_id', 'referenced_tweet_author_name',
    'referenced_tweet_author_username'
]

_TWEET_CSV_HEADER_DTYPES = [str, str, str, str, str,
                            bool, bool,
                            str, str,
                            str,
                            str, str,
                            str]

if len(TWEET_CSV_HEADER) != len(_TWEET_CSV_HEADER_DTYPES):
    raise ValueError('tweet headers & types lengths do not match')

TWEET_CSV_HEADER_DTYPES = {col: dtype for (col, dtype)
                           in zip(TWEET_CSV_HEADER, _TWEET_CSV_HEADER_DTYPES)}


CANDIDATES_USER_IDS = get_candidates_user_ids()


def merge_tweet_dfs(dfs: List[pd.DataFrame]) -> pd.DataFrame:
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

    tweets, includes = get_user_tweets(user_id,
                                       after_date=last_update_timestamp)
    print(f'fetched {len(tweets)} new tweets')

    if tweets:
        data = []
        for tweet in tweets:
            tweet_type, referenced_tweet_id = get_tweet_type(tweet)
            referenced_tweet, user = None, None
            not_found = False
            if referenced_tweet_id:
                try:
                    referenced_tweet, user = get_referenced_tweet_and_user(
                        referenced_tweet_id, includes)
                except ValueError:
                    print(f'referenced tweet {referenced_tweet_id} not found '
                          f'for tweet {tweet.id} ({tweet_type.value}) - '
                          f'text: {tweet.text}')
                    not_found = True
            tweet_row = {
                'username': username,
                'id': str(tweet.id),
                'datetime': tweet.created_at,
                'text': tweet.text,
                'type': tweet_type.value,
                'has_referenced_tweet': tweet_type != TweetType.NORMAL,
                'referenced_tweet_found': (referenced_tweet_id
                                           and not not_found),
                'referenced_tweet_id': (str(referenced_tweet.id)
                                        if referenced_tweet else ''),
                'referenced_tweet_text': (referenced_tweet.text
                                          if referenced_tweet else ''),
                'referenced_tweet_datetime': (referenced_tweet.created_at
                                              if referenced_tweet else ''),
                'referenced_tweet_author_id': str(user.id) if user else '',
                'referenced_tweet_author_name': user.name if user else '',
                'referenced_tweet_author_username': (user.username
                                                     if user else ''),
            }
            data.append(tweet_row)
        new_df = pd.DataFrame(data).astype(TWEET_CSV_HEADER_DTYPES,
                                           errors='ignore')

        merged_df = merge_tweet_dfs([df, new_df])

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
