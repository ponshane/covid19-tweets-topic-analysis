from codebase.utils import MongoConnector
from bson.tz_util import FixedOffset
from datetime import datetime
import pickle

def make_time_query(start, end):
    query = {}
    query["$and"] = [
        {
            u"tokens": {
                u"$exists": True
            }
        },
        {
            u"created_at": {
                u"$gte": datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo = FixedOffset(-240, "-0400"))
            }
        },
        {
            u"created_at": {
                u"$lte": datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo = FixedOffset(-240, "-0400"))
            }
        }]
    return query

if __name__ == "__main__":

    week_bounds = dict()
    with open("./week-time-mapping.csv", "r") as rf:
        for i, each_entry in enumerate(rf):
            # skip the header
            if i == 0:
                continue
            week,start,end = each_entry.strip().split(",")
            week_bounds[week] = {"start":start, "end":end}
    
    conn = MongoConnector("./config.ini")
    collections = list(week_bounds.keys())

    corpora_path = "./corpora/"

    for week, weekValue in week_bounds.items():
        start = weekValue.get("start")
        end = weekValue.get("end")
        print(f"Start to build usweek mapping tweets for {week}")
        wf = open(f"{corpora_path}{week}-raw-corpus.tsv", "w")
        wf.write("id_str\tcreated_at\ttokens\n")
        sizeOfWeek = 0
        for collection in collections:
            conn.get_collection_cursor(collection)
            query = make_time_query(start, end)
            cursor = conn.target_collection.find(query).batch_size(5000)
            sizeCorpus = 0
            for doc in cursor:
                id_str = doc["id_str"]
                created_at = doc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                tokens = ",".join(doc["tokens"])
                wf.write(f"{id_str}\t{created_at}\t{tokens}\n")
                sizeCorpus +=1
            cursor.close()
            # print(f"\tScanned {collection} with {sizeCorpus} tweets.")
            sizeOfWeek += sizeCorpus
        wf.close()
        print(f"{week} with {sizeOfWeek} tweets in total.")