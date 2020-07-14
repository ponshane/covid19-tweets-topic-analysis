import pandas as pd
from gensim.corpora import Dictionary

from codebase.topic_utilities import dtm_csv_to_pd_df
from codebase.utils import TweetRawCorpusStream

if __name__ == "__main__":
    # Define path
    corpora_path = "./corpora/"
    model_path = "./models/"

    # Variables
    week_start = 18 # the start of the week loop
    week_stop = 27 # the end of the week loop
    topic_num = 25
    top_n_tweets = 20

    # # export representative topical tweets from rolling model

    # wf = open("./representative-tweets-rolling-model.csv", "w")
    # wf.write("Week,Topic,Tweet_ID,Topic%\n")
    # # loop for each week
    # for week_index in range(week_start, week_stop):   
    #     # load meta dataframe 
    #     fileTag = f"Week{week_index}-Tweets-Rolling"
    #     meta = pd.read_csv("{}{}-Meta.csv".format(corpora_path, fileTag))
    #     meta.reset_index()
    #     meta = meta.set_index("position_index")

    #     # load document-topic matrix
    #     dtm = dtm_csv_to_pd_df(f"{model_path}Week{week_index}-Tweets-Rolling-{topic_num}topics-dtm.csv")
    #     meta_aug = meta.join(dtm, on="position_index", how="left")
    #     # loop for each topic
    #     for topic_index in range(0, topic_num):
    #         nL = meta_aug.nlargest(top_n_tweets, columns=topic_index)[["id_str", topic_index]]
    #         nL['id_str']= nL['id_str'].astype(str)
    #         for row in nL.iterrows():
    #             id_str = row[1]["id_str"]
    #             topic_ratio = row[1][topic_index]
    #             wf.write(f"Week{week_index},{topic_index},{id_str},{topic_ratio}\n")
    # wf.close()

    # export representative topical tweets from sliding model

    wf = open("./representative-tweets-sliding-model.csv", "w")
    wf.write("Week,Topic,Tweet_ID,Topic%\n")

    Week_set = ["W17W18", "W18W19", "W19W20", "W20W21", "W21W22", "W22W23",\
        "W23W24", "W24W25", "W25W26"]

    # loop for each week
    for week in Week_set:
        print(f"Start exporting {week}.")
        week_index = week[-2:] # e.g., W10W11 -> 11
        raw_file_path = f"{corpora_path}Week{week_index}-raw-corpus.tsv"
        fileTag = f"{week}-Tweets-Sliding"
        
        dct = Dictionary.load('{}{}.dict'.format(corpora_path,fileTag))
        ids = []
        id_str_list = []
        for _, a_tweet in enumerate(TweetRawCorpusStream(raw_file_path)):
            bow_per_doc = dct.doc2bow(a_tweet.tokens_str.split(","))
            if len(bow_per_doc) > 4:
                ids.append(len(id_str_list))
                id_str_list.append(a_tweet.id_str)
        
        meta = pd.DataFrame.from_dict({"position_index":ids, "id_str":id_str_list})
        meta.reset_index()
        meta = meta.set_index("position_index")
            
        dtm = dtm_csv_to_pd_df(f"{model_path}{fileTag}-{topic_num}topics-dtm.csv")
        
        # size of document should be equal
        assert meta.shape[0] == dtm.shape[0]
        meta_aug = meta.join(dtm, on="position_index", how="left")
        
        # loop for each topic
        for topic_index in range(0, topic_num):
            nL = meta_aug.nlargest(top_n_tweets, columns=topic_index)[["id_str", topic_index]]
            nL['id_str']= nL['id_str'].astype(str)
            for row in nL.iterrows():
                id_str = row[1]["id_str"]
                topic_ratio = row[1][topic_index]
                wf.write(f"Week{week_index},{topic_index},{id_str},{topic_ratio}\n")
    wf.close()