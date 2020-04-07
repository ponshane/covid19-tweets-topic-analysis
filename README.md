# Data Acquisition & Preprocessing
1. I use [streaming API of Twitter](https://developer.twitter.com/en/docs/tweets/filter-realtime/overview) to collect tweets containing keywords "covid19" or "#covid19". And, I monitor this stream from first week of March.
2. To avoid from considering the duplicated contents, e.g., retweets, quote tweet, I use `parse-tweets.py` to filter out those tweets. `retrieve-details-of-tweets.py` is then used to retrieve details of each tweet by [statuses/lookup api](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup) because I find texts of tweets returned by streaming API are truncated...
    - Note that `retrieve-details-of-tweets.py` also help do text preprocessing 
    - I use mongodb to store every tweet with its meta information and NLP results.
3. I will share the id list of these tweets ASAP. If you are interested in analyzing these tweets, you can use [statuses/lookup api](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup) to pull the contents back and preprocess by the similar strategy implemented in `retrieve-details-of-tweets.py`.
4. Number of English tweets I have (will keep update!):
    - Week10(Mar. 2 ~ Mar. 8) of 2020:     1.49M 
    - Week11(Mar. 9 ~ Mar. 15) of 2020:   3.92M 
    - Week12(Mar. 16 ~ Mar. 22) of 2020: 4.03M 
    - Ｗeek13(Mar. 23 ~ Mar. 29) of 2020: 4.24M 

# Procedure for Topic Analysis
1. 