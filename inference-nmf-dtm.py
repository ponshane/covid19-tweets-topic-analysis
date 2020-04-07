import argparse
from gensim.corpora import MmCorpus
from gensim.models.nmf import Nmf
from codebase.topic_utilities import export_dtm 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_topics', type=int, required=True, dest="num_topics",
                        help='num of topics is a necessary to choose the right NMF model')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    args = parser.parse_args()
    
    corpora_path = "./corpora/"
    model_path = "./models/"
    model_suffix = "-{}topics".format(args.num_topics)
    fileTag = args.fileTag
    
    tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))
    nmf = Nmf.load("{}{}{}.model".format(model_path,fileTag,model_suffix))
    export_dtm(nmf=nmf, corpus=tfidf_corpus,\
           out_path="{}{}{}-dtm.csv".format(model_path, fileTag, model_suffix),\
          stop_at=None)