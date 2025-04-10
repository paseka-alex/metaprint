from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from django.core.cache import cache
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PrintReport, PlasticReceiptReport, PlasticReceiptItem, CombinedSummary

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

# Optimized inline model for PlasticReceiptItem
class PlasticReceiptItemInline(TabularInline):
    model = PlasticReceiptItem
    extra = 0  # Reduced from 1 to 0 for faster page load
    max_num = 10  # Limit maximum number of items
    fields = ('material', 'quantity')
    verbose_name = "Елемент отримання пластику"
    verbose_name_plural = "Елементи отримання пластику"
    classes = ['collapse']  # Collapsible by default
    form = PlasticReceiptItemForm  # Use the custom form
    raw_id_fields = ('material',)  # Use raw_id for materials selector

# Admin interface for CombinedSummary - optimized
@admin.register(CombinedSummary)
class CombinedSummaryAdmin(ModelAdmin):
    form = CombinedSummaryForm
    list_display = ('printer_nickname', 'total_reels_received', 'total_printed', 'total_weight')
    search_fields = ('printer_nickname',)
    readonly_fields = ('total_reels_received', 'total_printed', 'total_weight')
    list_per_page = 50  # Increase pagination for faster browsing
    
    def has_add_permission(self, request):
        return True
        
    def has_change_permission(self, request, obj=None):
        return True
    
    def get_queryset(self, request):
        # Cache the queryset for 5 minutes (summary data changes frequently)
        cache_key = 'combined_summary_admin_queryset'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
        return queryset
    
    def save_model(self, request, obj, form, change):
        # Clear cache when a summary is saved
        cache.delete('combined_summary_admin_queryset')
        super().save_model(request, obj, form, change)

# Admin interface for PrintReport - optimized
@admin.register(PrintReport)
class PrintReportAdmin(ModelAdmin):
    form = PrintReportForm
    list_display = [
        'printer_nickname', 'product_name', 'start_date', 'end_date', 
        'quantity_printed', 'printed_weight'
    ]
    search_fields = ['printer_nickname', 'product_name']
    list_filter = ['start_date', 'end_date']
    list_per_page = 30
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'product_name', 'start_date', 
                      'end_date', 'quantity_printed', 'printed_weight', 
                      'materials_used'),
            'description': "Деталі звіту про друк."
        }),
        (_('Медіа'), {
            'fields': ('print_photo',),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        cache_key = f'print_report_admin_queryset_{request.user.id}'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            # Удаляем неправильный select_related
            cache.set(cache_key, queryset, 120)
        return queryset
    
    def save_model(self, request, obj, form, change):
        # Clear caches when a print report is saved
        cache.delete(f'print_report_admin_queryset_{request.user.id}')
        cache.delete('combined_summary_admin_queryset')  # Also clear summary cache
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Clear caches when a print report is deleted
        cache.delete(f'print_report_admin_queryset_{request.user.id}')
        cache.delete('combined_summary_admin_queryset')
        super().delete_model(request, obj)

# Admin interface for PlasticReceiptReport - optimized
@admin.register(PlasticReceiptReport)
class PlasticReceiptReportAdmin(ModelAdmin):
    form = PlasticReceiptReportForm
    list_display = ['printer_nickname', 'receipt_date', 'get_total_items']
    search_fields = ['printer_nickname']
    list_per_page = 30
    date_hierarchy = 'receipt_date'  # Adds date-based drilldown navigation
    
    fieldsets = (
        (None, {
            'fields': ('printer_nickname', 'receipt_date'),
            'description': "Звіт про отримання пластику."
        }),
    )
    inlines = [PlasticReceiptItemInline]
    
    def get_total_items(self, obj):
        # Use caching for this calculation
        cache_key = f'plastic_receipt_total_items_{obj.id}'
        total = cache.get(cache_key)
        if total is None:
            total = obj.plasticreceiptitem_set.count()
            cache.set(cache_key, total, 300)  # Cache for 5 minutes
        return total
    get_total_items.short_description = 'Кількість елементів'
    
    def get_queryset(self, request):
        # Cache PlasticReceiptReport queryset for 2 minutes
        cache_key = f'plastic_receipt_admin_queryset_{request.user.id}'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_queryset(request)
            cache.set(cache_key, queryset, 120)  # Cache for 2 minutes
        return queryset
    
    def save_model(self, request, obj, form, change):
        # Clear caches when a receipt report is saved
        cache.delete(f'plastic_receipt_admin_queryset_{request.user.id}')
        cache.delete('combined_summary_admin_queryset')
        cache.delete(f'plastic_receipt_total_items_{obj.id}')
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Clear caches when a receipt report is deleted
        cache.delete(f'plastic_receipt_admin_queryset_{request.user.id}')
        cache.delete('combined_summary_admin_queryset')
        cache.delete(f'plastic_receipt_total_items_{obj.id}')
        super().delete_model(request, obj)
