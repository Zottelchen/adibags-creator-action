#!/bin/sh -l

printf "\n\n"
echo "$(date) MAKING ADIBAGS_$ADDON_VARIANT"
mkdir out
echo "$(date) CREATING FILES"
poetry run /app/create.py
echo "$(date) CLEANING UP"
cp -r .git ./out
ls -la
