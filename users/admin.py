from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, Contact


class ContactsInline(admin.TabularInline):
    model = Contact
    extra = 0


class UserPanelAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", 'email', 'password',
                           'company', 'position', 'is_active', 'type',
                           'is_superuser', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("first_name", "last_name", "email",
                           "password1", "password2", "company", "position",
                           "is_active", "type", "is_superuser", "is_staff"),
                },),
    )
    list_display = ['id', 'first_name', 'last_name',
                    'email', 'company', 'type', 'is_active']
    list_filter = ['type']
    ordering = ['id']
    inlines = [ContactsInline, ]


admin.site.register(User, UserPanelAdmin)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'phone', 'user']
    ordering = ['id']
