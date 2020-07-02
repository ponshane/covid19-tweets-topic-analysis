#!/bin/bash

# $# is number of input arguments
if [[ $# -ne 1 ]]; then
    # $0 is the name of this bash file
    echo "Usage: $0 Stage"
    echo "Stage could be prepare-corpus, train-model, inference-dtm, export-summary, calculate-jac-diff"
    exit
fi

Stage=$1
echo "Stage -> " $Stage

# general setting
NumTopic=25
collections=(Week10,Week11 Week11,Week12 Week12,Week13 Week13,Week14 Week14,Week15 Week15,Week16 Week16,Week17 Week17,Week18 Week18,Week19 Week19,Week20 Week20,Week21 Week21,Week22 Week22,Week23 Week23,Week24 Week24,Week25 Week25,Week26)
abbrs=(W10W11 W11W12 W12W13 W13W14 W14W15 W15W16 W16W17 W17W18 W18W19 W19W20 W20W21 W21W22 W22W23 W23W24 W24W25 W25W26)

if [ "$Stage" == "prepare-corpus" ]; then
# ${#collections[*]} is the size of collections
# since size(collections) == size(abbrs)
# use the same index to loop them
    for (( i=0; i<${#collections[*]}; ++i)); do
        IFS=',' read -ra cases <<< ${collections[$i]}
        if [ ${#cases[*]} -eq 2 ]; then
            python prepare-nmf-corpus.py -c "${cases[@]}" -f "${abbrs[$i]}"-Tweets-Sliding
        else
            python prepare-nmf-corpus.py -c "${collections[$i]}" -f "${abbrs[$i]}"-Tweets-Sliding
        fi
    done
elif [ "$Stage" == "train-model" ]; then
    for col in "${abbrs[@]}"
    do
        python train-nmf-model.py -n "$NumTopic" -f "$col"-Tweets-Sliding
    done
elif [ "$Stage" == "inference-dtm" ]; then
    for col in "${abbrs[@]}"
    do
        python inference-nmf-dtm.py -n "$NumTopic" -f "$col"-Tweets-Sliding
    done
elif [ "$Stage" == "export-summary" ]; then
    for col in "${abbrs[@]}"
    do
        # for saving time, use -idtm 0 to skip calculating topic ratio
        python export-nmf-model-summary.py -n "$NumTopic" -f "$col"-Tweets-Sliding -idtm 0
    done
elif [ "$Stage" == "calculate-jac-diff" ]; then
    cstr="${abbrs[@]}"
    symb="'"
    suffix="-Tweets-Sliding-"$NumTopic"topics-summary.csv"
    echo "python calculate-jaccard-index-between-models.py -tl "$cstr" -s="$symb$suffix$symb" > tmp.txt"
    echo "Please copy above line and run it by yourself."
fi