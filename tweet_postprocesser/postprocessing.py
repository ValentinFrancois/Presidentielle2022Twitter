import re
import time
from typing import Dict, Tuple

import pandas as pd
import spacy
from bs4 import BeautifulSoup

from tweet_postprocesser.csv_io import (read_scrapped_csvs,
                                        save_postprocessed_csv)
from tweet_scrapper.parse_tweet import TweetType

nlp = spacy.load('fr_core_news_md')


USERNAME_REGEX = re.compile('@(\\w){1,30}')
REPLY_TO_REGEX = re.compile(f'^(({USERNAME_REGEX} )+)')
TWEET_URL_REGEX = re.compile('https?:\\/\\/t\\.co\\/[0-9a-zA-Z\\-\\_]{5,30}$')
HASHTAG_REGEX = re.compile('#(\\w+)')

EMOJIS_REGEX = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE)
# https://www.regextester.com/106421
EMOJIS_REGEX_2 = re.compile(
    u'(\u00a9|\u00ae|[\u2020-\u3300]|\ud83c[\ud000-\udfff]'
    u'|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]|🟢)', flags=re.UNICODE)

URL_REGEX = re.compile(r'(https?://)?(www\.)?(\w+\.)?(\w+)(\.\w+)(/.+)?')
PUNCTUATION_REGEX = re.compile('(\\.{2,100})|(#)')
WEIRD_CHARACTERS_REGEX = re.compile('(\\[\\.+\\])|[«»‹›!\\?"\']')


def extract_replied_to(tweet_text) -> Tuple[Tuple[str], str]:
    cleaned_text = re.sub(REPLY_TO_REGEX, '', tweet_text, count=1)
    if cleaned_text == tweet_text:
        # user replied to themselves
        return tuple(), tweet_text
    else:
        usernames = re.match(REPLY_TO_REGEX, tweet_text).groups()[0]
        usernames = tuple(usernames.rstrip(' ').split(' '))
        return usernames, cleaned_text


def extract_quoting_own_text(tweet_text) -> str:
    splitted_text = re.sub(TWEET_URL_REGEX, '', tweet_text)
    return splitted_text.rstrip()


def get_own_text(tweets_csv_row) -> str:
    tweet_type = tweets_csv_row['type']
    text = tweets_csv_row['text']
    if tweet_type == TweetType.NORMAL.value:
        return text
    elif tweet_type == TweetType.RETWEET.value:
        return ''
    elif tweet_type == TweetType.REPLY.value:
        return extract_replied_to(text)[1]
    elif tweet_type == TweetType.QUOTING.value:
        return extract_quoting_own_text(text)
    else:
        raise ValueError(tweet_type)


def is_real_word(word: str) -> bool:
    if len(word) <= 1 and not word.isalpha():
        return False
    tokens = nlp(word)
    if not (hasattr(tokens, 'is_oov') or len(tokens) == 1):
        return False
    if hasattr(tokens, 'is_oov'):
        return not tokens.is_oov
    else:
        return not tokens[0].is_oov


def _remove_multiple_regex(text: str, regexes: list) -> str:
    res = text
    for regex in regexes:
        res = re.sub(regex, '', res)
    return res


def clean_tweet_text(tweet_text: str) -> str:
    no_emojis_text = re.sub(EMOJIS_REGEX, '', tweet_text)
    no_emojis_text = re.sub(EMOJIS_REGEX_2, '', no_emojis_text)

    no_url_text = re.sub(URL_REGEX, '', no_emojis_text)

    no_username_text = re.sub(USERNAME_REGEX, '', no_url_text)

    lowercase_text = no_username_text.lower()

    hashtags = set(re.findall(HASHTAG_REGEX, lowercase_text))
    cleaned_hashtags_text = lowercase_text
    if hashtags:
        real_words = {hashtag for hashtag in hashtags if is_real_word(hashtag)}
        pure_hashtags = hashtags - real_words
        for pure_hashtag in pure_hashtags:
            cleaned_hashtags_text = cleaned_hashtags_text.replace(
                f'#{pure_hashtag}', '')

    no_html_text = BeautifulSoup(cleaned_hashtags_text, 'lxml').get_text()

    cleaned_text_tokens = nlp(no_html_text)
    cleaned_text_tokens = [
        token_.text for token_ in cleaned_text_tokens
        if not (token_.is_quote
                or token_.is_stop
                or token_.is_digit
                or token_.is_punct
                or token_.is_space
                or token_.is_bracket
                or token_.is_currency)
    ]

    cleaned_text = ' '.join(cleaned_text_tokens)
    cleaned_text = _remove_multiple_regex(cleaned_text,
                                          [PUNCTUATION_REGEX,
                                           WEIRD_CHARACTERS_REGEX])

    return cleaned_text


def do_post_processing():
    scrapped_csvs_dfs: Dict[str, pd.DataFrame] = read_scrapped_csvs()
    for username, df in scrapped_csvs_dfs.items():
        start_time = time.time()
        print(f'postprocessing {len(df)} tweets of {username}...')
        own_text_column = df.apply(get_own_text, axis=1)
        df['own_text'] = own_text_column
        cleaned_text_column = own_text_column.apply(clean_tweet_text)
        df['cleaned_text'] = cleaned_text_column
        spent_minutes = (time.time() - start_time)/60
        print(f'postprocessed in {round(spent_minutes, 1)} min')
        save_postprocessed_csv(df, username)


if __name__ == '__main__':
    do_post_processing()



