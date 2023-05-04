#!/bin/sh

python manage.py collectstatic
python manage.py migrate
gunicorn diplom.wsgi --bind 0.0.0.0:8000