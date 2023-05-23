# Service for ordering goods for retail chains

## Api documentation
- [postman](https://documenter.getpostman.com/view/26733994/2s93eSZaVB)
- swagger-ui:  http://localhost/api/schema/swagger-ui/
- redoc:  http://localhost/api/schema/redoc/

### Login via VK.com
- create an application in vk.com
- set up redirect url: http://localhost/auth/complete/vk-oauth2/
- copy the id app, secret key to .env file


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