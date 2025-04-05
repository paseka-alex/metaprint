from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem
from django import forms

class OrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'
        help_texts = {
            'product': "Товар, який замовлено.",
            'price': "Ціна товару на момент замовлення.",
            'quantity': "Кількість замовленого товару.",
            'material': "Матеріал, з якого виготовлено товар.",
            'technology': "Технологія, що використовується для виготовлення товару.",
            'postprocessing': "Додаткові обробки, які потрібно виконати.",
        }

class OrderItemInline(TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    raw_id_fields = ['product', 'material', 'technology']
    extra = 1

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        help_texts = {
            'first_name': "Ім'я замовника.",
            'last_name': "Прізвище замовника.",
            'telegram_nick': "Нік в Telegram для зв'язку.",
            'city': "Місто, куди потрібно доставити замовлення.",
            'paid': "Чи було оплачено замовлення?",
            'status': "Поточний статус замовлення.",
            'delivery_date': "Дата доставки замовлення.",
            'tracking_number': "Номер для відстеження доставки.",
            'address': "Адреса доставки.",
            'postal_code': "Поштовий індекс.",
            'total_cost': "Загальна вартість замовлення.",
        }

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderAdminForm
    list_display = [
        'id', 'first_name', 'last_name',
        'telegram_nick', 'city', 'paid', 'status',
        'created', 'total_cost'
    ]
    list_filter = [
        'paid', 'status', 'created', 'city'
    ]
    search_fields = [
        'first_name', 'last_name', 'telegram_nick',
        'address', 'city', 'tracking_number'
    ]
    readonly_fields = ['created', 'updated', 'total_cost']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основна інформація', {
            'fields': ('first_name', 'last_name', 'telegram_nick'),
            'description': 'Основна інформація про замовника.'
        }),
        ('Адреса доставки', {
            'fields': ('address', 'postal_code', 'city'),
            'description': 'Адреса, куди потрібно доставити замовлення.'
        }),
        ('Статус замовлення', {
            'fields': ('paid', 'status', 'delivery_date', 'tracking_number'),
            'description': 'Статус та деталі доставки замовлення.'
        }),
        ('Фінанси', {
            'fields': ('total_cost',)
        }),
        ('Системна інформація', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

class OrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'
        help_texts = {
            'order': "Замовлення, до якого належить цей товар.",
            'product': "Товар, який замовлено.",
            'price': "Ціна товару на момент замовлення.",
            'quantity': "Кількість замовленого товару.",
            'material': "Матеріал, з якого виготовлено товар.",
            'technology': "Технологія, що використовується для виготовлення товару.",
            'postprocessing': "Додаткові обробки, які потрібно виконати.",
        }

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    form = OrderItemAdminForm
    list_display = [
        'id', 'order', 'product', 'price',
        'quantity', 'material', 'technology',
        'postprocessing'
    ]
    list_filter = [
        'postprocessing', 'material', 'technology'
    ]
    search_fields = [
        'order__id', 'product__name',
        'material__name', 'technology__name'
    ]
    raw_id_fields = ['order', 'product', 'material', 'technology']
