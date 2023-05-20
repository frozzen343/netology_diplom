from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import viewsets, status, serializers
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from diplom.celery import send_email
from users.models import Contact, User
from users.serializers import UserSerializer, ContactSerializer, \
    ContactCreateUpdateSerializer, EmailConfirmationSerializer, \
    UserLoginSerializer


class UserRegistrationView(CreateAPIView):
    """
    Для регистрации покупателей, продавцов
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_email('Подтверждение почты',
                   user.auth_token.key,
                   [user.email])


@extend_schema(
    responses={
       201: inline_serializer(
           name='Response_confirm',
           fields={'detail': serializers.CharField()}),
    }
)
class EmailConfirmationView(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    serializer_class = EmailConfirmationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Email confirmed successfully."},
                        status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
       200: inline_serializer(
           name='Response_login',
           fields={'detail': serializers.CharField(),
                   'token': serializers.CharField()}),
    }
)
class UserLoginView(APIView):
    """
    Класс для авторизации пользователей
    """
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get(user=user)
        return Response({"detail": "Успешная авторизация.",
                         "token": token.key},
                        status=status.HTTP_200_OK)


class UserDetailView(RetrieveUpdateAPIView):
    """
    Класс для работы данными пользователя
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ContactViewSet(viewsets.ModelViewSet):
    """
    Класс для работы с контактами покупателей
    """
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return ContactCreateUpdateSerializer
        return ContactSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
