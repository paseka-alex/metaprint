from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import PrintReport, PlasticReceiptReport, PlasticReceiptItem, CombinedSummary
from django import forms

# Custom form for CombinedSummary with help texts for each field
class CombinedSummaryForm(forms.ModelForm):
    class Meta:
        model = CombinedSummary
        fields = '__all__'
        help_texts = {
            'printer_nickname': "Нікнейм друкаря/його ім'я.",
            'total_reels_received': "Загальна кількість отриманих катушок, незалежно від виду, за весь час. ",
            'total_printed': "Загальна кількість надрукованих одиниць за весь час.",
            'total_weight': "Загальна вага надрукованих виробів у грамах за весь час.",
        }

# Admin interface for CombinedSummary
@admin.register(CombinedSummary)
class CombinedSummaryAdmin(ModelAdmin):
    form = CombinedSummaryForm  # Use custom form
    list_display = ('printer_nickname', 'total_reels_received', 'total_printed', 'total_weight')  # Fields to display in the list
    search_fields = ('printer_nickname',)  # Make 'printer_nickname' searchable
    readonly_fields = ('printer_nickname', 'total_reels_received', 'total_printed', 'total_weight')  # Make some fields read-only

    def has_add_permission(self, request):
        # Allow adding new printer nicknames
        return True
        
    def has_change_permission(self, request, obj=None):
        # Allow changing printer nickname but not the calculated fields
        return True

# Custom form for PrintReport with help texts
class PrintReportForm(forms.ModelForm):
    class Meta:
        model = PrintReport
        fields = '__all__'
        help_texts = {
            'printer_nickname': "Нік друкаря, який виконує друк.",
            'print_photo': "Фото результату друку.",
            'product_name': "Назва виробу, що друкується.",
            'start_date': "Дата початку друку.",
            'end_date': "Дата завершення друку.",
            'quantity_printed': "Кількість надрукованих одиниць.",
            'printed_weight': "Вага надрукованого виробу в грамах.",
            'materials_used': "Матеріали, використані для друку.",
        }

# Custom form for PlasticReceiptReport with help texts
class PlasticReceiptReportForm(forms.ModelForm):
    class Meta:
        model = PlasticReceiptReport
        fields = '__all__'
        help_texts = {
            'printer_nickname': "Нік друкаря, який отримав матеріал.",
            'receipt_date': "Дата отримання матеріалу.",
        }

# Custom form for PlasticReceiptItem with help texts
class PlasticReceiptItemForm(forms.ModelForm):
    class Meta:
        model = PlasticReceiptItem
        fields = '__all__'
        help_texts = {
            'report': "Звіт, до якого належить цей елемент.",
            'material': "Матеріал, який отримується.",
            'quantity': "Кількість катушок матеріалу.",
        }

# Inline model for PlasticReceiptItem in PlasticReceiptReport
class PlasticReceiptItemInline(TabularInline):
    model = PlasticReceiptItem  # The model for the inline
    extra = 1  # Number of empty forms to display
    fields = ('material', 'quantity')  # Fields to display in the inline form
    verbose_name = "Елемент отримання пластику"  # Singular name for the inline
    verbose_name_plural = "Елементи отримання пластику"  # Plural name for the inline

# Admin interface for PrintReport
@admin.register(PrintReport)
class PrintReportAdmin(ModelAdmin):
    form = PrintReportForm  # Use custom form
    list_display = [
        'printer_nickname', 'product_name', 'start_date', 'end_date', 
        'quantity_printed', 'printed_weight'
    ]  # Fields to display in the list
    search_fields = ['printer_nickname', 'product_name']  # Searchable fields
    list_filter = ['start_date', 'end_date']  # Filter by start and end date
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'print_photo', 'product_name', 
                       'start_date', 'end_date', 'quantity_printed', 
                       'printed_weight', 'materials_used'),
            'description': "Деталі звіту про друк."  # Description for the fieldset
        }),
    )

# Admin interface for PlasticReceiptReport
@admin.register(PlasticReceiptReport)
class PlasticReceiptReportAdmin(ModelAdmin):
    form = PlasticReceiptReportForm  # Use custom form
    list_display = ['printer_nickname', 'receipt_date']  # Fields to display in the list
    search_fields = ['printer_nickname']  # Searchable fields
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'receipt_date'),
            'description': "Звіт про отримання пластику."  # Description for the fieldset
        }),
    )
    inlines = [PlasticReceiptItemInline]  # Inline model for PlasticReceiptItem
