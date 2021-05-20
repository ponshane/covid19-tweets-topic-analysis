# import argparse

from gensim.corpora import Dictionary, MmCorpus
from gensim.models.nmf import Nmf
from gensim.models import TfidfModel

from codebase.utils import TweetRawCorpusStream
from codebase.topic_utilities import export_dtm 

if __name__ == "__main__":
    
    corpora_path = "./corpora/"
    model_path = "./models/"
    num_topics = 50
    model_suffix = "-{}topics".format(num_topics)
    modelTag = "Seventh-and-EighthWeek-Tweets-Rolling"
    
    nmf = Nmf.load("{}{}{}.model".format(model_path,modelTag,model_suffix))

    fileTag_list = ["Fifth-and-SixthWeek-Tweets-Rolling"]
    for fileTag in fileTag_list:
        tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))
        export_dtm(nmf=nmf, corpus=tfidf_corpus,\
            out_path="{}{}{}-dtm.csv".format(model_path, fileTag, model_suffix),\
            stop_at=None)