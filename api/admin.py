from django.contrib import admin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin
from django import forms

try:
    from rest_framework.authtoken.models import TokenProxy as DRFToken
except ImportError:
    from rest_framework.authtoken.models import Token as DRFToken

# Unregister existing User and Group models (if they are registered)
if User in admin.site._registry:
    admin.site.unregister(User)

if Group in admin.site._registry:
    admin.site.unregister(Group)

# Unregister Token if already registered
if DRFToken in admin.site._registry:
    admin.site.unregister(DRFToken)

# Register models with Unfold
@admin.register(DRFToken)
class TokenAdmin(ModelAdmin):
    pass

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        help_texts = {
            'username': "Унікальне ім'я користувача для входу.",
            'first_name': "Ім'я користувача.",
            'last_name': "Прізвище користувача.",
            'email': "Електронна адреса користувача.",
            'is_staff': "Позначте, якщо користувач має доступ до цієї адмін-панелі.",
            'is_active': "Позначте, якщо користувач активний (якщо встановлено у False, це означає, що обліковий запис користувача деактивовано, і він не зможе увійти в систему).",
            'groups': "Групи, до яких належить користувач.",
            'user_permissions': "Додаткові дозволи для користувача.",
            'date_joined': "Дата приєднання користувача (створюється автоматично).",
            'last_login': "Остання дата входу користувача (створюється автоматично).",
        }

class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        help_texts = {
            'name': "Унікальна назва групи.",
            'permissions': "Дозволи, які має група.",
        }

@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserAdminForm
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password'),
            'description': "Основна інформація про користувача."
        }),
        ('Права доступу', {
            'fields': ('is_staff', 'is_active', 'groups', 'user_permissions'),
            'description': "Налаштування прав доступу для користувача."
        }),
        ('Додаткова інформація', {
            'fields': ('date_joined', 'last_login'),
            'description': "Інформація про приєднання та останній вхід."
        }),
    )

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    form = GroupAdminForm
    list_display = ['name']
    search_fields = ['name']
