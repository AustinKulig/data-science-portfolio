import tweepy
from tweepy import OAuthHandler
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("/Users/austinkulig/PycharmProjects/data-science-portfolio/twitter data scrape/config.ini")

twitter_info = config_object["twitter"]

auth = OAuthHandler(twitter_info['consumer_key'], twitter_info['consumer_secret'])
auth.set_access_token(twitter_info['access_token'], twitter_info['access_secret'])

api = tweepy.API(auth)

# read user timeline
for status in tweepy.Cursor(api.home_timeline).items(10):
    # Process a single status
    print(status.tweet)
