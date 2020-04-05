import re
import tqdm
import pandas as pd
import matplotlib.pyplot as plt

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