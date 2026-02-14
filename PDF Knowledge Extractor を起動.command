#!/bin/bash

# Change to the app directory
cd "$(dirname "$0")"

# Launch the app with venv Python
./venv/bin/python3 src/app.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "エラーが発生しました。Enterキーを押して終了してください。"
    read
fi
