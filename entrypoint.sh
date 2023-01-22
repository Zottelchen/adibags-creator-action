#!/bin/sh -l

printf "\n\n"
echo "$(date) MAKING ADIBAGS_ADDON"
mkdir out
echo "$(date) CREATING FILES"
python create.py
echo "$(date) CLEANING UP"
cp -r .git ./out
chmod -R 777 ./out
ls -la ./out
