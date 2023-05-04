import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from orders.models import OrderItem, Order
from partners.models import Shop
from products.models import Product, Category, ProductInfo
from users.models import User, Contact


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture()
def user_factory():
    def factory(*args, **kwargs):
        user = baker.make(User, is_active=True, *args, **kwargs)
        token = Token.objects.create(user=user)
        header_auth = {'Authorization': f'Token {token.key}'}
        contact = baker.make(Contact, user=user, *args, **kwargs)
        return user, header_auth, contact

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


@pytest.fixture
def order_factory():
    def factory(user_id, contact_id, product_id, *args, **kwargs):
        order = baker.make(Order, status='new', user_id=user_id,
                           contact_id=contact_id, *args, **kwargs)
        baker.make(OrderItem, order_id=order.id,
                   product_info_id=product_id,
                   quantity=1, *args, **kwargs)
        return order

    return factory


@pytest.mark.django_db
def test_add_item_basket(client, user_factory, product_factory,
                         shop_factory, category_factory):
    """Add item to basket test"""
    user, header_auth, contact = user_factory()
    category = category_factory()
    shop = shop_factory(user.id)
    product = product_factory(category.id, shop.id)

    url = reverse('order_basket')
    products = '[{"product_info": ' + str(product.id) + ', "quantity": 34}]'
    response = client.post(url,
                           data={'items': products},
                           headers=header_auth)
    data = response.json()
    assert data['Создано объектов'] == 1


@pytest.mark.django_db
def test_get_item_basket(client, user_factory, shop_factory, order_factory,
                         product_factory, category_factory):
    """Get item from basket test"""
    user, header_auth, contact = user_factory()
    shop = shop_factory(user.id)
    category = category_factory()
    product = product_factory(category.id, shop.id)
    order = order_factory(user.id, contact.id, product.id)
    order.status = 'basket'
    order.save()

    url = reverse('order_basket')
    response = client.get(url, headers=header_auth)

    data = response.json()
    assert data[0]['ordered_items'][0]['product_info']['shop'] == shop.id


@pytest.mark.django_db
def test_edit_item_basket(client, user_factory, shop_factory, order_factory,
                          product_factory, category_factory):
    """Edit item from basket test"""
    user, header_auth, contact = user_factory()
    shop = shop_factory(user.id)
    category = category_factory()
    product = product_factory(category.id, shop.id)
    order = order_factory(user.id, contact.id, product.id)
    order.status = 'basket'
    order.save()

    order_item = OrderItem.objects.get(order_id=order.id)
    url = reverse('order_basket')
    items = '[{"id": ' + str(order_item.id) + ', "quantity": 2}]'
    response = client.put(url,
                          data={'items': items},
                          headers=header_auth)

    data = response.json()
    assert data['Обновлено объектов'] == 1


@pytest.mark.django_db
def test_del_item_basket(client, user_factory, shop_factory, order_factory,
                         product_factory, category_factory):
    """Delete item from basket test"""
    user, header_auth, contact = user_factory()
    shop = shop_factory(user.id)
    category = category_factory()
    product = product_factory(category.id, shop.id)
    order = order_factory(user.id, contact.id, product.id)
    order.status = 'basket'
    order.save()

    order_item = OrderItem.objects.get(order_id=order.id)
    url = reverse('order_basket')
    response = client.delete(url,
                             data={'items': str(order_item.id)},
                             headers=header_auth)

    data = response.json()
    assert data['Удалено объектов'] == 1


@pytest.mark.django_db
def test_get_orders(client, user_factory, shop_factory, product_factory,
                    category_factory, order_factory):
    """Get my orders test"""
    user, header_auth, contact = user_factory()
    shop = shop_factory(user.id)
    category = category_factory()
    product = product_factory(category.id, shop.id)
    order = order_factory(user.id, contact.id, product.id)
    order.status = 'new'
    order.save()

    url = reverse('orders')
    response = client.get(url, headers=header_auth)

    data = response.json()
    print(data)
    assert data[0]['ordered_items'][0]['product_info']['shop'] == shop.id


@pytest.mark.django_db
def test_make_order(client, user_factory, shop_factory, order_factory,
                    category_factory, product_factory):
    """Make order test"""
    user, header_auth, contact = user_factory()
    shop = shop_factory(user.id)
    category = category_factory()
    product = product_factory(category.id, shop.id)
    order = order_factory(user.id, contact.id, product.id)
    order.status = 'basket'
    order.save()

    url = reverse('orders')
    response = client.post(url,
                           data={'id': order.id, 'contact': contact.id},
                           headers=header_auth)

    data = response.json()
    assert data['Status']
