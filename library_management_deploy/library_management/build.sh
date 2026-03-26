#!/bin/bash
# Build script for Railway deployment
pip install -r requirements.txt
python manage.py collectstatic --no-input --settings=library_management.settings_prod
python manage.py migrate --settings=library_management.settings_prod
