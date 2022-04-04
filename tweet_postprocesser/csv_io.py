import csv
from typing import Dict

import pandas as pd

from tweet_postprocesser.constants import (CANDIDATES_TWEET_CSVS,
                                           POSTPROCESSED_TWEET_CSVS,
                                           POSTPROCESSED_TWEET_HEADER_DTYPES,
                                           TWEET_CSV_HEADER_DTYPES)


def read_scrapped_csvs() -> Dict[str, pd.DataFrame]:
    csvs = {}
    for username, csv_path in CANDIDATES_TWEET_CSVS.items():
        df = pd.read_csv(csv_path,
                         header=0,
                         dtype=TWEET_CSV_HEADER_DTYPES)
        csvs[username] = df
    return csvs


def save_postprocessed_csv(df: pd.DataFrame, username: str):
    for username_, csv_path in POSTPROCESSED_TWEET_CSVS.items():
        if username_ == username:
            return df.to_csv(csv_path,
                             index=False,
                             quoting=csv.QUOTE_NONNUMERIC)
    raise ValueError(username)


def save_postprocessed_csvs(dfs: Dict[str, pd.DataFrame]):
    for username, csv_path in POSTPROCESSED_TWEET_CSVS.items():
        df = dfs[username]
        df.to_csv(csv_path,
                  index=False,
                  quoting=csv.QUOTE_NONNUMERIC)


def read_postprocessed_csvs() -> Dict[str, pd.DataFrame]:
    csvs = {}
    for username, csv_path in POSTPROCESSED_TWEET_CSVS.items():
        df = pd.read_csv(csv_path,
                         header=0,
                         dtype=POSTPROCESSED_TWEET_HEADER_DTYPES)
        csvs[username] = df
    return csvs
