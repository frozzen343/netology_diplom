from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance,
                                 reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    """
    msg = EmailMultiAlternatives(
        f"Token сброса пароля для {reset_password_token.user}",
        reset_password_token.key,
        None, [reset_password_token.user.email]
    )
    msg.send()
