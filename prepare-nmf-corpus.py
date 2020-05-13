from codebase.utils import TweetRawCorpusStream, Timer

from gensim.models import TfidfModel
from gensim.corpora import Dictionary, MmCorpus

import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', type=str, nargs="+", required=True, dest="collections",
                        help='give a list of week name, e.g., FirstWeek_March')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    parser.add_argument('-pd', '--preDictTag', type=str, dest="preDictTag",
                        help='if pd exisit, it uses preDict instead')                   
    args = parser.parse_args()

    fileTag = args.fileTag
    collections = args.collections
    preDictTag = args.preDictTag
    
    corpora_path = "./corpora/"
    model_path = "./models/"

    #### Step 1, build dictionary object ####
    if preDictTag == None:
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
    elif preDictTag != None:
        dct = Dictionary.load('{}{}.dict'.format(corpora_path,preDictTag))

    #### Step 2, apply Tf-IDF representation ####
    bow_corpus = []
    meta_wf = open("{}{}-Meta.csv".format(corpora_path, fileTag),"w")
    meta_wf.write("position_index,id_str,created_time\n")

    # use Timer to print elapsed time
    with Timer():
        for each_collection in collections:
            print("Transforming the corpus for {}".format(each_collection))
            file_path = f"{corpora_path}{each_collection}-raw-corpus.tsv"
            for i, a_tweet in enumerate(TweetRawCorpusStream(file_path)):
                # gensim's Dictionary.doc2bow will ignore words that are not in dictionary by default
                bow_per_doc = dct.doc2bow(a_tweet.tokens_str.split(","))
                if len(bow_per_doc) > 4:
                    timestamp = a_tweet.created_at
                    id_str = a_tweet.id_str
                    meta_wf.write("{},{},{}\n".format(len(bow_corpus), id_str, timestamp))
                    bow_corpus.append(bow_per_doc)
    meta_wf.close()

    tfidf_model = TfidfModel(bow_corpus)  # fit model
    tfidf_corpus = tfidf_model[bow_corpus]

    #### Step 3, export model ####
    if preDictTag == None:
        dct.save('{}{}.dict'.format(corpora_path,fileTag))
    MmCorpus.serialize('{}{}-tf-idf.mm'.format(corpora_path,fileTag), tfidf_corpus)
    tfidf_model.save('{}{}-tf-idf.model'.format(model_path,fileTag))