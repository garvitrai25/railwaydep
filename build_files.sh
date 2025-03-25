#!/bin/bash

echo "Build started"
set -o errexit  # Exit on error

# Make script executable
chmod +x build_files.sh

# Print Python version
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Run collectstatic
python manage.py collectstatic --noinput --clear

echo "Build completed" 