from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Account

class AccountAdmin(UserAdmin):
    model = Account
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # For non-superusers, show only their own account and meter readers they manage
        if not request.user.is_superuser:
            if request.user.role == Account.Role.ADMIN:
                # Admins can see all users
                return qs
            elif request.user.role == Account.Role.METER_READER:
                # Meter readers can only see themselves and their customers
                return qs.filter(
                    models.Q(pk=request.user.pk) | 
                    models.Q(role=Account.Role.CUSTOMER, client_profile__assigned_meter_reader=request.user)
                )
            else:
                # Customers can only see themselves
                return qs.filter(pk=request.user.pk)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only superusers can change roles and permissions
        if not request.user.is_superuser:
            if 'role' in form.base_fields:
                form.base_fields['role'].disabled = True
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True
            if 'groups' in form.base_fields:
                form.base_fields['groups'].disabled = True
        return form

admin.site.register(Account, AccountAdmin)
