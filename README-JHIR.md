# Data Acquisition & Preprocessing
1. I use [streaming API of Twitter](https://developer.twitter.com/en/docs/tweets/filter-realtime/overview) to collect tweets containing keywords "covid19" or "#covid19". And, I monitor this stream from first week of March.
2. To avoid from considering the duplicated contents, e.g., retweets, quote tweet, I use `parse-tweets.py` to filter out those tweets. `retrieve-details-of-tweets.py` is then used to retrieve details of each tweet by [statuses/lookup api](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup) because I find texts of tweets returned by streaming API are truncated...
    - Note that `retrieve-details-of-tweets.py` also help do text preprocessing 
    - I use mongodb to store every tweet with its meta information and NLP results.
3. I will share the id list of these tweets ASAP. If you are interested in analyzing these tweets, you can use [statuses/lookup api](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup) to pull the contents back and preprocess by the similar strategy implemented in `retrieve-details-of-tweets.py`.

# Procedure for Topic Analysis
Train the topic model using onlineNMF 
- Learn topic patterns using nmf scheme because of three reasons:
    - The large corpus (~ tens of milions of tweets) slows down the sampling process of Latent Dirichlet Allocation (LDA).
    - Recent empirical study (Chen et al., 2019) shows the short text characteristic of tweet breaks the assumption of LDA, which assumes each document consist of multiple topics.
    - Gensim, a well-implemented python toolkit, has implemented [onlineNMF with several helper functions](https://radimrehurek.com/gensim/models/nmf.html) to explore the resultant topic model.

## Data Preparation
The **build-usweek-mapping-tweets.py** is used for exporting tweets sorted in the us-week order, which starts a week from Sunday.

## Model 1, Rolling-based NMF
Run as ```bash rolling-model-run.sh Stage```

    Stage: scan-vocab, prepare-corpus, train-model, inference-dtm, export-summary, calculate-jac-diff

Only need to revise the general information in script.
The required data and logics should be self-explaned in bash script.

## Model 2, Sliding-based NMF
Run as ```bash sliding-window-model-run.sh Stage```

	Stage: prepare-corpus, train-model, inference-dtm, export-summary, calculate-jac-diff

## Subsequent Analysis
Use `export-representative-tweets.py` for exporting representative topical tweets of each week

# Reference
- Chen, Y., Zhang, H., Liu, R., Ye, Z., & Lin, J. (2019). Experimental explorations on short text topic mining between LDA and NMF based Schemes. Knowledge-Based Systems, 163, 1-13.