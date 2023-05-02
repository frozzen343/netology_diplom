from django.contrib import admin

from products.models import Product, ProductInfo, Category


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 0


class CategoryProductsInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Product)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']
    ordering = ['id']
    inlines = [ProductInfoInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']
    inlines = [CategoryProductsInline]
