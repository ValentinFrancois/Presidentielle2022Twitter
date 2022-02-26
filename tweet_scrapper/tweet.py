from typing import Optional, Union, List, Dict, Iterable
from enum import Enum

from tweepy import Tweet


class TweetType(Enum):
    NORMAL = 'normal'
    QUOTING = 'quoting'
    RETWEET = 'retweet'
    REPLY = 'reply'


def get_tweet_type(tweet: Tweet) -> TweetType:
    if not tweet.referenced_tweets:
        return TweetType.NORMAL
    else:
        for referenced_type in [t['type'] for t in tweet.referenced_tweets]:
            if referenced_type == 'retweeted':
                return TweetType.RETWEET
            elif referenced_type == 'replied_to':
                return TweetType.REPLY
            elif referenced_type == 'quoted':
                return TweetType.QUOTING
    return TweetType.NORMAL


def filter_out_replies_and_retweets(tweets: List[Tweet]) -> List[Tweet]:
    filtered_tweets = [
        tweet for tweet in tweets
        if get_tweet_type(tweet) in {TweetType.NORMAL, TweetType.QUOTING}
    ]
    return filtered_tweets
