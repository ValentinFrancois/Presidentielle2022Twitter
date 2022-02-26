from typing import Optional, Union, List, Dict, Iterable

from datetime import datetime
from tweepy import Client, Tweet, Response

from tweet_scrapper.auth import get_client
from tweet_scrapper.constants import CANDIDATES_USERNAMES


def get_user_id(username: str,
                client: Optional[Client] = None) -> int:
    """Max 100 usernames in the list"""
    if not client:
        client = get_client()
    response = client.get_user(username=username)
    return response.data.id


def get_user_ids(usernames: Iterable[str],
                 client: Optional[Client] = None) -> Dict[str, int]:
    """Max 100 usernames in the list"""
    if not client:
        client = get_client()
    result = {username: None for username in usernames}
    response = client.get_users(usernames=list(usernames))
    for user in response.data:
        result[user.username] = user.id
    return result


def get_candidates_user_ids(client: Optional[Client] = None) -> Dict[str, int]:
    usernames = [username.replace('@', '')
                 for username in CANDIDATES_USERNAMES]
    user_ids = get_user_ids(usernames, client)
    return user_ids


def _query_tweets(user_id: Union[int, str],
                  after_tweet_id: Optional[Union[int, str]] = None,
                  after_date: Optional[Union[datetime, str]] = None,
                  before_tweet_id: Optional[Union[int, str]] = None,
                  before_date: Optional[Union[datetime, str]] = None,
                  pagination_token: Optional[str] = None,
                  client: Optional[Client] = None) -> Response:

    args = dict(
        id=user_id,
        # 100 is the maximum allowed count
        max_results=100,
        # we could filter out retweets and replies here but it limits to 800
        # results instead of 3200
        # exclude=['retweets', 'replies'],
        # minimal fields in response:
        tweet_fields=['id', 'text', 'created_at', 'referenced_tweets'],
        user_fields=[],
        media_fields=[],
        poll_fields=[],
        place_fields=[]
    )
    if after_tweet_id:
        args['since_id'] = after_tweet_id  # excluding condition
    if after_date:
        args['start_time'] = after_date
    if before_tweet_id:
        args['until_id'] = before_tweet_id  # excluding condition
    if before_date:
        args['end_time'] = before_date
    if pagination_token:
        args['pagination_token'] = pagination_token

    if not client:
        client = get_client()

    return client.get_users_tweets(**args)


def _query_tweets_paginated(user_id: Union[int, str],
                            after_tweet_id: Optional[Union[int, str]] = None,
                            after_date: Optional[Union[datetime, str]] = None,
                            before_tweet_id: Optional[Union[int, str]] = None,
                            before_date: Optional[Union[datetime, str]] = None,
                            client: Optional[Client] = None) -> List[Tweet]:
    """Pagination goes from most recent to oldest tweet.
    API only gives access to the last 3200 tweets of the user.
    """

    pagination_token = None
    tweets = []
    i = 0
    while True:
        response = _query_tweets(
            user_id,
            after_tweet_id=after_tweet_id,
            after_date=after_date,
            before_tweet_id=before_tweet_id,
            before_date=before_date,
            pagination_token=pagination_token,
            client=client
        )
        i += 1
        response_tweets = response.data
        if not response_tweets:
            break
        tweets.extend(response_tweets)
        pagination_token = response.meta.get('next_token')
        if not pagination_token:
            break
    return tweets


def get_user_tweets(*args, **kwargs) -> List[Tweet]:
    return _query_tweets_paginated(*args, **kwargs)


def get_all_available_user_tweets(
        user_id: Union[int, str],
        client: Optional[Client] = None) -> List[Tweet]:
    return _query_tweets_paginated(user_id, client=client)
