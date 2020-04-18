from gensim.models.nmf import Nmf
from gensim.corpora import Dictionary, MmCorpus

import argparse
import logging
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_topics', type=int, required=True, dest="num_topics",
                        help='num of topics we want to infer from NMF model')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    parser.add_argument('-pd', '--preDictTag', type=str, dest="preDictTag",
                        help='fileTag as prefix for all exported files') 
    parser.add_argument('-pf', '--preFileTag', type=str, dest="preFileTag",
                        help='preFileTag used to select previous nmf model')                 
    args = parser.parse_args()

    num_topics = args.num_topics
    fileTag = args.fileTag
    preFileTag = args.preFileTag
    preDictTag = args.preDictTag
    corpora_path = "./corpora/"
    model_path = "./models/"
    model_suffix = "-{}topics".format(num_topics)

    #### Step 1, Load Corpus ####
    if (preFileTag == None) and (preDictTag == None):
        dct = Dictionary.load('{}{}.dict'.format(corpora_path,fileTag))
    # for rolling way first built model
    elif (preFileTag == None) and (preDictTag != None):
        dct = Dictionary.load('{}{}.dict'.format(corpora_path,preDictTag))

    tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))

    #### Step 2, train NMF to extract topic patterns ####
    if preFileTag == None:
        nmf = Nmf(tfidf_corpus, id2word=dct, num_topics=num_topics)
    elif preFileTag != None:
        nmf = Nmf.load("{}{}{}.model".format(model_path,preFileTag,model_suffix))
        nmf.update(tfidf_corpus)

    #### Step 3, export model ####
    nmf.save("{}{}{}.model".format(model_path,fileTag,model_suffix))