import pytest
from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import User, Contact


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def half_user_factory():
    def factory(*args, **kwargs):
        user = baker.make(User, *args, **kwargs)
        Token.objects.create(user=user)
        return user

    return factory


@pytest.fixture
def user_factory():
    def factory(shop=False, *args, **kwargs):
        user = baker.make(User, *args, **kwargs)
        contact = baker.make(Contact, user=user, *args, **kwargs)
        user.is_active = True
        if shop:
            user.type = "shop"
        user.save()
        token = Token.objects.create(user=user)
        header_auth = {'Authorization': f'Token {token.key}'}
        return user, header_auth, contact

    return factory


@pytest.mark.django_db
def test_create_user(client):
    """Test to create user"""
    url = reverse('user_register')
    response = client.post(url, data={'first_name': 'Evgen',
                                      'last_name': 'Master',
                                      'email': 'test@tetest.ru',
                                      'password1': 'Evgen343!',
                                      'password2': 'Evgen343!',
                                      'company': 'Netology',
                                      'position': 'student'})

    user = User.objects.get(email='test@tetest.ru')
    data = response.json()
    assert response.status_code == 200
    assert data['Status']
    assert user


@pytest.mark.django_db
def test_confirm_account(client, half_user_factory):
    """Test to confirm account"""
    user = half_user_factory()
    token = Token.objects.get(user=user)

    url = reverse('user_confirm')
    response = client.post(url, data={'email': user.email,
                                      'token': token.key})

    user = User.objects.get(id=user.id)
    data = response.json()
    assert response.status_code == 200
    assert data['Status']
    assert user.is_active


@pytest.mark.django_db
def test_user_login(client, half_user_factory):
    """Test to user login"""
    user = half_user_factory()
    user_pass = user.password
    user.set_password(user.password)
    user.is_active = True
    user.save()
    token = Token.objects.get(user=user)

    url = reverse('user_login')
    response = client.post(url, data={'email': user.email,
                                      'password': user_pass})

    data = response.json()
    assert response.status_code == 200
    assert data['Status']
    assert data['Token'] == token.key


@pytest.mark.django_db
def test_user_change_pass(client, half_user_factory):
    """Test to user change password"""
    user = half_user_factory()
    user.is_active = True
    user.save()

    url = reverse('password-reset')
    response = client.post(url, data={'email': user.email})
    data = response.json()
    assert data['status'] == "OK"

    token = ResetPasswordToken.objects.get(user=user)
    url = reverse('password-reset-confirm')
    response = client.post(url, data={'token': token.key,
                                      'password': 'HardPass123#@!'})
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == "OK"


@pytest.mark.django_db
def test_contact_add(client, user_factory):
    """Add user contact test"""
    user, header_auth, _ = user_factory()

    url = reverse('user_contact')
    response = client.post(url, data={'address': 'addr133', 'phone': '321-13'},
                           headers=header_auth)

    contact = Contact.objects.get(address='addr133', phone='321-13',
                                  user=user)
    data = response.json()
    assert data['Status']
    assert contact


@pytest.mark.django_db
def test_contact_edit(client, user_factory):
    """Edit user contact test"""
    user, header_auth, contact = user_factory()

    url = reverse('user_contact')
    response = client.put(url, data={'id': contact.id, 'phone': '11-132'},
                          headers=header_auth)

    contact_query = Contact.objects.get(id=contact.id, phone='11-132',
                                        user=user)
    data = response.json()
    assert data['Status']
    assert contact_query


@pytest.mark.django_db
def test_contact_get(client, user_factory):
    """Get user contact test"""
    user, header_auth, contact = user_factory()

    url = reverse('user_contact')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert contact.address == data[0]['address']


@pytest.mark.django_db
def test_contact_del(client, user_factory):
    """Delete user contact test"""
    user, header_auth, contact = user_factory()

    url = reverse('user_contact')
    response = client.delete(url, data={'items': f'{contact.id}'},
                             headers=header_auth)

    data = response.json()
    assert data['Удалено объектов'] == 1


@pytest.mark.django_db
def test_account_detail_get(client, user_factory):
    """Delete user contact test"""
    user, header_auth, contact = user_factory()

    url = reverse('user_details')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data['email'] == user.email
    assert data['contacts'][0]['address'] == contact.address


@pytest.mark.django_db
def test_account_detail_edit(client, user_factory):
    """Edit user contact test"""
    user, header_auth, _ = user_factory()

    url = reverse('user_details')
    response = client.post(url, data={'first_name': '5geg4',
                                      'email': 'iounh@iuehnrt.ru'},
                           headers=header_auth)

    user_query = User.objects.get(first_name='5geg4',
                                  email='iounh@iuehnrt.ru',
                                  id=user.id)
    data = response.json()
    assert data['Status']
    assert user_query
