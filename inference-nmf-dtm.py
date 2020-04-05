import argparse
from gensim.corpora import MmCorpus
from gensim.models.nmf import Nmf
from codebase.topic_utilities import export_dtm 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--corpus', type=str, required=True,\
                        dest="corpus",help='give a corpus path')
    parser.add_argument('-m', '--model', type=str, required=True, dest="model",
                        help='give a nmf model path')
    parser.add_argument('-o', '--out_path', type=str, required=True, dest="out_path",
                        help='give a path+file_name.csv for output file')
    args = parser.parse_args()
    
    tfidf_corpus = MmCorpus(args.corpus)
    nmf = Nmf.load(args.model)
    export_dtm(nmf=nmf, corpus=tfidf_corpus,\
           out_path=args.out_path,\
          stop_at=None)