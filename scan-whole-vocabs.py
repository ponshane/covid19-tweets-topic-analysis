"""
This module is used for rolling-based topic model, which needs whole vocabulary
to initialize size of vocabulary. With this purpose, as the corpus is too large
(across too many collections), prepare-nmf-corpus.py is not appropriate for building
initial vocabulary dictionary, since it also has functionality to transform tf-idf corpus.
"""
from codebase.utils import TweetRawCorpusStream, Timer

from gensim.corpora import Dictionary

import argparse
import pickle

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', type=str, nargs="+", required=True, dest="collections",
                        help='give a list of week name, e.g., FirstWeek_March')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    args = parser.parse_args()

    fileTag = args.fileTag
    collections = args.collections
    
    corpora_path = "./corpora/"

    #### Step 1, build dictionary object ####
    print("Start to build dictionary object.")
    dct = Dictionary()
    # use Timer to print elapsed time
    with Timer():
        for each_collection in collections:
            print("Reading the corpus for {}".format(each_collection))
            file_path = f"{corpora_path}{each_collection}-raw-corpus.tsv"
            for i, a_tweet in enumerate(TweetRawCorpusStream(file_path)):
                token_f = [x for x in a_tweet.tokens_str.split(",") if len(x) > 1]
                dct.add_documents([token_f], prune_at=None)
            sizeofCorpus = i-1
            print(f"Totally {sizeofCorpus} tweets in {each_collection}.")
    print("Original size of vocabs: {}".format(len(dct)))
    # control the vocabulary
    dct.filter_extremes(no_below=40, no_above=0.5, keep_n=len(dct), keep_tokens=None)
    print("Truncated size of vocabs: {}".format(len(dct)))

    #### Step 2, export model ####
    dct.save('{}{}.dict'.format(corpora_path,fileTag))