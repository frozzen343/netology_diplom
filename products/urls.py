from django.urls import path

from products.views import CategoryView, ShopView, ProductInfoView


urlpatterns = [
    path('categories', CategoryView.as_view(), name='product_categories'),
    path('shops', ShopView.as_view(), name='product_shops'),
    path('products', ProductInfoView.as_view(), name='products'),
]
