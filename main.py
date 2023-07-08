import os
import tweepy
from dotenv import load_dotenv

load_dotenv('.env')

# UIUC FREE FOOD TWITTER ID
id = 1522443992847335425

consumer_key = os.environ["Key"]
consumer_secret = os.environ["Secret"]
bearer = os.environ["Bearer"]
access_token = os.environ['Token']
access_token_secret = os.environ['TokenSecret']

client = tweepy.Client(bearer_token = bearer, consumer_key = consumer_key, consumer_secret=consumer_secret, access_token= access_token, access_token_secret=access_token_secret)

li = client.get_users_tweets(id = id,  tweet_fields = ['created_at', 'text', 'id', 'attachments', 'author_id', 'entities'], media_fields = ['url'], expansions=['attachments.media_keys', 'author_id'])
for tweet in li.data:
    print("NEW TWEET")
    print(tweet.created_at)
    print(tweet.text)
    print(tweet.id)
    print("Tweet Url: https://twitter.com/twitter/statuses/{}".format(tweet.id))