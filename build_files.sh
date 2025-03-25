#!/bin/bash

# Make script executable
chmod +x build_files.sh

# Install Python dependencies
pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --noinput

# Make the script executable after creation
chmod +x build_files.sh 