#!/bin/bash

# $# is number of input arguments
if [[ $# -ne 1 ]]; then
    # $0 is the name of this bash file
    echo "Usage: $0 Stage"
    echo "Stage could be scan-vocab, prepare-corpus, train-model, inference-dtm, export-summary, calculate-jac-diff"
    exit
fi

Stage=$1
echo "Stage -> " $Stage

# general setting
preDictTag="Mar2Jun-Tweets"
NumTopic=25
collections_str="Week10 Week11 Week12 Week13 Week14 Week15 Week16 Week17 Week18 Week19 Week20 Week21 Week22 Week23 Week24 Week25 Week26"
# split string into array
IFS=' ' read -ra collections <<< "$collections_str"

if [ "$Stage" == "scan-vocab" ]; then
    cstr="${collections[@]}"
    python scan-whole-vocabs.py -c $cstr -f $preDictTag
    echo "please run next stage: prepare-corpus"
elif [ "$Stage" == "prepare-corpus" ]; then
    for col in "${collections[@]}"
    do
        # ${string/substring/replacement}
        modcol=${col/_/-}
        python prepare-nmf-corpus.py -c "$col" -f "$modcol"-Tweets-Rolling -pd "$preDictTag"
    done
    echo "please run next stage: train-model"
elif [ "$Stage" == "train-model" ]; then
    preCol=""
    for col in "${collections[@]}"
    do
        # ${string/substring/replacement}
        modcol=${col/_/-}
        # -z to check whether "$preCol" is null
        if [ -z "$preCol" ]; then
            python train-nmf-model.py -n "$NumTopic" -f "$modcol"-Tweets-Rolling -pd "$preDictTag"
            preCol=$modcol
        else
            python train-nmf-model.py -n "$NumTopic" -f "$modcol"-Tweets-Rolling -pf "$preCol"-Tweets-Rolling
            preCol=$modcol
        fi
    done
    echo "please run next stage: inference-dtm"
elif [ "$Stage" == "inference-dtm" ]; then
    for col in "${collections[@]}"
    do
        # ${string/substring/replacement}
        modcol=${col/_/-}
        python inference-nmf-dtm.py -n "$NumTopic" -f "$modcol"-Tweets-Rolling
    done
    echo "please run next stage: export-summary"
elif [ "$Stage" == "export-summary" ]; then
    for col in "${collections[@]}"
    do
        # ${string/substring/replacement}
        modcol=${col/_/-}
        # for saving time, use -idtm 0 to skip calculating topic ratio
        python export-nmf-model-summary.py -n "$NumTopic" -f "$modcol"-Tweets-Rolling -idtm 0
    done
elif [ "$Stage" == "calculate-jac-diff" ]; then
    cstr="${collections[@]}"
    modcollections=${cstr//_/-}
    symb="'"
    suffix="-Tweets-Rolling-"$NumTopic"topics-summary.csv"
    echo "python calculate-jaccard-index-between-models.py -tl "$modcollections" -s="$symb$suffix$symb" > tmp.txt"
    echo "Please copy above line and run it by yourself."
fi