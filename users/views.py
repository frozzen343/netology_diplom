from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserSerializer


class RegisterAccount(APIView):
    """
    Для регистрации покупателей, продавцов
    """
    def post(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.POST.update({})
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.save()
            send_mail('Подтверждение почты',
                      user.auth_token.key,
                      None, [user.email])
            return Response({'Status': True})
        else:
            return Response({'Status': False,
                             'Errors': user_serializer.errors})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = Token.objects.filter(user__email=request.data['email'],
                                         key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                return Response({'Status': True})
            else:
                return Response({'Status': False,
                                 'Errors': 'Неправильный токен или email'})

        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'],
                                password=request.data['password'])
            if user:
                if user.is_active:
                    token = Token.objects.get(user=user)
                    return Response({'Status': True, 'Token': token.key})
            return Response({'Status': False,
                             'Errors': 'Не удалось авторизовать'})

        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    """
    Класс для работы данными пользователя
    """
    permission_classes = [IsAuthenticated]

    # получить данные
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # Редактирование методом POST
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(request.user,
                                         data=request.data,
                                         partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Status': True})
        else:
            return Response({'Status': False,
                             'Errors': user_serializer.errors})
