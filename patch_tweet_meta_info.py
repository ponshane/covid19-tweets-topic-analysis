import tweepy
import configparser
import argparse

from tqdm import tqdm
from math import ceil
from multiprocessing import Pool
from pymongo import MongoClient, UpdateOne

def get_collection_cursor(collection):
    client = MongoClient(uri)
    return client[MongoDB][collection]

def parse(tweet):
    tweet = tweet._json

    user = {}
    coordinates = {}
    place = {}
    retweet_count = 0
    favorite_count = 0

    # user-info
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
    
    return UpdateOne(filter={"id_str": tweet["id_str"]},\
                    update={
                        "$set":{
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
    pbar = tqdm(total=ceil(tweet_count / 100))
    pool = Pool(6)
    try:
        # initial the list for storing updates
        operations = []
        for i in range(ceil(tweet_count / 100)):
            # Catch the last group if it is less than 100 tweets
            end_loc = min((i + 1) * 100, tweet_count)
            
            rs = api.statuses_lookup(id_=tweet_IDs[i * 100:end_loc], tweet_mode="extended")
            
            if len(rs) != 0:
                operations += list(pool.imap_unordered(parse, rs))

            if i % 10 == 0:
                # if there has any update
                if len(operations) != 0:
                        target_collection.bulk_write(operations)
                        operations = []
            
            pbar.update(1)

        # write the all last bulk of updates
        if len(operations) != 0:
            target_collection.bulk_write(operations)
        pbar.close()
    except tweepy.TweepError:
        print('Tweepy got something wrong...')
        pbar.close()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', type=str, nargs="+", required=True, dest="collections",
                        help='give a list of collection name, e.g., -c Collection1 Collection2')
    args = parser.parse_args()

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

    # mongo query
    query = {}
    query["text"] = {
        u"$exists": True
    }
    query["patched"] = {
        u"$exists": False
    }

    for collection_name in args.collections:
        target_collection = get_collection_cursor(collection_name)
        ############## Find those Tweets' Id which need to be patched ######################
        id_list = []
        for doc in target_collection.find(query):
            id_list.append(doc["id_str"])

        lookup_tweets(id_list, api)
        ####################################################################################