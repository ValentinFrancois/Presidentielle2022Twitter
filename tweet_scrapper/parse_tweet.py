from typing import Optional, Tuple
from enum import Enum

from tweepy import Tweet, ReferencedTweet, User


class TweetType(Enum):
    NORMAL = 'normal'
    QUOTING = 'quoting'
    RETWEET = 'retweet'
    REPLY = 'reply'


def get_tweet_type(tweet: Tweet) -> Tuple[TweetType, Optional[int]]:
    if not tweet.referenced_tweets:
        return TweetType.NORMAL, None
    else:
        for t in tweet.referenced_tweets:
            t: ReferencedTweet
            if t.id == tweet.id:
                continue
            if t.type == 'retweeted':
                return TweetType.RETWEET, t.id
            elif t.type == 'replied_to':
                return TweetType.REPLY, t.id
            elif t.type == 'quoted':
                return TweetType.QUOTING, t.id
    return TweetType.NORMAL, None


def get_referenced_tweet_and_user(referenced_tweet_id: int,
                                  includes: dict) -> Tuple[Tweet, User]:
    referenced_tweet = None
    for included_tweet in includes['tweets']:
        if included_tweet.id == referenced_tweet_id:
            referenced_tweet = included_tweet
    if not referenced_tweet:
        raise ValueError()

    user = None
    for included_user in includes['users']:
        if included_user.id == referenced_tweet.author_id:
            user = included_user
    if not user:
        raise ValueError()

    return referenced_tweet, user
