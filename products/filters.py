from django_filters import FilterSet, filters

from products.models import ProductInfo


class ProductFilter(FilterSet):
    category_id = filters.NumberFilter('product__category_id')

    class Meta:
        model = ProductInfo
        fields = ['shop_id', 'category_id']
