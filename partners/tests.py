import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from partners.models import Shop
from products.models import ProductInfo, Product, Category
from users.models import User, Contact


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        user = baker.make(User, is_active=True, type='shop', *args, **kwargs)
        token = Token.objects.create(user=user)
        header_auth = {'Authorization': f'Token {token.key}'}
        return user, header_auth

    return factory


@pytest.fixture
def shop_factory():
    def factory(user_id, *args, **kwargs):
        return baker.make(Shop, user_id=user_id, *args, **kwargs)

    return factory


@pytest.fixture
def order_factory():
    def factory(user_id, shop_id, *args, **kwargs):
        category = baker.make(Category, *args, **kwargs)
        product = baker.make(Product, category_id=category.id, *args, **kwargs)
        product_info = baker.make(ProductInfo, product_id=product.id,
                                  shop_id=shop_id, *args, **kwargs)
        contact = baker.make(Contact, user_id=user_id, *args, **kwargs)
        order = baker.make(Order, status='new', user_id=user_id,
                           contact_id=contact.id, *args, **kwargs)
        baker.make(OrderItem, order_id=order.id,
                   product_info_id=product_info.id,
                   quantity=1, *args, **kwargs)
        return order

    return factory


@pytest.mark.django_db
def test_partner_update_price(client, user_factory):
    """Partner update price test"""
    user, header_auth = user_factory()

    url = reverse('partner_update')
    url_yaml = ('https://raw.githubusercontent.com/netology-code/python-final-'
                'diplom/a7371c6536107f6360fe54c4fc95be15f7d19d60/data/'
                'shop1.yaml')
    response = client.post(url, data={'url': url_yaml}, headers=header_auth)

    data = response.json()
    assert data['Status']


@pytest.mark.django_db
def test_get_shop_status(client, user_factory, shop_factory):
    """Get shop status test"""
    user, header_auth = user_factory()
    shop = shop_factory(user.id)

    url = reverse('partner_state')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data['name'] == shop.name
    assert data['state'] == shop.state


@pytest.mark.django_db
def test_edit_shop_status(client, user_factory, shop_factory):
    """Edit shop status test"""
    user, header_auth = user_factory()
    shop_factory(user.id)

    url = reverse('partner_state')
    response = client.post(url, data={'state': 'True'}, headers=header_auth)

    data = response.json()
    assert data['Status']


@pytest.mark.django_db
def test_get_shop_orders(client, user_factory, shop_factory, order_factory):
    """Get shop orders test"""
    user, header_auth = user_factory()
    shop = shop_factory(user.id)
    order_factory(user.id, shop.id)

    url = reverse('partner_orders')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data[0]['status'] == 'new'
