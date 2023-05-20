from django.urls import path, include
from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm
from rest_framework import routers

from users.views import UserRegistrationView, EmailConfirmationView,\
    UserLoginView, UserDetailView, ContactViewSet


router = routers.DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='usercontact')


urlpatterns = [
    path('', include(router.urls)),
    path('register', UserRegistrationView.as_view(), name='user_register'),
    path('confirm', EmailConfirmationView.as_view(), name='user_confirm'),
    path('login', UserLoginView.as_view(), name='user_login'),
    path('details', UserDetailView.as_view(), name='user_details'),
    path('password_reset', reset_password_request_token,
         name='password-reset'),
    path('password_reset/confirm', reset_password_confirm,
         name='password-reset-confirm'),
]
