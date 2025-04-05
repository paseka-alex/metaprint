from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from django import forms  # Імпортуйте forms
from django.db import models
from django.db.models import JSONField
from .models import Material, Technology, Category, Product, ProductImage


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    
class MaterialAdminForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        help_texts = {
            'name': "Назва матеріалу, наприклад, PLA, ABS, PETG.",
            'description': "Короткий опис матеріалу, його властивості та застосування."
        }

class TechnologyAdminForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = '__all__'
        help_texts = {
            'name': "Назва технології 3D-друку, наприклад, FDM, SLA, SLS.",
            'description': "Опис технології та її особливості."
        }

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {
            'name': "Назва категорії, наприклад, 'Моделі для друку'.",
            'slug': "Унікальний URL-слуг для категорії, автоматично генерується з назви."
        }

@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')
    form = MaterialAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Матеріали, що використовуються для 3D-друку. Наприклад: PLA, ABS, PETG."
        }),
    )

@admin.register(Technology)
class TechnologyAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    form = TechnologyAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Технології 3D-друку, такі як FDM, SLA, SLS."
        }),
    )
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    form = CategoryAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'slug'),
            'description': "Категорії для класифікації 3D-моделей та матеріалів."
        }),
    )

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

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'base_price', 'discount_price']
    list_filter = ['category']
    list_editable = ['base_price', 'discount_price']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    ordering = ['name']
    form = ProductAdminForm
    inlines = [ProductImageInline]
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