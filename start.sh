#!/usr/bin/env sh

# Navigate to project directory
cd /path/to/your/python/project

# Check for Pipfile.lock
if [ ! -f Pipfile.lock ]; then
    echo "Initializing pipenv..."
    pipenv --bare install
else
    echo "Pipfile.lock found. Ensuring dependencies are installed..."
    pipenv sync
fi

# Run the Python app
pipenv run python main.py
