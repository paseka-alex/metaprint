from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import PrintReport, PlasticReceiptReport, PlasticReceiptItem, CombinedSummary
from django import forms

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

@admin.register(CombinedSummary)
class CombinedSummaryAdmin(ModelAdmin):
    form = CombinedSummaryForm
    list_display = ('printer_nickname', 'total_reels_received', 'total_printed', 'total_weight')
    search_fields = ('printer_nickname',)
    readonly_fields = ('printer_nickname', 'total_reels_received', 'total_printed', 'total_weight')

    def has_add_permission(self, request):
        # Allow adding new printer nicknames
        return True
        
    def has_change_permission(self, request, obj=None):
        # Allow changing printer nickname but not the calculated fields
        return True

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

class PlasticReceiptReportForm(forms.ModelForm):
    class Meta:
        model = PlasticReceiptReport
        fields = '__all__'
        help_texts = {
            'printer_nickname': "Нік друкаря, який отримав матеріал.",
            'receipt_date': "Дата отримання матеріалу.",
        }

class PlasticReceiptItemForm(forms.ModelForm):
    class Meta:
        model = PlasticReceiptItem
        fields = '__all__'
        help_texts = {
            'report': "Звіт, до якого належить цей елемент.",
            'material': "Матеріал, який отримується.",
            'quantity': "Кількість катушок матеріалу.",
        }

class PlasticReceiptItemInline(TabularInline):
    model = PlasticReceiptItem
    extra = 1  
    fields = ('material', 'quantity')
    verbose_name = "Елемент отримання пластику"
    verbose_name_plural = "Елементи отримання пластику"

@admin.register(PrintReport)
class PrintReportAdmin(ModelAdmin):
    form = PrintReportForm
    list_display = [
        'printer_nickname', 'product_name', 'start_date', 'end_date', 
        'quantity_printed', 'printed_weight'
    ]
    search_fields = ['printer_nickname', 'product_name']
    list_filter = ['start_date', 'end_date']
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'print_photo', 'product_name', 
                       'start_date', 'end_date', 'quantity_printed', 
                       'printed_weight', 'materials_used'),
            'description': "Деталі звіту про друк."
        }),
    )

@admin.register(PlasticReceiptReport)
class PlasticReceiptReportAdmin(ModelAdmin):
    form = PlasticReceiptReportForm
    list_display = ['printer_nickname', 'receipt_date']
    search_fields = ['printer_nickname']
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'receipt_date'),
            'description': "Звіт про отримання пластику."
        }),
    )
    inlines = [PlasticReceiptItemInline] 
