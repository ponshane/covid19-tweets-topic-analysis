import json
import re
import string
import configparser
import argparse
import time

import tweepy

from multiprocessing import Pool
from pymongo import MongoClient, UpdateOne
from datetime import datetime
from nltk.corpus import stopwords
from math import ceil

class Timer():
    def __init__(self):
        """ Return Elapsed Time
        This is a helper class for measuring the elapsed time 
        for a code block.

        Example:
            with Timer():
                do_something()
        """
        pass
    def __enter__(self):
        self.start = time.time()
        return None
    def __exit__(self, type, value, traceback):
        elapsed_time = time.time() - self.start
        print("Elasped Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
 
def get_collection_cursor(collection):
    client = MongoClient(uri)
    return client[MongoDB][collection]

def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s):
    
    ############## clean first ##############
    # remove emoji
    s = emoji_pattern.sub(r'', s)
    s = re.sub(emoticons_str, r'', s)
    s = re.sub(r'(?:(?:\d+,?)+(?:\.?\d+)?)', r'', s) # numbers
    s = re.sub(r'<[^>]+>', r'', s) # HTML tags
    s = re.sub(r'(?:@[\w_]+)', r'', s) # @-mentions
    s = re.sub(r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',\
              r'', s) # URLs
    #########################################
    
    # split tokens
    tokens = tokenize(s)
    # lowerize the tokens
    tokens = [w.lower() for w in tokens]
    
    filtered_tokens = []
    for w in tokens:
        #check tokens against stop words and punctuations
        if w not in STOP_WORDS and w not in string.punctuation:
            filtered_tokens.append(w)
    
    return filtered_tokens

def parse(tweet):

    tweet = tweet._json

    user = {}
    coordinates = {}
    place = {}
    retweet_count = 0
    favorite_count = 0

    # user information
    allowed_ks = ["id_str", "screen_name", "location", "followers_count",\
         "friends_count", "listed_count", "favourites_count", "created_at", "verified"]

    if tweet.get("user") != None:
        temp_user = tweet["user"]
        # store all user information is too bulky
        user = {k: v for k, v in temp_user.items() if k in allowed_ks}
    # coordinates
    if tweet.get("coordinates") != None:
        coordinates = tweet.get("coordinates")
    # place
    if tweet.get("place") != None:
        place = tweet.get("place")
    # numbers of retweet
    if tweet.get("retweet_count") != None:
        retweet_count = tweet.get("retweet_count")
    # numbers of likes
    if tweet.get("favorite_count") != None:
        favorite_count = tweet.get("favorite_count")

    hashtags = []
    if len(tweet["entities"]) > 0:
        hashtags = [tag["text"] for tag in tweet["entities"]["hashtags"]]

    try:
        tokens = preprocess(tweet["full_text"])
    except KeyError:
        print(tweet)
    
    return UpdateOne(filter={"id_str": tweet["id_str"]},\
                    update={
                        "$set":{
                            "hashtags": hashtags,
                            "text": tweet["full_text"],
                            "tokens": tokens,
                            "user": user,
                            "coordinates": coordinates,
                            "place": place,
                            "retweet_count": retweet_count,
                            "favorite_count": favorite_count,
                            "patched": True
                        }
                    })

def lookup_tweets(tweet_IDs, api):
    tweet_count = len(tweet_IDs)
    pool = Pool(6)
    try:
        # initial the list for storing updates
        operations = []
        for i in range(ceil(tweet_count / 100)):
            # Catch the last group if it is less than 100 tweets
            end_loc = min((i + 1) * 100, tweet_count)
            
            rs = api.statuses_lookup(id_=tweet_IDs[i * 100:end_loc], tweet_mode="extended")
            
            if len(rs) != 0:
                with Timer():
                    operations += list(pool.imap_unordered(parse, rs))
                print("Has processed {} tweets".format(len(rs)))

            if i % 10 == 0:
                
                # if there has any update
                if len(operations) != 0:
                    with Timer():
                        target_collection.bulk_write(operations)
                    print("Has updated {} tweets in MongoDB".format(len(operations)))
                    # clear operations
                    operations = []

                print("{}: ({}/{}) tweets have scanned.".format(collection_name, str(i*100),\
                     str(tweet_count)))

        # write the all last bulk of updates
        if len(operations) != 0:
            target_collection.bulk_write(operations)

    except tweepy.TweepError:
        print('Something went wrong, quitting...')

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', type=str, nargs="+", required=True, dest="collections",
                        help='give a list of collection name, e.g., -c Collection1 Collection2')
    args = parser.parse_args()

    emoticons_str = r"(?:[:=;][oO\-]?[D\)\(\[\]\\OpP])"

    #Emoji patterns
    emoji_pattern = re.compile("["
             u"\U0001F600-\U0001F64F"  # emoticons
             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
             u"\U0001F680-\U0001F6FF"  # transport & map symbols
             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
             u"\U00002702-\U000027B0"
             u"\U000024C2-\U0001F251"
             "]+", flags=re.UNICODE)

    regex_str = [
        r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
        r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
        r'(?:[\w_]+)', # other words
        r'(?:\S)' # anything else
    ]

    tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)

    STOP_WORDS = set(stopwords.words('english'))
    
    # initialize and read config file - connect to mongodb
    config = configparser.ConfigParser()
    config.read('./config.ini')

    # connect to mongo
    MongoServer = config["Mongo"]["URI"]
    MongoDB = config["Mongo"]["Database"]
    MongoUser = config["Mongo"]["User"]
    MongoPW = config["Mongo"]["PW"]

    uri = "mongodb://" + MongoUser + ":" + MongoPW + "@" + MongoServer + "/?authSource=" +\
    MongoDB + "&authMechanism=SCRAM-SHA-1"
    
    access_token = config["Twitter"]["access_token"]
    access_token_secret = config["Twitter"]["access_token_secret"]
    consumer_key = config["Twitter"]["consumer_key"]
    consumer_secret = config["Twitter"]["consumer_secret"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    for collection_name in args.collections:
        target_collection = get_collection_cursor(collection_name)
        ############## Find those Tweets' Id which need to be updated ######################
        id_list = []
        for doc in target_collection.find({"text":{"$exists": False}}):
            id_list.append(doc["id_str"])

        lookup_tweets(id_list, api)
        ####################################################################################