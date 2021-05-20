import os
import re
import json
import string
import argparse
from codebase.utils import Timer
from nltk.corpus import stopwords
from json.decoder import JSONDecodeError

def extract_json_from_file(file_path):
    with open(file_path, "r") as rf:
        return json.loads(rf.read())

def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s):
    
    ############## clean first ##############
    # remove emoji
    s = emoji_pattern.sub(r'', s)
    s = re.sub(emoticons_str, r'', s)
    s = re.sub(r'(?:(?:\d+,?)+(?:\.?\d+)?)', r'', s) # numbers
    s = re.sub(r'<[^>]+>', r'', s) # HTML tags
    s = re.sub(r'(?:@[\w_]+)', r'', s) # @-mentions
    s = re.sub(r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',\
              r'', s) # URLs
    #########################################
    
    # split tokens
    tokens = tokenize(s)
    # lowerize the tokens
    tokens = [w.lower() for w in tokens]
    
    filtered_tokens = []
    for w in tokens:
        #check tokens against stop words and punctuations
        if w not in STOP_WORDS and w not in string.punctuation:
            filtered_tokens.append(w)
    
    return filtered_tokens

if __name__ == "__main__":

    # define Args of this programe
    parser = argparse.ArgumentParser()
    parser.add_argument('-fs', '--folders', type=str, nargs="+", required=True, dest="folders",
                        help='give a list of folder names, e.g., -fs folder1 folder2')
    parser.add_argument('-op', '--outpath', type=str, required=True, dest="outpath",
                        help='give the path of the output file, e.g., -op dirpath')                  
    parser.add_argument('-on', '--outname', type=str, required=True, dest="outname",
                        help='give the name of the output file, e.g., -on outFile')
    args = parser.parse_args()

    # define Global variables
    # define Emoji patterns
    emoticons_str = r"(?:[:=;][oO\-]?[D\)\(\[\]\\OpP])"
    emoji_pattern = re.compile("["
             u"\U0001F600-\U0001F64F"  # emoticons
             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
             u"\U0001F680-\U0001F6FF"  # transport & map symbols
             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
             u"\U00002702-\U000027B0"
             u"\U000024C2-\U0001F251"
             "]+", flags=re.UNICODE)
    # define reguilar expressions
    regex_str = [
        r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
        r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
        r'(?:[\w_]+)', # other words
        r'(?:\S)' # anything else
    ]
    tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
    # define stop words
    STOP_WORDS = set(stopwords.words('english'))

    base_dir = "/home/ponshane/Data/Corona_Vaccine_Tweets"
    # join a output path & filename for storing the processed corpus
    outFile = os.path.join(args.outpath, args.outname+'-raw-corpus.tsv')
    wf = open(outFile, "w")
    wf.write("id_str\tcreated_at\ttokens\n")
    # define a variable recording number of effective tweets we can use later
    effective_NTweets = 0

    for folder in args.folders:
        print(f"Start processing files in {folder}")
        with Timer():
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
                        # filter out retweets 
                        if j['retweet'] == True:
                            continue
                        id_str = j['id_str']
                        created_at = j['created_at']
                        # noise removal & simple tokenization
                        tokens_str = ",".join(preprocess(j['full_text']))
                        
                        wf.write(f"{id_str}\t{created_at}\t{tokens_str}\n")
                        effective_NTweets += 1
    # finish importing json objects from all files of a folder
    wf.close()
    foldernames = ",".join(args.folders)
    print(f"Extracted {effective_NTweets} original tweets from {foldernames}")