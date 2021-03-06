import re
import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import log

def make_perplexity_plots(log_path, output_path):
    # https://stackoverflow.com/questions/37570696/how-to-monitor-convergence-of-gensim-lda-model

    p = re.compile("(-*\d+\.\d+) per-word .* (\d+\.\d+) perplexity")
    matches = [p.findall(line) for line in open(log_path)]

    # not every line has perplexity information
    matches = [m for m in matches if len(m) > 0]

    # pick match tuple "There is only one match in one line"
    tuples = [t[0] for t in matches]

    # furthermore to extract likelihood and perplexity
    liklihood = [float(t[0]) for t in tuples]
    perplexity = [float(t[1]) for t in tuples]

    iters = list(range(0,len(tuples)))
    plt.plot(iters,perplexity,c="black")
    plt.ylabel("perplexity")
    plt.xlabel("iteration")
    plt.title("Topic Model Convergence")
    plt.grid()
    plt.savefig(output_path)
    plt.close()
    
def format_topics_df(nmf, corpus, Meta, stop_at=10000):
    """ helps to create topical dataframe 
    that each row represents each document and has "dominant topic", "proportion of dominant topic",
    and all "Meta" information.
    
    Args:
        nmf: (gensim.models.nmf.Nmf instance)
        corpus: (iterable of iterable of (int, float)), corpus in BoW format
        Meta: (dict), each key contains a list of a meta information, e.g., date, id, title
    
    Return:
        panda.DataFrame
    """
    
    assert len(corpus) == len(Meta["id_str"]) == len(Meta["created_date"])
    
    topics_df = pd.DataFrame()

    # Estimate the dominant topic of each document
    topic_index_list = []
    topic_porp_list = []
    for i, topic_contributions in enumerate(nmf[corpus]):
        
        if i % 1000 == 0:
            print(i)
            
        if i == stop_at:
            break
        
        sorted_topic_contributions = sorted(topic_contributions, key=lambda x: x[1], reverse=True)
        topic_index, topic_porp = sorted_topic_contributions[0]
        topic_index_list.append(int(topic_index))
        topic_porp_list.append(round(topic_porp,4))
    
    topic_index_list = pd.Series(topic_index_list)
    topic_porp_list = pd.Series(topic_porp_list)
    id_str = pd.Series(Meta["id_str"][:stop_at])
    created_date = pd.Series(Meta["created_date"][:stop_at])
    
    topics_df = pd.concat([id_str, created_date, topic_index_list, topic_porp_list], axis=1)
    topics_df.reset_index()
    topics_df.columns = ['id_str', 'created_date', 'dominant_topic', 'perc_contribution']
    
    return topics_df

def export_dtm(nmf, corpus, out_path, stop_at=None):
    """ helps to export document-topic matrix as csv
    
    Args:
        nmf: (gensim.models.nmf.Nmf instance)
        corpus: (iterable of iterable of (int, float)), corpus in BoW format
        out_path: (str) the path of export file
        stop_at: (int) #document you want to infer
    
    Return:
        no return as it writes csv
    """
    
    if stop_at == None:
        stop_at = len(corpus)
        pbar = tqdm.tqdm(total=len(corpus))
    else:
        pbar = tqdm.tqdm(total=stop_at)
        
    wf = open(out_path,"w")
    wf.write("position_index,topic_id,topic_weight\n")
    # the below line takes time to inference each document
    for i, topic_contributions in enumerate(nmf[corpus]):
            
        if i == stop_at:
            break
        
        for topic_id, topic_weight in topic_contributions:
            wf.write("{},{},{}\n".format(i, topic_id, round(topic_weight,3)))
        pbar.update(1)
    pbar.close()
    wf.close()
    
def _relevance(word_contribution, word_prob, _lambda):
    """ calculate relevance score
    
    Args:
        word_contribution (float): p(word|topic)
        word_prob (float): p(word)
        _lambda (float): the threshold to penalize high frequency word
    Return 
        (float): relevance score
    """
    if word_contribution < 1e-8:
        word_contribution = 1e-8
    if word_prob > 0:
        return _lambda * log(word_contribution) + (1-_lambda)*log(word_contribution/word_prob)
    else:
        return -100

def rerank_topic_words_by_relevance(model, word_cnt, _lambda):
    """ rerank the topic words by relevance score
    
    Args:
        model (gensim.models.nmf.Nmf instance):
        word_cnt (collections.Counter instance):
        _lambda (float): the threshold to penalize high frequency word
    Return:
        (dict): {topicId: [(word1, rel1), ...]}
    """
    # total word frequency
    N = sum(word_cnt.values())
    # number of topics
    num_topic = model.get_topics().shape[0]
    rerank_topic_words = dict()
    for topic_idx in range(num_topic):
        # select all word contribution from a topic
        origina_word_rank = model.show_topic(topicid=topic_idx,topn=len(word_cnt), normalize=True)
        # calculate the relevance score of each topic
        # value == p(word|topic) == word_contribution
        # p(w) is estimated by empirical distribution: word_cnt[model.id2word.token2id[word]]/N
        rerank_word_rank = [(word,_relevance(value, (word_cnt[model.id2word.token2id[word]]/N), _lambda))
                            for word, value in origina_word_rank]
        rerank_topic_words[topic_idx] = sorted(rerank_word_rank, key=lambda x: x[1], reverse=True)
    return rerank_topic_words

def dtm_csv_to_pd_df(dtm_csv_file):
    """ read dtm csv and transform to pandas.Dataframe 
    
    Args:
        dtm_csv_file (str): filename of csv file
    Return:
        (pandas.Dataframe): with shape(num_doc, num_topic)
    """
    dtm = pd.read_csv(dtm_csv_file)
    # Reorient from long to wide
    dtm = dtm.pivot(index='position_index', columns='topic_id',\
                   values='topic_weight').fillna(0)
    # Normalize each row as a valid probability distribution
    dtm = dtm.div(dtm.sum(axis=1), axis=0)
    return dtm

def calculate_topic_ratios(dtm):
    """ calculate topic ratios
    
    Args:
        dtm (pandas.Dataframe):  with shape(num_doc, num_topic)
    Return:
        (dict): {"topic_idx":"XX.XX%", ...}
    """
    N = dtm.shape[0]
    topic_ratios = dict()
    for topic_idx in range(dtm.shape[1]):
        topic_ratios[topic_idx] = "{:.2%}".format(sum(dtm[topic_idx]) / N)
    return topic_ratios

def jaccard_similarity(list1, list2):
    """calculate jaccard index between two lists

    Arguments:
        list1 {str,list} -- string where each word is split by SEP, or list of words
        list2 {str,list} -- same as list1

    Raises:
        TypeError: only accept str or list as input

    Returns:
        float -- jaccard index between two word lists
    """
    if type(list1) == str and type(list2) == str:
        list1 = list1.split(" ")
        list2 = list2.split(" ")
    elif type(list1) != list and type(list2) != list:
        raise TypeError
    
    s1 = set(list1)
    s2 = set(list2)
    
    return len(s1.intersection(s2)) / len(s1.union(s2))

def calculate_jaccard_matrix_between_models(dict1, dict2):
    """ calculate jaccard matrix between two sets of topics

    Arguments:
        dict1 {dict} -- where key is topic_index of model1, and value is a list of topic words (or string)
        dict2 {dict} -- same as dict1, but for model1

    Returns:
        np.array -- matrix with shape(num_topics_of_model1, num_topics_of_model2)
    """
    jaccard_matrix = list()
    
    for i in range(len(dict1)):
        i_words = dict1[i]
        each_row = []
        for j in range(len(dict2)):
            j_words = dict2[j]
            each_row.append(jaccard_similarity(i_words, j_words))
        # when complete each row, then append back to matrix
        jaccard_matrix.append(np.asarray(each_row))
        
    return np.vstack(jaccard_matrix)

def pick_similar_topic_from_past(jaccard_matrix):
    """ select the most similar topic from model1, given each topic of model2 as query  

    Arguments:
        jaccard_matrix {np.array} -- matrix with shape(num_topics_of_model1, num_topics_of_model2)
    """
    for idx in range(jaccard_matrix.shape[1]):
        maxv = np.max(jaccard_matrix[:,idx])
        max_idx = np.argmax(jaccard_matrix[:,idx])
        print(f'{max_idx} {maxv}')