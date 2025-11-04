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

# Create or update sandra763 user with all account data
# get_or_create ensures data persists - only creates if doesn't exist, updates password if exists
echo "Creating/updating sandra763 user..."
python manage.py create_sandra_complete || echo "Warning: create_sandra_complete had issues"

# Create or update admin superuser
# Uses get_or_create internally - data persists in PostgreSQL, only updates password if user exists
echo "Creating/updating admin superuser..."
python manage.py create_superuser_cmd admin admin123 --email admin@rbc-bank.com || echo "Warning: create_superuser_cmd had issues"
