#!/bin/bash

set -uoe pipefail

# python3 movieLib-cons.py 

# tput_menu: a menu driven system information program
tput smcup
tput civis

clear

BG_BLUE="$(tput setab 39)"
FG_BLUE="$(tput setaf 33)"
BG_DIM="$(tput setab 239)"
FG_BLACK="$(tput setaf 0)"
FG_WHITE="$(tput setaf 255)"
RESET="$(tput sgr0)"

WIDTH=$(tput cols)
HEIGHT=$(tput lines)

SELECTED=0

OIFS="$IFS"
IFS=$'\n'

# tmpfile="$(find ./movieData/* | head -n 20 | cut -d"/" -f3)"

# Display menu until selection == 0
while true; do
    stty -echo #DISABLE INPUT
    echo -n "$RESET"
    tput home
    cat <<- _EOF_

       MOVIES
    ---======---
_EOF_
    tput cup "4" "0"
    
    counter=0
    for file in $(find ./movieData/* | head -n 20 | cut -d"/" -f3); do 
        file=$(echo "$file" | cut -d";" -f1)
        if [ $counter -eq $SELECTED ]; then
            # echo -n "$FG_BLACK$BG_BLUE"
            text="${FG_BLACK}${BG_BLUE}$file${RESET}"

        else
            # echo -n $FG_BLUE
            text="${FG_BLUE}$file${RESET}"
        fi

        printf '%3s: %1s' "$counter" "$text"
        tput cud1
        counter=$(( counter + 1))
    done
    stty echo #ENABLE INPUT

    echo -n "$RESET"
    tput cup "$((HEIGHT + 10))" "0"
    # echo -n $FG_WHITE
    read -rsn1 input

    case $input in
    'q')  
        echo -n "Press any for exit"
        break
        ;;
    'j')  
        SELECTED=$(( SELECTED + 1 ))
        ;;
    'k')
        SELECTED=$(( SELECTED - 1 ))
        ;;
    *)  echo -n "Invalid entry."
        read -rsn1
        tput cup "$HEIGHT" "0"
        echo -n "              "
        ;;
    esac
done

# ueberzug layer --parser bash 0< <(
#     declare -Ap add_command=([action]="add" [identifier]="example0" [x]="0"
#     [y]="0" [path]="")
# )

# ueberzug layer --parser bash 0< <(
#     declare -Ap remove_command=([action]="remove" [identifier]="example0")
#     sleep 5
# )


read -rsn1 
IFS="$OIFS"
tput cnorm
tput rmcup
