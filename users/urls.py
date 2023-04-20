from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm

from users.views import RegisterAccount, ConfirmAccount, LoginAccount, \
    AccountDetails

urlpatterns = [
    path('register', RegisterAccount.as_view(), name='user_register'),
    path('confirm', ConfirmAccount.as_view(), name='user_confirm'),
    path('login', LoginAccount.as_view(), name='user_login'),
    path('details', AccountDetails.as_view(), name='user_details'),
    path('password_reset', reset_password_request_token,
         name='password-reset'),
    path('password_reset/confirm', reset_password_confirm,
         name='password-reset-confirm'),
]
