from django.db import models
from catalog.models import Product, Material, Technology
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djmoney.models.validators import MinMoneyValidator
import uuid  # Импортируем библиотеку uuid


class Order(models.Model):

    first_name = models.CharField(max_length=50, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Прізвище')
    telegram_nick = models.CharField(max_length=32, verbose_name='Telegram нікнейм')
    address = models.CharField(max_length=250, blank=True, verbose_name='Адреса доставки')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')
    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    paid = models.BooleanField(default=False, verbose_name='Оплачено')
    status = models.CharField(max_length=250, blank=True, verbose_name='Статус замовлення')
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')
    tracking_number = models.CharField(max_length=50, blank=True, verbose_name='Номер відстеження')
    total_cost = MoneyField(
        max_digits=10,
        decimal_places=2,
        default=Money(0, 'UAH'),  # Устанавливаем значение по умолчанию
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Минимальная цена 0 UAH
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
    
    def __str__(self):
        return 'Замовлення {}'.format(self.id)
    
    def calculate_total_cost(self):
        """Обчислює загальну вартість замовлення"""
        for item in self.items.all():
            cost = item.get_cost()
            print(f"[DEBUG] Item ID: {item.id}, Cost: {cost}, Type: {type(cost)}")  # перевірка типу
        total = sum((item.get_cost() for item in self.items.all()), Money(0, 'UAH'))
        self.total_cost = total
        self.save()

    def save(self, *args, **kwargs):
        # Генерируем номер отслеживания, если он еще не установлен
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4())  # Генерация уникального номера отслеживания
        super().save(*args, **kwargs)  # Вызов метода save родительского класса


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Замовлення')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Товар')
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='UAH',  # Устанавливаем базовую валюту UAH
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Минимальная цена 0 UAH
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість', null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Матеріал')
    postprocessing = models.BooleanField(default=False, verbose_name='Постпроцесинг', null=True, blank=True)
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Технологія')
    order_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва замовлення")

    class Meta:
        verbose_name = "Замов. об'єкт"
        verbose_name_plural = "Замов. об'єкти"

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
