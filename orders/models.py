from django.db import models
from catalog.models import Product, Material, Technology

from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djmoney.models.validators import MinMoneyValidator
import uuid

## MODEL ORDER represents an order placed by a customer
class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Ім\'я')  # Customer's first name
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Прізвище')  # Customer's last name (optional)
    telegram_nick = models.CharField(max_length=32, verbose_name='Telegram нікнейм')  # Customer's Telegram username
    telegram_user_id = models.CharField(max_length=255, null=True, blank=True)  # Добавлено поле для ID пользователя Telegram
    address = models.CharField(max_length=250, blank=True, verbose_name='Адреса доставки')  # Shipping address (optional)
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')  # Postal code (optional)
    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')  # City (optional)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')  # Date the order was created
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')  # Date the order was last updated
    paid = models.BooleanField(default=False, verbose_name='Оплачено')  # Payment status of the order
    status = models.CharField(max_length=250, blank=True, verbose_name='Статус замовлення')  # Order status (e.g., pending, shipped)
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')  # Delivery date (optional)
    tracking_number = models.CharField(max_length=50, blank=True, verbose_name='Номер відстеження')  # Tracking number (optional)
    total_cost = MoneyField(
        max_digits=10,
        decimal_places=2,
        default=Money(0, 'UAH'),  # Default cost is set to 0 UAH
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Minimum cost is 0 UAH
    )

    class Meta:
        ordering = ('-created',)  # Orders are listed in reverse order by creation date
        verbose_name = 'Замовлення'  # Singular name for the order model
        verbose_name_plural = 'Замовлення'  # Plural name for the order model
    
    def __str__(self):
        return 'Замовлення {}'.format(self.id)  # Return a string representation of the order using its ID
    
    def calculate_total_cost(self):
        """Calculates the total cost of the order"""
        for item in self.items.all():  # Loop through all items in the order
            cost = item.get_cost()  # Get the cost of each item
            print(f"[DEBUG] Item ID: {item.id}, Cost: {cost}, Type: {type(cost)}")  # Debugging output to check the cost type
        total = sum((item.get_cost() for item in self.items.all()), Money(0, 'UAH'))  # Sum up the cost of all items
        self.total_cost = total  # Set the total cost of the order
        self.save()  # Save the order with the updated total cost

    def save(self, *args, **kwargs):
        """Generate a tracking number if it hasn't been set yet"""
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4())  # Generate a unique tracking number using uuid
        super().save(*args, **kwargs)  # Call the parent class's save method to save the order


## ORDERITEM MODEL represents an individual item in the order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Замовлення')  # ForeignKey to the Order
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Товар')  # ForeignKey to the Product (optional)
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default=Money(0, 'UAH'),  # Default currency is UAH
        validators=[MinMoneyValidator(Money(0, 'UAH'))]  # Minimum price is 0 UAH
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість', null=True, blank=True)  # Quantity of the product (default is 1)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Матеріал')  # ForeignKey to Material (optional)
    postprocessing = models.BooleanField(default=False, verbose_name='Постпроцесинг', null=True, blank=True)  # Boolean flag for post-processing (optional)
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Технологія')  # ForeignKey to Technology (optional)
    order_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва замовлення")  # Optional custom name for the order item

    class Meta:
        verbose_name = "Замов. об'єкт"  # Singular name for the order item model
        verbose_name_plural = "Замов. об'єкти"  # Plural name for the order item model

    def __str__(self):
        return '{}'.format(self.id)  # Return a string representation of the order item using its ID

    def get_cost(self):
        return self.price * self.quantity  # Calculate the total cost of the item based on price and quantity
