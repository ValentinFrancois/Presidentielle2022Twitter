from tweet_scrapper.create_csvs import do_update as update_scrapped_tweets_csvs
from tweet_postprocesser.postprocessing import do_post_processing

if __name__ == '__main__':
    update_scrapped_tweets_csvs()
    do_post_processing()
