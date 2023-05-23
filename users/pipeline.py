from rest_framework.authtoken.models import Token
from rest_framework import status
from django.http import JsonResponse

from users.models import User


def login_vk_pipeline(strategy, backend, user, response, *args, **kwargs):
    user, created = User.objects.get_or_create(
        first_name=response['first_name'],
        last_name=response['last_name'],
        email=response['email'],
        is_active=True,
    )
    token, created = Token.objects.get_or_create(user_id=user.id)
    return JsonResponse({"detail": "Successful authorization.",
                         "token": token.key},
                        status=status.HTTP_200_OK)
