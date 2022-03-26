from typing import Optional, Union, List, Dict, Iterable, Tuple

from datetime import datetime
from tweepy import Client, Tweet, Response

from tweet_scrapper.auth import get_client
from tweet_scrapper.constants import CANDIDATES_USERNAMES
from tweet_scrapper.tweets import GET_TWEET_ARGS


def _get_user_id(username: str,
                 client: Optional[Client] = None) -> int:
    """Max 100 usernames in the list"""
    if not client:
        client = get_client()
    response = client.get_user(username=username)
    return response.data.id


def _get_user_ids(usernames: Iterable[str],
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
    user_ids = _get_user_ids(usernames, client)
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
        **GET_TWEET_ARGS
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


def _query_tweets_paginated(
        user_id: Union[int, str],
        after_tweet_id: Optional[Union[int, str]] = None,
        after_date: Optional[Union[datetime, str]] = None,
        before_tweet_id: Optional[Union[int, str]] = None,
        before_date: Optional[Union[datetime, str]] = None,
        client: Optional[Client] = None) -> Tuple[List[Tweet], dict]:
    """Pagination goes from most recent to oldest tweet.
    API only gives access to the last 3200 tweets of the user.
    """

    pagination_token = None
    tweets = []
    includes = {'users': [], 'tweets': []}
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
        response_tweets = response.data
        if not response_tweets:
            break
        includes['users'].extend(response.includes.get('users', []))
        includes['tweets'].extend(response.includes.get('tweets', []))
        tweets.extend(response_tweets)
        pagination_token = response.meta.get('next_token')
        if not pagination_token:
            break
    return tweets, includes


def get_user_tweets(
        user_id: Union[int, str],
        after_tweet_id: Optional[Union[int, str]] = None,
        after_date: Optional[Union[datetime, str]] = None,
        before_tweet_id: Optional[Union[int, str]] = None,
        before_date: Optional[Union[datetime, str]] = None,
        client: Optional[Client] = None) -> Tuple[List[Tweet], dict]:
    """Gets tweets of a specific user with optional chronological filtering"""
    return _query_tweets_paginated(
        user_id,
        after_tweet_id=after_tweet_id,
        after_date=after_date,
        before_tweet_id=before_tweet_id,
        before_date=before_date,
        client=client,
    )


def get_all_available_user_tweets(
        user_id: Union[int, str],
        client: Optional[Client] = None) -> Tuple[List[Tweet], dict]:
    """Gets all the available tweets of a user, i.e. the ~3200 latest tweets"""
    return _query_tweets_paginated(user_id, client=client)
