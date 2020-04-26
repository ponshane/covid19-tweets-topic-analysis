python prepare-nmf-corpus.py -c FirstWeek_March -f W1-March-Tweets
python prepare-nmf-corpus.py -c FirstWeek_March SecondWeek_March -f W1W2-March-Tweets-Moving
python prepare-nmf-corpus.py -c SecondWeek_March -f W2-March-Tweets
python prepare-nmf-corpus.py -c SecondWeek_March ThirdWeek_March -f W2W3-March-Tweets-Moving
python prepare-nmf-corpus.py -c ThirdWeek_March -f W3-March-Tweets
python prepare-nmf-corpus.py -c ThirdWeek_March FourthWeek_March -f W3W4-March-Tweets-Moving
python prepare-nmf-corpus.py -c FourthWeek_March -f W4-March-Tweets