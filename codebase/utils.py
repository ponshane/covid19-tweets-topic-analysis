import time
import os.path
import configparser
from collections import namedtuple, defaultdict
import math

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

class MultipleTweetCorporaBOWStream(object):
    def __init__(self, files, dictionary):
        """ This is a class to prepare a corpus (iterable of list of (wordid, count))
        for gensim.matutils.MmWriter.write_corpus

        files (list of str), each for a filepath of a tweet raw corpus
        dictionary (gensim.corpora.Dictionary)
        """
        self.files = files
        self.dictionary = dictionary
    
    def __iter__(self):
        for file in self.files:
            print(f"Entering {file}.")
            for _, a_tweet in enumerate(TweetRawCorpusStream(file)):
                bow_per_doc = self.dictionary.doc2bow(a_tweet.tokens_str.split(","))
                if len(bow_per_doc) > 4:
                    yield bow_per_doc

def build_freq_table(docs):
    """
    Input
        docs (enumerator), object from TweetRawCorpusStream class
    
    Return
        term_freq_table (dict), key=term, value=term_count
        document_freq_table (dict), key=term, value=#documents of term appearance
        i+1 (int), number of documents
    """
    term_freq_table = defaultdict(int)
    document_freq_table = defaultdict(int)
    # loop for each doc
    for i, a_tweet in docs:
        # check whether a term has shown in a doc or not
        term_appear = defaultdict(int)
        doc = a_tweet.tokens_str.split(",")
        for term in doc:
            
            # if term is not hashtag then continue next term
            if not term.startswith("#"):
                continue
            
            # increase 1 for term_freq_table
            term_freq_table[term] +=1
            
            # increase 1 for document_freq_table when a term first appears in a doc
            if term_appear[term] == 0:
                term_appear[term] +=1
                document_freq_table[term] +=1
    
    return term_freq_table, document_freq_table, i+1

def calculate_tf_idf_table(term_freq_table, document_freq_table, N):
    """
    Input
        term_freq_table (dict), key=term, value=term_count
        document_freq_table (dict), key=term, value=#documents of term appearance
        N (int), number of documents
    Retrun
        tf_idf_table (dict), key=term, value=tf-idf
    """
    tf_idf_table = {}
    all_tf = sum(term_freq_table.values())
    for term, tf in term_freq_table.items():
        df = document_freq_table[term]
        idf = math.log10(N / float(df))
        tf_idf_table[term] = (tf/all_tf) * idf
    return tf_idf_table

def return_top_N_dict_by_value(table, N):
    return dict(sorted(table.items(), key=lambda x: x[1], reverse=True)[:N])