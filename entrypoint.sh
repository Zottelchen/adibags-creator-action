#!/bin/sh -l

echo "INSTALLING DEPENDENCIES"
poetry install

printf "\n\n"
echo "$(date) MAKING ADIBAGS_$ADDON_VARIANT"
mkdir out
echo "$(date) CREATING FILES"
poetry run python /app/create.py
echo "$(date) CLEANING UP"
cp -r .git ./out
ls -la
