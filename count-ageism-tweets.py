from codebase.utils import MongoConnector

def make_text_query(keyword):
    
    q = { 
            "$text" : { 
                "$search" : f"\"{keyword}\"", 
                "$language" : "en"
            }
    }
    
    return q

if __name__ == "__main__":
    conn = MongoConnector("./config.ini")
    
    keywords = ["Old people", "Elderly", "Ageism", "Ageist", "Older adults", "Grumpy old people"]
    Weeks = ["FirstWeek_March", "SecondWeek_March", "ThirdWeek_March", "FourthWeek_March", "FirstWeek_April", "SecondWeek_April", "ThirdWeek_April", "FourthWeek_April"]
    
#     num_count = dict()
#     for keyword in keywords:
#         keyword = keyword.lower()
#         num_count[keyword] = 0
#         for each_week in Weeks:
#             conn.get_collection_cursor(each_week)
#             n_docs = conn.target_collection.count_documents(make_text_query(keyword))
#             num_count[keyword] += n_docs
#             print(f"{keyword}@{each_week}: {n_docs}")
            
#     print(num_count)
    
    num_count = dict()
    for keyword in keywords:
        keyword = keyword.lower()
        num_count[keyword] = 0
        flag = keyword.replace(" ", "-")
        wf = open(f"export/{flag}-tweets.tsv", "w")
        wf.write("No\tCreated_at\tText\n")
        for each_week in Weeks:
            conn.get_collection_cursor(each_week)
            docs = conn.target_collection.find(make_text_query(keyword),\
                                              no_cursor_timeout=True)
            for i, doc in enumerate(docs):
                if i % 1000 == 0:
                    print(f"{keyword}@{each_week}: {i}")
                num_count[keyword] += 1
                created_at = doc["created_at"]
                text = doc["text"].replace("\n", " ")
                wf.write(f"{i}\t{created_at}\t{text}\n")

        wf.close()
        docs.close()
        cnt = num_count[keyword]
        print(f"Finished {keyword}: {cnt} tweets.")