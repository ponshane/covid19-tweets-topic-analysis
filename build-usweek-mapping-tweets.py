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
    week_bounds["FirstWeek_March"] = {"start":"2020-03-01 00:00:00.000000",
                                  "end":"2020-03-07 23:59:59.000000"}
    week_bounds["SecondWeek_March"] = {"start":"2020-03-08 00:00:00.000000",
                                    "end":"2020-03-14 23:59:59.000000"}
    week_bounds["ThirdWeek_March"] = {"start":"2020-03-15 00:00:00.000000",
                                    "end":"2020-03-21 23:59:59.000000"}
    week_bounds["FourthWeek_March"] = {"start":"2020-03-22 00:00:00.000000",
                                    "end":"2020-03-28 23:59:59.000000"}
    week_bounds["FirstWeek_April"] = {"start":"2020-03-29 00:00:00.000000",
                                    "end":"2020-04-04 23:59:59.000000"}
    week_bounds["SecondWeek_April"] = {"start":"2020-04-05 00:00:00.000000",
                                    "end":"2020-04-11 23:59:59.000000"}
    week_bounds["ThirdWeek_April"] = {"start":"2020-04-12 00:00:00.000000",
                                    "end":"2020-04-18 23:59:59.000000"}
    week_bounds["FourthWeek_April"] = {"start":"2020-04-19 00:00:00.000000",
                                    "end":"2020-04-25 23:59:59.000000"}

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
            print(f"\tScanned {collection} with {sizeCorpus} tweets.")
            sizeOfWeek += sizeCorpus
        wf.close()
        print(f"{week} with {sizeOfWeek} tweets in total.")