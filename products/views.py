from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from products.filters import ProductFilter
from products.models import Category, Shop, ProductInfo
from products.serializers import CategorySerializer, ShopSerializer, \
    ProductInfoSerializer


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(ListAPIView):
    """
    Класс для поиска товаров
    """
    queryset = ProductInfo.objects.select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()
    serializer_class = ProductInfoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
