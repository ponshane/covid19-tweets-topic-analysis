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
    keywords = ["Sars-CoV-2", "COVID-19", "corona virus"]
    Weeks = ["Week10", "Week11", "Week12", "Week13", "Week14", "Week15",\
        "Week16", "Week17", "Week18", "Week19", "Week20", "Week21", "Week22", "Week23",\
            "Week24", "Week25", "Week26", "Week27"]
    
    num_count = dict()
    for keyword in keywords:
        keyword = keyword.lower()
        num_count[keyword] = 0
        for each_week in Weeks:
            conn.get_collection_cursor(each_week)
            n_docs = conn.target_collection.count_documents(make_text_query(keyword))
            num_count[keyword] += n_docs
            print(f"{keyword}@{each_week}: {n_docs}")
            
    print(num_count)