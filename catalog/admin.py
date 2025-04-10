from django.contrib import admin
from django.db import models
from django.core.cache import cache
from django.db.models import JSONField
from django import forms
from unfold.admin import ModelAdmin, TabularInline
from django.conf import settings
from .models import Material, Technology, Category, Product, ProductImage

## ADMIN FORMS:

# Inline admin for ProductImage - optimized
class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0  # No extra empty forms
    max_num = 10  # Limit maximum number of images
    show_change_link = True
    classes = ['collapse']  # Collapsible by default to speed up initial load

# Admin form for Material
class MaterialAdminForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        help_texts = {
            'name': "Назва матеріалу, наприклад, PLA, ABS, PETG.",
            'description': "Короткий опис матеріалу, його властивості та застосування."
        }

# Admin form for Technology
class TechnologyAdminForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = '__all__'
        help_texts = {
            'name': "Назва технології 3D-друку, наприклад, FDM, SLA, SLS.",
            'description': "Опис технології та її особливості."
        }

# Admin form for Category
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {
            'name': "Назва категорії, наприклад, 'Моделі для друку'.",
            'slug': "Унікальний URL-слуг для категорії, автоматично генерується з назви."
        }

# Admin form for Product
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        help_texts = {
            'name': "Введіть назву продукту (наприклад, 'Корпус Arduino').",
            'slug': "Автоматично генерується, або введіть власний унікальний ідентифікатор для URL.",
            'category': "Оберіть категорію для продукту, наприклад, 'Електронні компоненти'.",
            'stl_file': "Завантажте STL-файл для 3D-друку. Допустимий формат: .stl.",
            'description': "Опишіть продукт, його призначення та характеристики.",
            'base_price': "Вкажіть базову ціну продукту у вибраній валюті.",
            'discount_price': "Необов'язково. Вкажіть ціну зі знижкою, якщо застосовується.",
            'currency': "Валюта, у якій відображатиметься ціна продукту.",
        }

## ADMIN INTERFACES

# Admin interface for Material - optimized
@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ('id', 'name')  # Reduced fields for faster loading
    search_fields = ('name',)  # Limited search fields
    form = MaterialAdminForm
    list_per_page = 50  # Increased pagination for faster browsing
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Матеріали, що використовуються для 3D-друку. Наприклад: PLA, ABS, PETG."
        }),
    )
    
    def get_queryset(self, request):
        # Cache the queryset for 10 minutes
        cache_key = 'material_admin_queryset'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            cache.set(cache_key, queryset, 600)  # Cache for 10 minutes
        return queryset

# Admin interface for Technology - optimized
@admin.register(Technology)
class TechnologyAdmin(ModelAdmin):
    list_display = ('name',)  # Reduced fields
    search_fields = ('name',)
    form = TechnologyAdminForm
    list_per_page = 50
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Технології 3D-друку, такі як FDM, SLA, SLS."
        }),
    )
    
    def get_queryset(self, request):
        cache_key = 'technology_admin_queryset'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            cache.set(cache_key, queryset, 600)
        return queryset

# Admin interface for Category - optimized
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    form = CategoryAdminForm
    list_per_page = 50
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug'),
            'description': "Категорії для класифікації 3D-моделей та матеріалів."
        }),
    )
    
    def get_queryset(self, request):
        cache_key = 'category_admin_queryset'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            cache.set(cache_key, queryset, 600)
        return queryset

# Admin interface for Product - optimized
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'discount_price']
    list_filter = ['category']
    list_editable = ['base_price', 'discount_price']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']  # Reduced search fields
    ordering = ['name']
    form = ProductAdminForm
    inlines = [ProductImageInline]
    list_per_page = 25  # Smaller page size for products due to images
    list_select_related = ['category']  # Reduce DB queries with select_related
    raw_id_fields = ['category']  # Use popup for selecting categories
    
    # Save queries when only specific fields are needed
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['name', 'category', 'base_price', 'discount_price']
        return ['name', 'base_price']
    
    fieldsets = (
        (None, {
            'fields': (),
            'description': "Продукти, які присутні в онлайн-магазині."
        }),
        ("Основна інформація", {
            'fields': ('name', 'slug', 'category', 'description'),
            'description': "Заповніть основні дані про продукт, призначений для 3D-друку."
        }),
        ("Файли та медіа", {
            'fields': ('stl_file',),
            'description': "Завантажте STL-файл, який використовується для 3D-друку."
        }),
        ("Ціни", {
            'fields': ('base_price', 'discount_price'),
            'description': "Укажіть ціну товару."
        }),
    )
    
    def get_queryset(self, request):
        # Use a shorter cache time for products (2 minutes) as they change more often
        cache_key = f'product_admin_queryset_{request.user.id}'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request).select_related('category')
            cache.set(cache_key, queryset, 120)  # Cache for 2 minutes
        return queryset
    
    def save_model(self, request, obj, form, change):
        # Clear cache when a product is saved
        cache.delete(f'product_admin_queryset_{request.user.id}')
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Clear cache when a product is deleted
        cache.delete(f'product_admin_queryset_{request.user.id}')
        super().delete_model(request, obj)