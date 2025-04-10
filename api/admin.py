from django.contrib import admin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin  # Custom admin base class from Unfold
from django import forms

# Try importing TokenProxy (used in recent versions of DRF); fallback to Token for older versions
try:
    from rest_framework.authtoken.models import TokenProxy as DRFToken
except ImportError:
    from rest_framework.authtoken.models import Token as DRFToken

# Unregister default User model from admin if already registered
if User in admin.site._registry:
    admin.site.unregister(User)

# Unregister default Group model from admin if already registered
if Group in admin.site._registry:
    admin.site.unregister(Group)

# Unregister DRF's Token model from admin if already registered
if DRFToken in admin.site._registry:
    admin.site.unregister(DRFToken)

# Create a custom form for Token to hide the 'key' field
class TokenAdminForm(forms.ModelForm):
    class Meta:
        model = DRFToken
        fields = '__all__'

    # Hide the 'key' field from the form
    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self, commit=True):
        # Ensure the 'key' field is auto-generated
        instance = super().save(commit=False)
        if not instance.key:  # Only set if the 'key' isn't already set
            instance.save()  # This triggers the auto-generation of the key field
        return instance

# Register the Token model with the custom admin and form
@admin.register(DRFToken)
class TokenAdmin(ModelAdmin):
    form = TokenAdminForm
    list_display = ('user', 'key')  # Optionally display the user and key fields
    readonly_fields = ('key',)  # Make the 'key' field readonly in the admin panel


# Custom form for User admin with Ukrainian help texts
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

# Custom form for Group admin with Ukrainian help texts
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        help_texts = {
            'name': "Унікальна назва групи.",
            'permissions': "Дозволи, які має група.",
        }

# Custom admin class for User model
@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserAdminForm
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']  # Columns in admin list view
    search_fields = ['username', 'first_name', 'last_name', 'email']  # Fields to search by in the admin

    # Organize form fields into sections with descriptions
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

# Custom admin class for Group model
@admin.register(Group)
class GroupAdmin(ModelAdmin):
    form = GroupAdminForm
    list_display = ['name']
    search_fields = ['name']
