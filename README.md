# Documentation
The following steps are used for replicating the research paper:
Detecting Topics and Sentiments of Public Concerns on COVID-19 Vaccines with Social Media Trend Analysis
## Step1, Download Tweets

We use the open accessed data, [CORONAVIRUS (COVID-19) TWEETS DATASET](https://ieee-dataport.org/open-access/coronavirus-covid-19-tweets-dataset), that can be downloaded from IEEE DataPort. For using the same tweets as the paper used, please download `corona_tweets_[273-332].zip` from the dataset's website. Those zip files should contain the Covid-19 related tweets from 2020-12-16 ~ 2021-02-13. All zip files are then unzipped and stored in a data folder (e.g., ~/DATA_PATH/[273-332]). 

For following the Twitter's Policy, we can only get tweet ids from the open accessed dataset. One needs to retrieve the metadata using Twitter's [lookup API](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup). `notebook/lookup-metadata.ipynb` is the notebook we used for retrieving the metadata of tweets (also called hydrate). After having the metadata of tweets, we then use `notebook/filter-tweets.ipynb` to perform keyword matching and retain the vaccine-related tweets.

## Step2, Train Model & inference
1. `format-vaccine-tweets.py` helps format the corpus that are stored in ~/DATA_PATH/[273-332]:
    ```python
    # note that all formatted outputs are put in ./corpora/
    # 2020-12-16 ~ 2020-12-30
    python format-vaccine-tweets.py -fs 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 \
    -op ./corpora \
    -on First-and-SecondWeek
    # 2020-12-31 ~ 2021-01-14
    python format-vaccine-tweets.py -fs 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 \
    -op ./corpora \
    -on Third-and-FourthWeek
    # 2021-01-15 ~ 2021-01-29
    python format-vaccine-tweets.py -fs 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 \
    -op ./corpora \
    -on Fifth-and-SixthWeek
    # 2021-01-30 ~ 2021-02-13
    python format-vaccine-tweets.py -fs 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 \
    -op ./corpora \
    -on Seventh-and-EighthWeek
    ```
2. `rolling-model-run.sh` prepares the tweets and train the rolling-nmf model:
    ```bash
    # please run the following commands sequentially
    # 1) scan vocabulary 
    # the outputs would be stored in ./corpora/
    bash rolling-model-run.sh scan-vocab
    
    # 2) transform the corpus into requried format
    # the outputs would be stored in ./corpora/ and ./models/
    bash rolling-model-run.sh prepare-corpus
    
    # 3) train the rolling-nmf model
    # the resultant models are saved in ./models/
    bash rolling-model-run.sh train-model
    ```
3. `inference-onemodel-dtm[1-4].py` is used for inferencing topic distribution of each document. Each py file is responsible for every two weeks data:
    ```bash
    # note that each py would only use 1 thread, so one can run them in parallel for better efficientcy
    # the resultant dtm (document topic matrix) would be stored in ./models/
    python inference-onemodel-dtm1.py
    python inference-onemodel-dtm2.py
    python inference-onemodel-dtm3.py
    python inference-onemodel-dtm4.py
    ```

## Step3, Visualization & Exploration
1. `select-distinct-tweets.py` helps identify distinct tweets in corpora, which are used for sentiment analysis & topic visualization
2. `notebook/create_dated_topic_frame.ipynb` combines the topic distribution of each document with its data information
    - `notebook/drawing-topic-trend.ipynb` draws the topic trend of each topic
    - `notebook/find-dated-representative-tweets.ipynb` helps identify representative tweets for a specific topic on a given day
    - `notebook/print-topics.ipynb` explores the most contributed words of each topic