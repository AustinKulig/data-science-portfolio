import sys
import tweepy
from tweepy import OAuthHandler, tweet
from configparser import ConfigParser
import json


# Accessing Twitter Data

config_object = ConfigParser()
config_object.read("/Users/austinkulig/PycharmProjects/data-science-portfolio/Data Scrapping/twitter data "
                   "scrape/config.ini")

twitter_info = config_object["twitter"]

auth = OAuthHandler(twitter_info['consumer_key'], twitter_info['consumer_secret'])
auth.set_access_token(twitter_info['access_token'], twitter_info['access_secret'])

api = tweepy.API(auth)

# read user timeline
for status in tweepy.Cursor(api.home_timeline).items(5):
    # Process a single status
    print(status.text)

# def process_or_store(tweet):
    # print(json.dumps(tweet))


# for tweet in tweepy.Cursor(api.user_timeline).items(2):
    # process_or_store(tweet._json)


# encoder
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=199)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=199, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

    # print total tweets fetched from given screen name
    print
    "Total tweets downloaded from %s are %s" % (screen_name, len(alltweets))

    return alltweets


def fetch_tweets(screen_names):
    # initialize the list to hold all tweets from all users
    alltweets = []

    # get all tweets for each screen name
    for screen_name in screen_names:
        alltweets.extend(get_all_tweets(screen_name))

    return alltweets


def store_tweets(alltweets, file=sys.argv[2]):
    # a list of all formatted tweets
    tweet_list = []

    for tweet in alltweets:
        # a dict to contain information about single tweet
        tweet_information = dict()

        # text of tweet
        tweet_information['text'] = tweet.text.encode('utf-8')

        # date and time at which tweet was created
        tweet_information['created_at'] = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")

        # id of this tweet
        tweet_information['id_str'] = tweet.id_str

        # retweet count
        tweet_information['retweet_count'] = tweet.retweet_count

        # favourites count
        tweet_information['favorite_count'] = tweet.favorite_count

        # screename of the user to which it was replied (is Nullable)
        tweet_information['in_reply_to_screen_name'] = tweet.in_reply_to_screen_name

        # user information in user dictionery
        user_dictionery = tweet._json['user']

        # no of followers of the user
        tweet_information['followers_count'] = user_dictionery['followers_count']

        # screename of the person who tweeted this
        tweet_information['screen_name'] = user_dictionery['screen_name']

        # add this tweet to the tweet_list
        tweet_list.append(tweet_information)

    # open file desc to output file with write permissions
    file_des = open(file, 'w', encoding='utf-8')
    # file_des = open(file, 'wb')

    # dump tweets to the file
    json.dump(tweet_list, file_des, ensure_ascii=False, cls=MyEncoder, indent=4)
    # json.dump(tweet_list, file_des, indent=4, sort_keys=True)

    # close the file_des
    file_des.close()


if __name__ == '__main__':

    # pass in the username of the account you want to download
    alltweets = get_all_tweets(sys.argv[1])

    # store the data into json file
    if len(sys.argv[2]) > 0:
        store_tweets(alltweets, sys.argv[2])
    else:
        store_tweets(alltweets)


