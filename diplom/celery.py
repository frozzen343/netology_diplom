from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom.settings')

app = Celery('diplom')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task
def __send_email(*args):
    if settings.EMAIL_HOST:
        send_mail(args[0], args[1], None, args[2])
    else:
        print('mail not configured!')


def send_email(title, body, to: list):
    __send_email.delay(title, body, to)
