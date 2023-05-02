from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemsInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'dt', 'contact', 'user']
    ordering = ['dt']
    inlines = [OrderItemsInline]
