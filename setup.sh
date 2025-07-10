#!/bin/bash

if [ -d ".virtualenv" ]; then
    rm -rf .virtualenv
fi

python3 -m venv .virtualenv

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .virtualenv/Scripts/activate
else
    source .virtualenv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt