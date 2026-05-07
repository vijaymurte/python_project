#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py seed_cities
python manage.py migrate