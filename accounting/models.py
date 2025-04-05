from django.db import models
from django.db.models import Sum
from catalog.models import Material  


class PrintReport(models.Model):
    printer_nickname = models.CharField(max_length=100, verbose_name="Нік друкаря")
    print_photo = models.ImageField(upload_to='print_reports/', null=True, blank=True, verbose_name="Фото результату")
    product_name = models.CharField(max_length=200, verbose_name="Назва виробу")
    start_date = models.DateTimeField(verbose_name="Дата початку друку")
    end_date = models.DateTimeField(verbose_name="Дата завершення друку")
    quantity_printed = models.IntegerField(verbose_name="Кількість надруковано")
    printed_weight = models.FloatField(verbose_name="Вага надрукованого (грам)")
    materials_used = models.ManyToManyField(Material, verbose_name="Використані матеріали", related_name="used_in_reports")

    class Meta:
        verbose_name = "Звітність по друку"
        verbose_name_plural = "Звітності по друку"

    def __str__(self):
        return f"{self.product_name} — {self.printer_nickname} ({self.start_date.date()})"


class PlasticReceiptReport(models.Model):
    printer_nickname = models.CharField(max_length=100, verbose_name="Нік друкаря")
    receipt_date = models.DateTimeField(verbose_name="Дата отримання")

    class Meta:
        verbose_name = "Звіт про отримання пластику"
        verbose_name_plural = "Звіти про отримання пластику"

    def __str__(self):
        return f"Отримання: {self.printer_nickname} ({self.receipt_date.date()})"


class PlasticReceiptItem(models.Model):
    report = models.ForeignKey(
        PlasticReceiptReport,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Звіт"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        verbose_name="Матеріал"
    )
    quantity = models.PositiveIntegerField(verbose_name="Кількість катушок")

    class Meta:
        verbose_name = "Елемент отримання пластику"
        verbose_name_plural = "Елементи отримання пластику"

    def __str__(self):
        return f"{self.material.name} — {self.quantity} шт."

class CombinedSummary(models.Model):
    printer_nickname = models.CharField(max_length=100, unique=True, verbose_name="Нік друкаря")
    total_reels_received = models.PositiveIntegerField(default=0, verbose_name="Загальна кількість отриманих катушок")
    total_printed = models.PositiveIntegerField(default=0, verbose_name="Загальна кількість надрукованих одиниць")
    total_weight = models.FloatField(default=0.0, verbose_name="Загальна вага надрукованих виробів (грам)")
    
    def update_summary(self):
        """Update or calculate the aggregated summary."""
        self.total_reels_received = PlasticReceiptReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('items__quantity'))['items__quantity__sum'] or 0
        self.total_printed = PrintReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('quantity_printed'))['quantity_printed__sum'] or 0
        self.total_weight = PrintReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('printed_weight'))['printed_weight__sum'] or 0.0

    class Meta:
        verbose_name = "Загальна звітність друкарів"
        verbose_name_plural = "Загальна звітність друкарів"

    def save(self, *args, **kwargs):
        # Recalculate the summary before saving
        self.update_summary()
        super().save(*args, **kwargs)
    
    def __str__(self):  # Corrected from **str**
        return f"Summary for {self.printer_nickname}"


