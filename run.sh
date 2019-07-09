#!/bin/bash

echo " "
echo "Starting Check Change Module..."
echo " "
# variables & functions
if [ "`echo -n`" = "-n" ]; then
  n=""
  c="\c"
else
  n="-n"
  c=""
fi

spinner()
{
    local pid=$!
    local delay=0.75
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}


# BUILD THE ORDER BOT IMAGE
echo "Loading the Docker image..."
docker load < ordering_bot.tar &
spinner

echo "Module loaded!"
# ECHO EXAMPLE
echo " "
echo "Instructions:"
echo "===================================================="
echo " The inputs of this module are:
        * a check (composed by 1 or more 'number + item') 
        * a new order (is a sentence saying that you want to change an existing item on the check for another item)"
echo " "
echo "  - The check items should be separated by commas:"
echo "    i.e: 2 large pepperoni pizzas, 2 sugar free sodas"
echo " "
echo "  - The new order should be a simple string:"
echo "    i.e: Make one of the sodas a regular"
echo "===================================================="
echo " "
echo " "



# RECEIVE INPUTS

while :
do

echo $n Enter the check: $c
read check
echo $n Enter the change: $c
read change
echo " "
echo "Arguments resume:"
echo "Check provided:"
echo "$check"
echo " "
echo "Change provided:"
echo "$change"
echo " "
read -p "Are the arguments correct [Y/n]? " yn
    case $yn in
        [Yy]* ) echo " ";
                docker run ordering_bot "$check" "$change" &
                spinner;;
        [Nn]* ) echo "Canceled...";;
        * ) docker run ordering_bot "$check" "$change" &
                spinner;;
    esac
echo "--------"
echo "Press [CTRL+C] to stop..."
echo " "
done

