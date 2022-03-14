from typing import List, Optional

import os
import pandas as pd
import csv

from tweet_scrapper.constants import (CANDIDATES_USERNAMES,
                                      CANDIDATES_TWEET_CSVS)
from tweet_scrapper.parse_tweet import (get_tweet_type,
                                        get_referenced_tweet_and_user,
                                        TweetType)
from tweet_scrapper.tweets import get_tweets

from tweet_scrapper.create_csvs import (TWEET_CSV_HEADER,
                                        TWEET_CSV_HEADER_DTYPES,
                                        merge_tweet_dfs)


def _get_older_tweet_ids(username: str) -> Optional[List[int]]:
    old_path = CANDIDATES_TWEET_CSVS[username].replace('tweets', 'tweets_old')
    if os.path.isfile(old_path):
        old_df = pd.read_csv(old_path, header=0)
        df = pd.read_csv(CANDIDATES_TWEET_CSVS[username],
                         header=0,
                         dtype=TWEET_CSV_HEADER_DTYPES)
        df_tweet_ids = set(df['id'].apply(lambda id_: int(id_)))
        old_df_tweet_ids = set(old_df['id'].apply(lambda id_: int(id_)))
        old_tweet_ids = old_df_tweet_ids - df_tweet_ids
        return list(old_tweet_ids)
    else:
        return None


def _update_older_tweets(username: str):
    older_tweet_ids = _get_older_tweet_ids(username)
    if not older_tweet_ids:
        print(f'no older tweets to fetch for {username}')
        return
    print(f'fetching {len(older_tweet_ids)} older tweets for {username}')

    df = pd.read_csv(CANDIDATES_TWEET_CSVS[username],
                     header=0,
                     dtype=TWEET_CSV_HEADER_DTYPES)

    tweets, includes = get_tweets(older_tweet_ids)
    data = []
    if tweets:
        for tweet in tweets:
            tweet_type, referenced_tweet_id = get_tweet_type(tweet)
            referenced_tweet, user = None, None
            not_found = False
            if referenced_tweet_id:
                try:
                    referenced_tweet, user = get_referenced_tweet_and_user(
                        referenced_tweet_id, includes)
                except ValueError:
                    print(
                        f'referenced tweet {referenced_tweet_id} not found'
                        f' for tweet {tweet.id} ({tweet_type.value}) - '
                        f'text: {tweet.text}')
                    not_found = True
            tweet_row = {
                'username': username,
                'id': str(tweet.id),
                'datetime': tweet.created_at,
                'text': tweet.text,
                'type': tweet_type.value,
                'has_referenced_tweet': bool(referenced_tweet_id),
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

    else:
        print(f'none of the tweet ids {older_tweet_ids} still exist.')
        old_path = CANDIDATES_TWEET_CSVS[username].replace('tweets',
                                                           'tweets_old')
        old_df = pd.read_csv(old_path, header=0)
        tweets = old_df[old_df.id.isin(older_tweet_ids)]
        for tweet in tweets.itertuples():
            if tweet.text.startswith('RT @'):
                tweet_type = TweetType.RETWEET
            elif tweet.text.startswith('@'):
                tweet_type = TweetType.RETWEET
            else:
                print('either quoting or normal tweet:')
                print(tweet.text)
                tweet_type = TweetType.NORMAL
            tweet_row = {
                'username': username,
                'id': str(tweet.id),
                'datetime': tweet.datetime,
                'text': tweet.text,
                'type': tweet_type.value,
                'has_referenced_tweet': tweet_type != TweetType.NORMAL,
                'referenced_tweet_found': False,
                'referenced_tweet_id': '',
                'referenced_tweet_text': '',
                'referenced_tweet_datetime': '',
                'referenced_tweet_author_id': '',
                'referenced_tweet_author_name': '',
                'referenced_tweet_author_username': '',
            }
            data.append(tweet_row)

    old_df = pd.DataFrame(data).astype(TWEET_CSV_HEADER_DTYPES,
                                       errors='ignore')

    merged_df = merge_tweet_dfs([df, old_df])

    merged_df.to_csv(CANDIDATES_TWEET_CSVS[username],
                     index=False,
                     quoting=csv.QUOTE_NONNUMERIC)


def update_csvs_with_older_tweets():
    for username in CANDIDATES_USERNAMES:
        _update_older_tweets(username)
        print('checking deleted tweets...')
        _update_older_tweets(username)


if __name__ == '__main__':
    update_csvs_with_older_tweets()
