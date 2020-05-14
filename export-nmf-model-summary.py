from collections import Counter
import argparse

from codebase.topic_utilities import rerank_topic_words_by_relevance
from codebase.topic_utilities import dtm_csv_to_pd_df, calculate_topic_ratios
from codebase.utils import Timer

from gensim.models.nmf import Nmf
from gensim.corpora import MmCorpus

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_topics', type=int, required=True, dest="num_topics",
                        help='num of topics we want to infer from NMF model')
    parser.add_argument('-f', '--fileTag', type=str, required=True, dest="fileTag",
                        help='fileTag as prefix for all exported files')
    parser.add_argument('-l', '--_lambda', type=float, dest="_lambda",
                        default=0.6, help='threshold to penalize high frequent words')
    parser.add_argument('-t', '--top_words', type=int, dest="top_words",
                        default=30, help='#words appearing in each topic')
    parser.add_argument('-idtm', '--infer_dtm', type=int, dest="infer_dtm",
                        default=1, help='whether to infer dtm, 1 for true and 0 for false')           
    args = parser.parse_args()

    num_topics = args.num_topics
    fileTag = args.fileTag
    _lambda = args._lambda
    top_words = args.top_words
    infer_dtm = args.infer_dtm
    corpora_path = "./corpora/"
    model_path = "./models/"
    model_suffix = "-{}topics".format(num_topics)

    print("Start to rerank topic words.")
    with Timer():
        tfidf_corpus = MmCorpus('{}{}-tf-idf.mm'.format(corpora_path,fileTag))
        # as gensim.Dictionary's cfs has unmapped index after filter_extreme
        # so I re-count the word frequency to estimate empirical word probability p(w)
        word_cnt = Counter()
        for doc in tfidf_corpus:
            tokens = [word for word, _ in doc]
            word_cnt.update(tokens)

        nmf = Nmf.load("{}{}{}.model".format(model_path,fileTag,model_suffix))
        rerank_topic_words = rerank_topic_words_by_relevance(model=nmf, word_cnt=word_cnt,\
            _lambda=_lambda)

    if infer_dtm == 1:
        print("Start to calculate topic ratios.")
        with Timer():
            doc_topic_matrix_filename = "{}{}{}-dtm.csv".format(model_path, fileTag, model_suffix)
            dtm = dtm_csv_to_pd_df(doc_topic_matrix_filename)
            topic_ratios = calculate_topic_ratios(dtm)

    summary_filename = "{}{}{}-summary.csv".format(model_path, fileTag, model_suffix)
    print("Start to write summary file. Please find {}.".format(summary_filename))
    with open(summary_filename, "w") as wf:
        if infer_dtm == 1:
            wf.write("topic_id,topic_ratio,relevant_words\n")
            for topic_id in range(dtm.shape[1]):
                wf.write("{},{},{}\n".format(topic_id, topic_ratios[topic_id],\
                    " ".join(
                        [word for word, _ in rerank_topic_words[topic_id][:top_words]]
                        )))
        elif infer_dtm == 0:
            wf.write("topic_id,relevant_words\n")
            for topic_id in range(num_topics):
                wf.write("{},{}\n".format(topic_id,\
                    " ".join(
                        [word for word, _ in rerank_topic_words[topic_id][:top_words]]
                        )))