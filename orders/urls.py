from django.urls import path

from orders.views import BasketView, OrderView


urlpatterns = [
    path('basket', BasketView.as_view(), name='order_basket'),
    path('orders', OrderView.as_view(), name='orders'),
]
