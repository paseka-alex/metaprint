from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from django import forms  # Import forms
from django.db import models
from django.db.models import JSONField
from .models import Material, Technology, Category, Product, ProductImage

# Inline admin for ProductImage
class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0  # No extra empty forms

# Admin form for Material
class MaterialAdminForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        help_texts = {
            'name': "Назва матеріалу, наприклад, PLA, ABS, PETG.",  # Material name, e.g., PLA, ABS, PETG.
            'description': "Короткий опис матеріалу, його властивості та застосування."  # Brief description of the material, its properties, and applications.
        }

# Admin form for Technology
class TechnologyAdminForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = '__all__'
        help_texts = {
            'name': "Назва технології 3D-друку, наприклад, FDM, SLA, SLS.",  # Name of the 3D printing technology, e.g., FDM, SLA, SLS.
            'description': "Опис технології та її особливості."  # Description of the technology and its features.
        }

# Admin form for Category
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {
            'name': "Назва категорії, наприклад, 'Моделі для друку'.",  # Category name, e.g., 'Models for printing'.
            'slug': "Унікальний URL-слуг для категорії, автоматично генерується з назви."  # Unique URL slug for the category, automatically generated from the name.
        }

# Admin interface for Material
@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ('id', 'name', 'description')  # Columns to display in the admin list view
    search_fields = ('name', 'description')  # Fields to search in the admin
    form = MaterialAdminForm  # Use the custom form
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Матеріали, що використовуються для 3D-друку. Наприклад: PLA, ABS, PETG."  # Materials used for 3D printing, e.g., PLA, ABS, PETG.
        }),
    )

# Admin interface for Technology
@admin.register(Technology)
class TechnologyAdmin(ModelAdmin):
    list_display = ('name', 'description')  # Columns to display in the admin list view
    search_fields = ('name', 'description')  # Fields to search in the admin
    form = TechnologyAdminForm  # Use the custom form
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Технології 3D-друку, такі як FDM, SLA, SLS."  # 3D printing technologies such as FDM, SLA, SLS.
        }),
    )

# Admin interface for Category
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')  # Columns to display in the admin list view
    search_fields = ('name',)  # Fields to search in the admin
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name
    form = CategoryAdminForm  # Use the custom form
    fieldsets = (
        (None, {
            'fields': ('name', 'slug'),
            'description': "Категорії для класифікації 3D-моделей та матеріалів."  # Categories for classifying 3D models and materials.
        }),
    )

# Admin form for Product
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        help_texts = {
            'name': "Введіть назву продукту (наприклад, 'Корпус Arduino').",  # Enter the product name (e.g., 'Arduino Case').
            'slug': "Автоматично генерується, або введіть власний унікальний ідентифікатор для URL.",  # Automatically generated, or enter your own unique identifier for the URL.
            'category': "Оберіть категорію для продукту, наприклад, 'Електронні компоненти'.",  # Select a category for the product, e.g., 'Electronic Components'.
            'stl_file': "Завантажте STL-файл для 3D-друку. Допустимий формат: .stl.",  # Upload the STL file for 3D printing. Allowed format: .stl.
            'description': "Опишіть продукт, його призначення та характеристики.",  # Describe the product, its purpose, and features.
            'base_price': "Вкажіть базову ціну продукту у вибраній валюті.",  # Specify the base price of the product in the selected currency.
            'discount_price': "Необов'язково. Вкажіть ціну зі знижкою, якщо застосовується.",  # Optional. Specify the discounted price if applicable.
            'currency': "Валюта, у якій відображатиметься ціна продукту.",  # The currency in which the product price will be displayed.
        }

# Admin interface for Product
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'base_price', 'discount_price']  # Columns to display in the admin list view
    list_filter = ['category']  # Filter products by category
    list_editable = ['base_price', 'discount_price']  # Fields that can be edited directly in the list view
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name
    search_fields = ['name', 'description']  # Fields to search in the admin
    ordering = ['name']  # Default ordering of products
    form = ProductAdminForm  # Use the custom form
    inlines = [ProductImageInline]  # Inline for product images
    fieldsets = (
        (None, {
            'fields': (),
            'description': "Продукти, які присутні в онлайн-магазині."  # Products available in the online store.
        }),
        ("Основна інформація", {
            'fields': ('name', 'slug', 'category', 'description'),
            'description': "Заповніть основні дані про продукт, призначений для 3D-друку."  # Fill in the basic details about the product intended for 3D printing.
        }),
        ("Файли та медіа", {
            'fields': ('stl_file',),
            'description': "Завантажте STL-файл, який використовується для 3D-друку."  # Upload the STL file used for 3D printing.
        }),
        ("Ціни", {
            'fields': ('base_price', 'discount_price'),
            'description': "Укажіть ціну товару."  # Specify the product price.
        }),
    )