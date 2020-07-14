from gensim.corpora import Dictionary, MmCorpus
from gensim.matutils import MmWriter # this class helps to write one document at a time
from gensim.models.coherencemodel import CoherenceModel

from codebase.utils import MultipleTweetCorporaBOWStream, Timer

import pandas as pd

if __name__ == "__main__":
    corpora_path = "./corpora/"
    fileTag = "Mar2Jun-Tweets" # use the same fileTag as Rolling model's "scan-vocab" step
    output_fname = f"{corpora_path}{fileTag}.mm"
    dct = Dictionary.load('{}{}.dict'.format(corpora_path,fileTag))
    model_path = "./models/"
    num_topics = 25
    summary_suffix = f"-Tweets-Sliding-{num_topics}topics-summary.csv"

    """[This block is used for generating mmcorpus of all references corpus]
    collections = "Week10 Week11 Week12 Week13 Week14 Week15 Week16 Week17 Week18 Week19 Week20 Week21 Week22 Week23 Week24 Week25 Week26".split(" ")
    files = [f"{corpora_path}{week}-raw-corpus.tsv" for week in collections]

    corpus = MultipleTweetCorporaBOWStream(files, dct)
    with Timer():
        MmWriter.write_corpus(fname=output_fname, corpus=corpus)
    """
    
    # read topics for evaluating
    Weeks = "W10 W10W11 W11W12 W12W13 W13W14 W14W15 W15W16 W16W17 W17W18 W18W19 W19W20 W20W21 W21W22 W22W23 W23W24 W24W25 W25W26".split(" ")
    topics = []
    for week in Weeks:
        summary_file = f"{model_path}{week}{summary_suffix}"
        df = pd.read_csv(summary_file)
        list_relevant_words = df.relevant_words.to_list()
        for each_relevant_words in list_relevant_words:
            topics.append(each_relevant_words.split(" "))
    
    # test block
    # coherences = []
    # for week in Weeks:
    #     coherences += [week[-2:]]*num_topics

    r_corpus = MmCorpus(output_fname)
    with Timer():
        cm = CoherenceModel(topics=topics, corpus=r_corpus,\
             dictionary=dct, coherence='u_mass')
        coherences = cm.get_coherence_per_topic()
    
    # write results
    wf = open("./coherence-evals.txt", "w")
    for i, week in enumerate(Weeks):
        wf.write(f"{week}\n")
        cs = coherences[i*num_topics:(i+1)*num_topics]
        for c in cs:
             wf.write(f"{c}\n")
    wf.close()