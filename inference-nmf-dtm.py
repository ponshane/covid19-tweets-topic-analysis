import argparse

from gensim.corpora import Dictionary, MmCorpus
from gensim.models.nmf import Nmf
from gensim.models import TfidfModel

from codebase.utils import TweetRawCorpusStream
from codebase.topic_utilities import export_dtm 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_topics', type=int, required=True, dest="num_topics",
                        help='num of topics is a necessary to choose the right NMF model')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    parser.add_argument('-tw', '--target_week', type=str, dest="target_week", default=None,
                        help='target_week, which only requires for sliding model, is the specific week for inference')
    args = parser.parse_args()
    
    corpora_path = "./corpora/"
    model_path = "./models/"
    model_suffix = "-{}topics".format(args.num_topics)
    fileTag = args.fileTag
    target_week = args.target_week
    
    nmf = Nmf.load("{}{}{}.model".format(model_path,fileTag,model_suffix))

    # if there is no specific target week (e.g., for rolling model)
    if target_week == None:
        tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))
        export_dtm(nmf=nmf, corpus=tfidf_corpus,\
            out_path="{}{}{}-dtm.csv".format(model_path, fileTag, model_suffix),\
            stop_at=None)
    else:
        # load pre-fitted dictionary
        dct = Dictionary.load('{}{}.dict'.format(corpora_path,fileTag))
        # load pre-fitted tfidf model
        tfidf_model = TfidfModel.load("{}{}-tf-idf.model".format(model_path,fileTag))
        # load raw-corpus 
        file_path = f"{corpora_path}{target_week}-raw-corpus.tsv"
        # define list for storing bag-of-words
        bow_corpus = []
        for i, a_tweet in enumerate(TweetRawCorpusStream(file_path)):
            # gensim's Dictionary.doc2bow will ignore words that are not in dictionary by default
            bow_per_doc = dct.doc2bow(a_tweet.tokens_str.split(","))
            if len(bow_per_doc) > 4:
                bow_corpus.append(bow_per_doc)
        # transform the corpus
        tfidf_corpus = tfidf_model[bow_corpus]
        # save memory
        del dct, tfidf_model, bow_corpus
        # export_dtm
        export_dtm(nmf=nmf, corpus=tfidf_corpus,\
            out_path="{}{}{}-dtm.csv".format(model_path, fileTag, model_suffix),\
            stop_at=None)