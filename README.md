# Service for ordering goods for retail chains

## Api documentation
[postman](https://documenter.getpostman.com/view/26733994/2s93eSZaVB)


## Installation Guide

### Env variables:
change .env file

### Docker / docker-compose:
```sh
docker-compose up
```

### Or manual installation
install virtual environment
```sh
python -m venv venv
source venv/bin/activate
```
install dependencies and start app
```sh
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn diplom.wsgi --bind 0.0.0.0:8000
```
start celery
```sh
celery -A diplom.celery worker
```

## Development
after making changes
```sh
pytest --cov=.
flake8 .
pytest
```