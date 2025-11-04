#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create static directory structure if it doesn't exist
mkdir -p static/css static/img static/js

# Collect static files (force overwrite, verbosity to see what's happening)
python manage.py collectstatic --no-input --clear -v 2

# Run migrations
python manage.py migrate --no-input
