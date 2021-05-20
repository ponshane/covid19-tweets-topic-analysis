"""
Created on Mon Mar 22 15:35:18 2021

@author: ponshane
"""
import pandas as pd
from gensim.corpora import Dictionary

from codebase.topic_utilities import dtm_csv_to_pd_df
from codebase.utils import TweetRawCorpusStream

if __name__ == "__main__":
    # Define path
    corpora_path = "./corpora/"
    model_path = "./models/"

    # Variables
    WEEKS = ["firstWeek", "secondWeek", "thirdWeek"]
    topic_num = 25
    top_n_tweets = 50

    # export representative topical tweets from rolling model

    wf = open("./representative-tweets-rolling-model.csv", "w")
    wf.write("Week,Topic,Tweet_ID,Topic%\n")
    # loop for each week
    for week_index in WEEKS:   
        # load meta dataframe 
        fileTag = f"{week_index}-Tweets-Rolling"
        meta = pd.read_csv("{}{}-Meta.csv".format(corpora_path, fileTag))
        meta.reset_index()
        meta = meta.set_index("position_index")

        # load document-topic matrix
        dtm = dtm_csv_to_pd_df(f"{model_path}{week_index}-Tweets-Rolling-{topic_num}topics-dtm.csv")
        meta_aug = meta.join(dtm, on="position_index", how="left")
        # loop for each topic
        for topic_index in range(0, topic_num):
            nL = meta_aug.nlargest(top_n_tweets, columns=topic_index)[["id_str", topic_index]]
            nL['id_str']= nL['id_str'].astype(str)
            for row in nL.iterrows():
                id_str = row[1]["id_str"]
                topic_ratio = row[1][topic_index]
                wf.write(f"{week_index},{topic_index},{id_str},{topic_ratio}\n")
    wf.close()