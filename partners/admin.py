from django.contrib import admin

from partners.models import Shop
from products.models import ProductInfo


class ShopProductsInline(admin.TabularInline):
    model = ProductInfo
    extra = 0


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'state', 'user']
    ordering = ['id']
    list_filter = ['state']
    inlines = [ShopProductsInline, ]
