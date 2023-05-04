import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from partners.models import Shop
from products.models import Category, ProductInfo, Product
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        user = baker.make(User, is_active=True, *args, **kwargs)
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
def category_factory():
    def factory(*args, **kwargs):
        return baker.make(Category, *args, **kwargs)

    return factory


@pytest.fixture
def product_factory():
    def factory(category_id, shop_id, *args, **kwargs):
        product = baker.make(Product, category_id=category_id, *args, **kwargs)
        return baker.make(ProductInfo, product_id=product.id,
                          shop_id=shop_id, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_categories(client, user_factory, category_factory):
    """Get categories test"""
    user, header_auth = user_factory()
    category = category_factory()

    url = reverse('product_categories')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data['results'][0]['name'] == category.name


@pytest.mark.django_db
def test_get_shops(client, user_factory, shop_factory):
    """Get shops test"""
    user, header_auth = user_factory()
    shop = shop_factory(user.id)

    url = reverse('product_shops')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data['results'][0]['name'] == shop.name


@pytest.mark.django_db
def test_get_products(client, user_factory, product_factory,
                      category_factory, shop_factory):
    """Get products test"""
    user, header_auth = user_factory()
    category = category_factory()
    shop = shop_factory(user.id)
    product_factory(category.id, shop.id)

    url = reverse('products')
    response = client.get(url,
                          data={'shop_id': shop.id,
                                'category_id': category.id},
                          headers=header_auth)

    data = response.json()
    assert data['results'][0]['product']['category'] == category.name
