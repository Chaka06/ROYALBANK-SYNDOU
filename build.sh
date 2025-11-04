#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create static directory structure if it doesn't exist
mkdir -p static/css static/img static/js

# Collect static files (force overwrite, verbosity to see what's happening)
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear -v 2 || echo "Warning: collectstatic had issues"
echo "Static files collected. Checking STATIC_ROOT..."
ls -la staticfiles/ 2>&1 | head -10 || echo "staticfiles directory not found"

# Run migrations
python manage.py migrate --no-input
