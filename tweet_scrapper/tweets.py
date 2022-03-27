from typing import List, Optional, Tuple, Union

from tweepy import Client, Response, Tweet

from tweet_scrapper.auth import get_client

# minimal fields in response:
GET_TWEET_ARGS = dict(
    expansions=['author_id',
                'referenced_tweets.id',
                'referenced_tweets.id.author_id'],
    tweet_fields=['id', 'text', 'created_at',
                  'referenced_tweets', 'author_id'],
    user_fields=['id', 'username'],
    media_fields=[],
    poll_fields=[],
    place_fields=[]
)


def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _query_tweets(tweet_ids: List[Union[int, str]],
                  client: Optional[Client] = None) -> Response:
    """Max 100 tweet ids"""
    args = dict(
        ids=tweet_ids,
        **GET_TWEET_ARGS
    )
    if not client:
        client = get_client()

    return client.get_tweets(**args)


def get_tweets(tweet_ids: List[Union[int, str]],
               client: Optional[Client] = None) -> Tuple[List[Tweet], dict]:
    """Get tweets from list of IDs"""
    tweets = []
    includes = {'users': [], 'tweets': []}
    if not client:
        client = get_client()
    for chunk_100_tweet_ids in _chunks(tweet_ids, 100):
        response = _query_tweets(chunk_100_tweet_ids, client)
        response_tweets = response.data
        if not response_tweets:
            continue
        tweets.extend(response_tweets)
        includes['users'].extend(response.includes.get('users', []))
        includes['tweets'].extend(response.includes.get('tweets', []))
    return tweets, includes
