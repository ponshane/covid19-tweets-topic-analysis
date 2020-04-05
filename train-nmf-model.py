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
    args = parser.parse_args()

    num_topics = args.num_topics
    fileTag = args.fileTag
    corpora_path = "./corpora/"
    model_path = "./models/"

    #### Step 1, Load Corpus ####
    dct = Dictionary.load('{}{}.dict'.format(corpora_path,fileTag))
    tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))

    #### Step 2, train NMF to extract topic patterns ####
    nmf = Nmf(tfidf_corpus, id2word=dct, num_topics=num_topics)

    #### Step 3, export model ####
    model_suffix = "-{}topics".format(num_topics)
    nmf.save("{}{}{}.model".format(model_path,fileTag,model_suffix))