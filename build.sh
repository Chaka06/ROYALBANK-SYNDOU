#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create static directory if it doesn't exist (for collectstatic)
mkdir -p static/css static/img static/js

# Collect static files (force overwrite)
python manage.py collectstatic --no-input --clear

# Run migrations
python manage.py migrate --no-input
