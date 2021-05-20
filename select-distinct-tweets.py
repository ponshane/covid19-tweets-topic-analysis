import pandas as pd
import os

import json
from json.decoder import JSONDecodeError

def extract_json_from_file(file_path):
    with open(file_path, "r") as rf:
        return json.loads(rf.read())

if __name__ == "__main__":
    
    """ 
    Step 1, store the distinct tweets' IDs
    """
    # fixed params
    corpora_path = "./corpora/"

    # params
    fileTag_list = ["First-and-SecondWeek-Tweets-Rolling","Third-and-FourthWeek-Tweets-Rolling",\
        "Fifth-and-SixthWeek-Tweets-Rolling", "Seventh-and-EighthWeek-Tweets-Rolling"]

    start_list = ["2020-12-16","2020-12-31", "2021-01-15", "2021-01-30"]
    end_list = ["2020-12-31", "2021-01-15", "2021-01-30", "2021-02-14"]

    # store all tweet IDs as a set
    whole_ids_set = set()

    for fileTag, start, end in zip(fileTag_list, start_list, end_list):
        
        print("Start {} from {} to {}.".format(fileTag, start, end))

        metadata_filename = "{}{}-Meta.csv".format(corpora_path, fileTag)
        # Read back data from csv files
        metadata = pd.read_csv(metadata_filename)
        ids_set = set(metadata["id_str"])
        whole_ids_set.update(ids_set)

        num_metadata = metadata.shape[0]
        num_distinct_tweets = len(ids_set)
        print("Number of redundant tweets: {} and number of distinct tweets: {}".format(num_metadata-num_distinct_tweets, num_distinct_tweets))
    
    """ 
    Step 2, export necessary tweets (those distinct ones)
    """
    folders = [i for i in range(273, 333)] # 60 days tweets
    base_dir = "/home/ponshane/Data/Corona_Vaccine_Tweets"

    existing_ids = set()
    id_list = []
    date_list = []
    text_list = []

    for folder in folders:
        print(f"Start processing files in {folder}")
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(base_dir, str(folder))):
            # print how many files in the folder
            print(f"{len(filenames)} files in {dirpath}")
            for eachfile in filenames:
                eachfile_path = os.path.join(dirpath, eachfile)
                
                try:
                    # retrieve list of json objects from the file
                    j_obj = extract_json_from_file(eachfile_path)
                except (JSONDecodeError, UnicodeDecodeError):
                    print("There is a decoding issue in {}".format(eachfile_path))
                    continue
            
                for j in j_obj:
                    a_id_str = int(j['id_str'])
                    if a_id_str in whole_ids_set and a_id_str not in existing_ids:
                        id_list.append(a_id_str)
                        date_list.append(j['created_at'])
                        # noise removal & simple tokenization
                        text_list.append(j['full_text'])
                        existing_ids.add(a_id_str)

    data = {"id_str": id_list,\
    "created_at": date_list,\
        "full_text": text_list}
    df = pd.DataFrame(data)
    df.to_pickle("./corpora/distinct_tweets/distinct-tweets.pkl")