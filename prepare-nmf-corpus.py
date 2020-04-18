from codebase.utils import MongoConnector, Timer

from gensim.models import TfidfModel
from gensim.corpora import Dictionary, MmCorpus

import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', type=str, nargs="+", required=True, dest="collections",
                        help='give a list of collection name')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files') 
    parser.add_argument('-pd', '--preDictTag', type=str, dest="preDictTag",
                        help='fileTag as prefix for all exported files')                   
    args = parser.parse_args()

    fileTag = args.fileTag
    collections = args.collections
    preDictTag = args.preDictTag
    
    query = {"tokens":{"$exists": True}}
    corpora_path = "./corpora/"
    model_path = "./models/"

    conn = MongoConnector("./config.ini")

    #### Step 1, build dictionary object ####
    if preDictTag == None:
        print("Start to build dictionary object.")
        dct = Dictionary()
        # use Timer to print elapsed time
        with Timer():
            for each_collection in collections:
                print("Reading the corpus from {}".format(each_collection))
                conn.get_collection_cursor(each_collection)
                for doc in conn.data_streaming_from_collection(query=query):
                    token_f = [x for x in doc["tokens"] if len(x) > 1]
                    dct.add_documents([token_f])
        
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
            print("Transforming the corpus from {}".format(each_collection))
            conn.get_collection_cursor(each_collection)
            for doc in conn.data_streaming_from_collection(query=query):
                # gensim's Dictionary.doc2bow will ignore words that are not in dictionary by default
                bow_per_doc = dct.doc2bow(doc["tokens"])
                if len(bow_per_doc) > 4:
                    timestamp = doc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    meta_wf.write("{},{},{}\n".format(len(bow_corpus), doc["id_str"], timestamp))
                    bow_corpus.append(bow_per_doc)
    meta_wf.close()

    tfidf_model = TfidfModel(bow_corpus)  # fit model
    tfidf_corpus = tfidf_model[bow_corpus]

    #### Step 3, export model ####
    if preDictTag == None:
        dct.save('{}{}.dict'.format(corpora_path,fileTag))
    MmCorpus.serialize('{}{}-tf-idf.mm'.format(corpora_path,fileTag), tfidf_corpus)
    tfidf_model.save('{}{}-tf-idf.model'.format(model_path,fileTag))