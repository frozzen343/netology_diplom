from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from diplom.celery import send_email


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance,
                                 reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    """
    send_email(f"Token сброса пароля для {reset_password_token.user}",
               reset_password_token.key,
               [reset_password_token.user.email])
