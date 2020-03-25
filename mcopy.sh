#!/bin/bash

for item in "$1"*; do

    if [[ "$item" == *"mkv"* ]] || [[ "$item" == *"mp4"* ]] || [[ "$item" == *"avi"* ]];
    then
        echo $item
        echo "found"
        JMENO=$(echo "$item" | awk -F'/' '{ print $6 }')
        touch "$JMENO"

    else
        echo "not"
    fi
done
echo "done"
