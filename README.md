> This is an ongoing project. Codes may be changed significantly from time to time.

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
1. Prepare the tweets corpus for later topic modeling
    ```bash
    python prepare-nmf-corpus.py -c FirstWeek_March SecondWeek_March ThirdWeek_March FourthWeek_March -f Whole-March-Tweets
    ```
2. Train the topic model using onlineNMF (Zhao & Tan, 2016)
    - I use online matrix factorization approach - onlineNMF to learn topic patterns because of three reasons:
        - The large corpus (~11.3M) slows down the sampling process of Latent Dirichlet Allocation (LDA).
        - Recent empirical study (Chen et al., 2019) shows the short text characteristic of tweet breaks the assumption of LDA, which assumes each document consist of multiple topics.
        - Gensim, a well-implemented python toolkit, has implemented [onlineNMF with several helper functions](https://radimrehurek.com/gensim/models/nmf.html) to explore the resultant topic model.
    ```bash
    python train-nmf-model.py -n 25 -f Whole-March-Tweets
    ```
3. Infer the document-topic matrix for further visualization and analysis
    ```bash
    python inference-nmf-dtm.py -n 25 -f Whole-March-Tweets
    ```

# Reference
- Zhao, R., & Tan, V. Y. (2016). Online nonnegative matrix factorization with outliers. IEEE Transactions on Signal Processing, 65(3), 555-570.
- Chen, Y., Zhang, H., Liu, R., Ye, Z., & Lin, J. (2019). Experimental explorations on short text topic mining between LDA and NMF based Schemes. Knowledge-Based Systems, 163, 1-13.