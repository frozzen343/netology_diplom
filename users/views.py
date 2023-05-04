from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from diplom.celery import send_email
from users.models import Contact
from users.serializers import UserSerializer, ContactSerializer


class RegisterAccount(APIView):
    """
    Для регистрации покупателей, продавцов
    """
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.save()
            send_email('Подтверждение почты',
                       user.auth_token.key,
                       [user.email])
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


class ContactView(APIView):
    """
    Класс для работы с контактами покупателей
    """
    permission_classes = [IsAuthenticated]

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        contact = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data.update({'user': request.user.id})
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'Status': True})
        else:
            return Response({'Status': False,
                             'Errors': serializer.errors})

    # удалить контакты
    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query |= Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return Response({'Status': True,
                                 'Удалено объектов': deleted_count})
        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        if {'id'}.issubset(request.data):
            contact = Contact.objects.filter(id=request.data['id'],
                                             user=request.user).first()
            if contact:
                serializer = ContactSerializer(contact,
                                               data=request.data,
                                               partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'Status': True})
                else:
                    return Response({'Status': False,
                                     'Errors': serializer.errors})
            return Response({'Status': False,
                             'Errors': 'Не найдено'})
        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})
