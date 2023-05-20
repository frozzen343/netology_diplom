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


@pytest.mark.django_db
def test_user_registration_view(client):
    """
    Register user test
    """
    data = {'first_name': 'Evgen',
            'last_name': 'Master',
            'email': 'test@tetest.ru',
            'password': 'Evgen343!',
            'password_confirmation': 'Evgen343!',
            'company': 'Netology',
            'position': 'student'}

    response = client.post(reverse('user_register'), data=data)

    data_response = response.json()
    assert response.status_code == 201
    assert User.objects.filter(email=data['email']).exists()
    assert data_response['first_name'] == data['first_name']


@pytest.mark.django_db
def test_email_confirmation_view(client):
    """
    Confirm user test
    """
    user = baker.make(User)
    token = Token.objects.create(user=user)

    url = reverse('user_confirm')
    response = client.post(url, data={'email': user.email,
                                      'token': token.key})

    user = User.objects.get(id=user.id)
    data = response.json()
    assert response.status_code == 201
    assert data['detail'] == 'Email confirmed successfully.'
    assert user.is_active


@pytest.mark.django_db
def test_user_login_view(client):
    """
    User login test
    """
    user_pass = 'testpassword123!'
    user = baker.make(User, password=user_pass, is_active=True)
    user.set_password(user.password)
    user.save()
    token = Token.objects.create(user=user)

    url = reverse('user_login')
    response = client.post(url, data={'email': user.email,
                                      'password': user_pass})

    data = response.json()
    assert response.status_code == 200
    assert data['detail'] == 'Успешная авторизация.'
    assert data['token'] == token.key


class TestUserDetailView:
    def setup(self):
        self.user = baker.make(User, is_active=True)
        token = Token.objects.create(user=self.user)
        self.header_auth = {'Authorization': f'Token {token.key}'}
        self.contact = baker.make(Contact, user=self.user)

    @pytest.mark.django_db
    def test_detail_view_get(self, client):
        """
        Get user detail test
        """
        url = reverse('user_details')
        response = client.get(url, headers=self.header_auth)

        data = response.json()
        assert response.status_code == 200
        assert data['email'] == self.user.email
        assert data['contacts'][0]['address'] == self.contact.address

    @pytest.mark.django_db
    def test_detail_view_patch(self, client):
        """
        Edit user detail test
        """
        data = {'first_name': '5geg4', 'email': 'iounh@iuehnrt.ru'}

        url = reverse('user_details')
        response = client.patch(url, data=data,
                                headers=self.header_auth)

        user_query = User.objects.filter(**data)
        data_response = response.json()
        assert response.status_code == 200
        assert data_response['first_name'] == data['first_name']
        assert data_response['email'] == data['email']
        assert user_query.exists()


class TestContactViewSet:
    def setup(self):
        self.user = baker.make(User, is_active=True)
        token = Token.objects.create(user=self.user)
        self.header_auth = {'Authorization': f'Token {token.key}'}
        self.contact = baker.make(Contact, user=self.user)

    @pytest.mark.django_db
    def test_contact_add(self, client):
        """Add user contact test"""
        data = {'address': 'addr133',
                'phone': '321-13'}

        url = reverse('usercontact-list')
        response = client.post(url, data=data,
                               headers=self.header_auth)

        contact = Contact.objects.filter(**data, user=self.user)
        data_response = response.json()
        assert response.status_code == 201
        assert data_response['address'] == data['address']
        assert contact.exists()

    @pytest.mark.django_db
    def test_contact_edit(self, client):
        """Edit user contact test"""
        data = {'phone': '11-132-123',
                'address': '87oho87g87g8uy7g 45yt4er'}

        url = reverse('usercontact-detail', args=[self.contact.id])
        response = client.put(url, data=data, headers=self.header_auth)

        contact_query = Contact.objects.filter(id=self.contact.id, **data)
        data_response = response.json()
        assert response.status_code == 200
        assert data['phone'] == data_response['phone']
        assert data['address'] == data_response['address']
        assert contact_query.exists()

    @pytest.mark.django_db
    def test_contact_get(self, client):
        """Get user contact test"""
        url = reverse('usercontact-list')
        response = client.get(url, headers=self.header_auth)

        data = response.json()
        assert response.status_code == 200
        assert self.contact.address == data['results'][0]['address']

    @pytest.mark.django_db
    def test_contact_del(self, client):
        """Delete user contact test"""
        url = reverse('usercontact-detail', args=[self.contact.id])
        response = client.delete(url, headers=self.header_auth)

        assert response.status_code == 204


@pytest.mark.django_db
def test_user_change_pass(client):
    """Test to user change password"""
    user = baker.make(User, is_active=True)

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
