from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.text import slugify
# Djmoney imports to work w price and currency
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator

import uuid

## MODEL MATERIALS FOR 3D PRINTING
class Material(models.Model):
    name = models.CharField(max_length=100)  # Material name
    description = models.TextField(blank=True)  # Description of the material
    colors = models.JSONField(default=list, blank=True)  # List of colors associated with the material

    class Meta:
        ordering = ('name',)  # Order by name
        verbose_name = 'Матеріал'  # Singular name in admin
        verbose_name_plural = 'Матеріали'  # Plural name in admin
    
    def __str__(self):
        return self.name  # String representation of the material

## MODEL TECHNOLOGY FOR 3D PRINTING
class Technology(models.Model):
    name = models.CharField(max_length=100)  # Technology name
    description = models.TextField(blank=True)  # Description of the technology

    class Meta:
        ordering = ('name',)  # Order by name
        verbose_name = 'Технологія'  # Singular name in admin
        verbose_name_plural = 'Технології'  # Plural name in admin

    def __str__(self):
        return self.name  # String representation of the technology

## MODEL CATEGORY FOR ONLINE SHOP
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)  # Category name
    slug = models.SlugField(max_length=200, db_index=True, unique=True)  # Unique slug for the category

    class Meta:
        ordering = ('name',)  # Order by name
        verbose_name = 'Категорія'  # Singular name in admin
        verbose_name_plural = 'Категорії'  # Plural name in admin

    def __str__(self):
        return self.name  # String representation of the category

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])  # URL for the category

def validate_stl_file(value):
    """Validate that the uploaded file is a valid STL file."""
    if not value.name.endswith('.stl'):
        raise ValidationError('Only STL files are allowed.')  # Raise error if not an STL file

## MODEL PRODUCTS FOR ONLINE SHOP
class Product(models.Model):
    # main fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False  # UUID is not editable
    )
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)  # Product category
    name = models.CharField('Назва', max_length=200, db_index=True)  # Product name
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # URL slug for the product

    # stl file
    stl_file = models.FileField(
        'STL файл',
        upload_to='stl_files/',
        null=True,
        blank=True,
        validators=[validate_stl_file]  # Validate STL files
    )

    # product description
    description = models.TextField('Опис', blank=True)  # Product description

    # prices field
    base_price = MoneyField(
        'Базова ціна',
        max_digits=10,
        decimal_places=2,
        default_currency='UAH',  # Set default currency to UAH
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Minimum price of 0 UAH
    )

    discount_price = MoneyField(
        'Ціна зі знижкою',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,  # Can be empty
        default_currency='UAH',
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Minimum price of 0 UAH
    )

    class Meta:
        ordering = ('name',)  # Order by name
        verbose_name = 'Продукт'  # Singular name in admin
        verbose_name_plural = 'Продукти'  # Plural name in admin

    def __str__(self):
        return f"{self.name} ({self.id})"  # String representation of the product

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Generate slug from name
        if self.discount_price and self.discount_price >= self.base_price:
            raise ValidationError("Ціна зі знижкою повинна бути меншою за базову ціну")  # Validate discount price
        
        super().save(*args, **kwargs)  # Call the parent save method

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                      args=[str(self.id), self.slug])  # Convert UUID to string for URL

    @property
    def current_price(self):
        """Returns the current price (discounted if applicable)"""  
        return self.discount_price if self.discount_price else self.base_price

    @property
    def discount_percentage(self):
        """Returns the discount percentage"""  
        if self.discount_price:
            return round((1 - self.discount_price.amount / self.base_price.amount) * 100)
        return 0

    @classmethod
    def get_related_products(cls, product, limit=4):
        """Gets related products"""  
        return cls.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:limit]  # Exclude the current product

    @property
    def main_image(self):
        """Returns the main image of the product"""  
        return self.images.first()

    @property
    def all_images(self):
        """Returns all images of the product ordered by the specified order"""  
        return self.images.all()

## MODEL PRODUCTIMMAGE TO HAVE A GALLERY OF IMAGES FOR PRODUCT
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='images', 
        on_delete=models.CASCADE,
        help_text="Продукт, до якого належить це зображення."  # Product to which this image belongs
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        help_text="Завантажте файл зображення продукту."  # Upload the product image file
    )
    alt_text = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Додатковий текст до зображення, використовується для SEO та доступності."  # Alt text for the image, used for SEO and accessibility
    )

    class Meta:
        ordering = ['id']  # Order by ID
        verbose_name = 'Зображення продукту'  # Singular name in admin
        verbose_name_plural = 'Зображення продукту'

    def __str__(self):
        return f"Зображення для {self.product.name}"  # String representation of the product image


