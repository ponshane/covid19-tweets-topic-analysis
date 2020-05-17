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
collections=(FirstWeek_March FirstWeek_March,SecondWeek_March SecondWeek_March SecondWeek_March,ThirdWeek_March ThirdWeek_March ThirdWeek_March,FourthWeek_March FourthWeek_March FourthWeek_March,FirstWeek_April FirstWeek_April FirstWeek_April,SecondWeek_April SecondWeek_April SecondWeek_April,ThirdWeek_April ThirdWeek_April ThirdWeek_April,FourthWeek_April FourthWeek_April)
abbrs=(W1-March W1W2-March W2-March W2W3-March W3-March W3W4-March W4-March W4MarW1Apr W1-April W1W2-April W2-April W2W3-April W3-April W3W4-April W4-April)

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