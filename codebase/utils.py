import time
import os.path
import configparser
from collections import namedtuple

from pymongo import MongoClient

RawTweet = namedtuple("rawTweet", ["id_str", "created_at", "tokens_str"])

class Timer():
    def __init__(self):
        """ This is a helper class for measuring the elapsed time 
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

class NoCollectionError(Exception):
    pass

class MongoConnector():
    def __init__(self, config_file, prefix=""):
        
        # check whether the file exists
        assert os.path.isfile(config_file) == True
            
        config = configparser.ConfigParser()
        config.read(config_file)
        
        MongoServer = config["Mongo"]["URI"]
        self.MongoDB = config["Mongo"][prefix+"Database"]
        MongoUser = config["Mongo"][prefix+"User"]
        MongoPW = config["Mongo"][prefix+"PW"]

        self.uri = "mongodb://" + MongoUser + ":" + MongoPW + "@" + MongoServer + "/?authSource=" +\
        self.MongoDB + "&authMechanism=SCRAM-SHA-1"
        
        self.target_collection = None
        
    def get_collection_cursor(self, collection):
        client = MongoClient(self.uri)
        self.target_collection = client[self.MongoDB][collection]
    
    def data_streaming_from_collection(self, query={}, batch_size=2000):
        """ save memory space when corpus is extremely large
        """
        if self.target_collection == None:
            raise NoCollectionError

        for doc in self.target_collection.find(query).batch_size(batch_size):
            yield doc
            
class DocumentStream(object):
    def __init__(self, file_path):
        self.file_path = file_path
    
    # __iter__ using on "for" and "enumerate"
    def __iter__(self):
        with open(self.file_path, "r") as rf:
            for doc in rf:
                yield doc.split(" ")

    # implement len function for this class
    # O(n) in run time
    # O(1) in memory
    def __len__(self):
        return sum(1 for e in self.__iter__())

class TweetRawCorpusStream(object):
    def __init__(self, file_path):
        self.file_path = file_path
    
    def __iter__(self):
        with open(self.file_path, "r") as rf:
            for i, line in enumerate(rf):
                # skip header
                if i == 0:
                    continue

                try:
                    a_tweet = RawTweet._make(line.strip().split("\t"))
                    yield a_tweet
                except TypeError:
                    # this is the case which has empty tokens
                    continue
