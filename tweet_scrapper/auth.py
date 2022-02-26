import os
from dotenv import load_dotenv
from tweepy import Client


load_dotenv()

OAUTH2_BEARER_TOKEN = os.getenv('OAUTH2_BEARER_TOKEN')


def get_client() -> Client:
    return Client(OAUTH2_BEARER_TOKEN)
