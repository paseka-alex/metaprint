from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models import F
from decimal import Decimal

from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator

import uuid

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    colors = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Матеріал'
        verbose_name_plural = 'Матеріали'
    
    def __str__(self):
        return self.name

class Technology(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Технологія'
        verbose_name_plural = 'Технології'

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

def validate_stl_file(value):
    """Validate that the uploaded file is a valid STL file."""
    if not value.name.endswith('.stl'):
        raise ValidationError('Only STL files are allowed.')

class Product(models.Model):
    # Основні поля
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)  # Категорія продукту
    name = models.CharField('Назва', max_length=200, db_index=True)  # Назва продукту
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # URL-частина для продукту

    # Медійні файли
    stl_file = models.FileField(
        'STL файл',
        upload_to='stl_files/',
        null=True,
        blank=True,
        validators=[validate_stl_file]  # Валідація STL файлів
    )

    # Опис та характеристики
    description = models.TextField('Опис', blank=True)  # Опис продукту

    # Ціни та наявність
    base_price = MoneyField(
        'Базова ціна',
        max_digits=10,
        decimal_places=2,
        default_currency='UAH',  # Устанавливаем базовую валюту UAH
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Минимальная цена 10 UAH
    )

    discount_price = MoneyField(
        'Ціна зі знижкою',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,  # Може бути пустою
        default_currency='UAH',
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Минимальная цена 0 UAH
    )

    class Meta:
        ordering = ('name',)  # Сортування за назвою
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукти'

    def __str__(self):
        return f"{self.name} ({self.id})"  # Відображення назви продукту

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.discount_price and self.discount_price >= self.base_price:
            raise ValidationError("Ціна зі знижкою повинна бути меншою за базову ціну")
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                      args=[str(self.id), self.slug])  # конвертуємо UUID в рядок

    @property
    def current_price(self):
        """Повертає актуальну ціну (зі знижкою, якщо є)"""
        return self.discount_price if self.discount_price else self.base_price

    @property
    def discount_percentage(self):
        """Повертає відсоток знижки"""
        if self.discount_price:
            return round((1 - self.discount_price.amount / self.base_price.amount) * 100)
        return 0

    @classmethod
    def get_related_products(cls, product, limit=4):
        """Отримує схожі продукти"""
        return cls.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:limit]

    def get_price_in_currency(self, currency_code='UAH'):
        """Метод для отримання ціни в конкретній валюті"""
        # Потрібно додавати обробку конвертації через API або вручну, якщо валюти відрізняються
        if self.base_price.currency == currency_code:
            return self.base_price

        # Якщо валюта не збігається, застосовуємо конвертацію (потрібно реалізувати)
        # Наприклад, ви можете використовувати API для отримання актуальних курсів валют.

        return self.base_price  # Для прикладу, якщо конвертація не реалізована

    @property
    def main_image(self):
        """Returns the main image of the product"""
        return self.images.first()

    @property
    def all_images(self):
        """Returns all images of the product ordered by the specified order"""
        return self.images.all()

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='images', 
        on_delete=models.CASCADE,
        help_text="Продукт, до якого належить це зображення."
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        help_text="Завантажте файл зображення продукту."
    )
    alt_text = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Додатковий текст до зображення, використовується для SEO та доступності."
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Зображення продукту'  # Назва в адмінці

    def __str__(self):
        return f"Зображення для {self.product.name}"


