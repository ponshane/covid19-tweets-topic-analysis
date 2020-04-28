import json
import configparser
import argparse

from pymongo import MongoClient
from datetime import datetime

def get_collection_cursor(collection):
    client = MongoClient(uri)
    return client[MongoDB][collection]

def parse_tweet_object(tweet):
    
    if tweet["id_str"] in ExistingIDs:
        return 0
    
    # update ExistingIDs
    ExistingIDs.add(tweet["id_str"])

    doc = {}
    doc["created_at"] = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')
    doc["id_str"] = tweet["id_str"]
    
    if "place" in tweet.keys():
        if tweet["place"] != None:
            doc["place"] = {}
            doc["place"]["place_type"] = tweet["place"]["place_type"]
            doc["place"]["full_name"] = tweet["place"]["full_name"]
            doc["place"]["country_code"] = tweet["place"]["country_code"]
    
    target_collection.insert_one(doc)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', type=str, nargs="+", required=True, dest="files",
                        help='give a list of file name, e.g., -f file1.json file2.json, ...')
    parser.add_argument('-c', '--collection', type=str, required=True, dest="collection",
                        help='give a collection name, e.g., -c Collection1')
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

    target_collection = get_collection_cursor(args.collection)
    
    # build ids for preventing from adding duplicated tweets
    ExistingIDs = set()
    for doc in target_collection.find():
        ExistingIDs.add(doc["id_str"])
    print("Loading {} Exising IDs".format(len(ExistingIDs)))
    
    for each_file in args.files:
        f =  open(each_file, 'r')
        print("Loading tweets from {}".format(each_file))
        for i, line in enumerate(f):
            
            # skip empty lines
            if not line.strip():
                continue

            try:
                tweet = json.loads(line)
            except:
                print("JSON Decoding Error. Continue.")
                continue

            if i % 10000 == 0:
                print("{} tweets has processed.".format(str(i)))

            # skip the case which is not with right type
            if not isinstance(tweet, dict):
                continue

            # 若無法語言 Flag 則跳過
            # this happen in streamline mode
            if "lang" not in tweet.keys():
                continue
            
            # 若非英文推，則跳過此筆資料
            if tweet["lang"] != "en":
                continue            

            # if this tweet is a retweet
            if "retweeted_status" in tweet.keys():
                parse_tweet_object(tweet["retweeted_status"])

            # if this tweet is a quoted tweet
            elif "quoted_status" in tweet.keys():
                # parse quoted tweet
                parse_tweet_object(tweet["quoted_status"])
                # parse original tweet
                parse_tweet_object(tweet)

            # if this is an original tweet
            else:
                # parse orginal tweet
                parse_tweet_object(tweet)

        f.close()