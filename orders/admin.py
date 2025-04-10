from django.contrib import admin  # Importing Django admin for model registration
from unfold.admin import ModelAdmin, TabularInline  # Importing ModelAdmin and TabularInline from unfold (assumed custom admin)
from .models import Order, OrderItem  # Importing Order and OrderItem models from the current app
from django import forms  # Importing forms for custom form fields in admin

## INLINES & FORMS
# Custom Form for OrderItem inline editing in the Order admin page
class OrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = OrderItem  # Bind the form to the OrderItem model
        fields = '__all__'  # Include all fields from the model in the form
        help_texts = {  # Custom help text for the fields to be displayed in the admin
            'product': "Товар, який замовлено.",
            'price': "Ціна товару на момент замовлення.",
            'quantity': "Кількість замовленого товару.",
            'material': "Матеріал, з якого виготовлено товар.",
            'technology': "Технологія, що використовується для виготовлення товару.",
            'postprocessing': "Додаткові обробки, які потрібно виконати.",
        }

# Inline model admin for OrderItem to be shown within Order admin page
class OrderItemInline(TabularInline):
    model = OrderItem  # The model to be inlined
    form = OrderItemInlineForm  # Use the custom form for the inline
    raw_id_fields = ['product', 'material', 'technology']  # Use raw ID fields for these foreign keys (optimizes for large datasets)
    extra = 1  # Add one empty form by default for new order items

# Custom Form for the main Order model
class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order  # Bind the form to the Order model
        fields = '__all__'  # Include all fields from the model in the form
        help_texts = {  # Custom help text for the fields to be displayed in the admin
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
# Custom Form for the OrderItem model
class OrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderItem  # Bind the form to the OrderItem model
        fields = '__all__'  # Include all fields from the model in the form
        help_texts = {  # Custom help text for the fields to be displayed in the admin
            'order': "Замовлення, до якого належить цей товар.",
            'product': "Товар, який замовлено.",
            'price': "Ціна товару на момент замовлення.",
            'quantity': "Кількість замовленого товару.",
            'material': "Матеріал, з якого виготовлено товар.",
            'technology': "Технологія, що використовується для виготовлення товару.",
            'postprocessing': "Додаткові обробки, які потрібно виконати.",
        }


## ADMIN INTERSFACES

# Registering the Order model in the admin panel with custom settings
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderAdminForm  # Use the custom form for Order model
    list_display = [  # Fields to be displayed in the list view
        'id', 'first_name', 'last_name',
        'telegram_nick', 'city', 'paid', 'status',
        'created', 'total_cost', 'telegram_user_id'
    ]
    list_filter = [  # Filters for the list view
        'paid', 'status', 'created', 'city'
    ]
    search_fields = [  # Fields to search by
        'first_name', 'last_name', 'telegram_nick',
        'address', 'city', 'tracking_number'
    ]
    readonly_fields = ['created', 'updated', 'total_cost', 'telegram_user_id']
    inlines = [OrderItemInline]  # Display OrderItem inline within the Order admin page
    fieldsets = (  # Organize the fields into sections on the form
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
            'classes': ('collapse',)  # Collapsable section for system data
        }),
    )

# Registering the OrderItem model in the admin panel with custom settings
@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    form = OrderItemAdminForm  # Use the custom form for OrderItem model
    list_display = [  # Fields to be displayed in the list view
        'id', 'order', 'product', 'price',
        'quantity', 'material', 'technology',
        'postprocessing'
    ]
    list_filter = [  # Filters for the list view
        'postprocessing', 'material', 'technology'
    ]
    search_fields = [  # Fields to search by
        'order_id', 'product_name',
        'material_name', 'technology_name'
    ]
    raw_id_fields = ['order', 'product', 'material', 'technology']  # Use raw ID fields for foreign keys (performance optimization)
