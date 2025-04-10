from django.db import models
from django.db.models import Sum
from catalog.models import Material   # Import Material model for use in the reports

# Model representing a print report
class PrintReport(models.Model):
    printer_nickname = models.CharField(max_length=100, verbose_name="Нік друкаря")  # Nickname of the printer
    print_photo = models.ImageField(upload_to='print_reports/', null=True, blank=True, verbose_name="Фото результату")  # Optional image of the print result
    product_name = models.CharField(max_length=200, verbose_name="Назва виробу")  # Name of the product being printed
    start_date = models.DateTimeField(verbose_name="Дата початку друку")  # Start date of the print job
    end_date = models.DateTimeField(verbose_name="Дата завершення друку")  # End date of the print job
    quantity_printed = models.IntegerField(verbose_name="Кількість надруковано")  # Number of units printed
    printed_weight = models.FloatField(verbose_name="Вага надрукованого (грам)")  # Weight of the printed products in grams
    materials_used = models.ManyToManyField(Material, verbose_name="Використані матеріали", related_name="used_in_reports")  # Materials used for printing

    class Meta:
        verbose_name = "Звітність по друку"  # Display name for a single report
        verbose_name_plural = "Звітності по друку"  # Display name for multiple reports

    def __str__(self):
        return f"{self.product_name} — {self.printer_nickname} ({self.start_date.date()})"  # String representation of the print report

# Model representing a plastic receipt report
class PlasticReceiptReport(models.Model):
    printer_nickname = models.CharField(max_length=100, verbose_name="Нік друкаря")  # Nickname of the printer
    receipt_date = models.DateTimeField(verbose_name="Дата отримання")  # Date the plastic was received

    class Meta:
        verbose_name = "Звіт про отримання пластику"  # Display name for a single receipt report
        verbose_name_plural = "Звіти про отримання пластику"  # Display name for multiple receipt reports

    def __str__(self):
        return f"Отримання: {self.printer_nickname} ({self.receipt_date.date()})"  # String representation of the plastic receipt report

# Model representing an item in a plastic receipt report
class PlasticReceiptItem(models.Model):
    report = models.ForeignKey(
        PlasticReceiptReport,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Звіт"  # Link to the corresponding plastic receipt report
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        verbose_name="Матеріал"  # Material used in the plastic receipt item
    )
    quantity = models.PositiveIntegerField(verbose_name="Кількість катушок")  # Quantity of reels received

    class Meta:
        verbose_name = "Елемент отримання пластику"  # Display name for a single receipt item
        verbose_name_plural = "Елементи отримання пластику"  # Display name for multiple receipt items

    def __str__(self):
        return f"{self.material.name} — {self.quantity} шт."  # String representation of the plastic receipt item

# Model representing the combined summary for a printer's activities
class CombinedSummary(models.Model):
    printer_nickname = models.CharField(max_length=100, unique=True, verbose_name="Нік друкаря")  # Nickname of the printer
    total_reels_received = models.PositiveIntegerField(default=0, verbose_name="Загальна кількість отриманих катушок")  # Total number of reels received
    total_printed = models.PositiveIntegerField(default=0, verbose_name="Загальна кількість надрукованих одиниць")  # Total number of units printed
    total_weight = models.FloatField(default=0.0, verbose_name="Загальна вага надрукованих виробів (грам)")  # Total weight of printed products

    def update_summary(self):
        """Update or calculate the aggregated summary."""
        # Calculate the total number of reels received for this printer
        self.total_reels_received = PlasticReceiptReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('items__quantity'))['items__quantity__sum'] or 0
        # Calculate the total number of units printed for this printer
        self.total_printed = PrintReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('quantity_printed'))['quantity_printed__sum'] or 0
        # Calculate the total weight of printed products for this printer
        self.total_weight = PrintReport.objects.filter(printer_nickname=self.printer_nickname) \
            .aggregate(Sum('printed_weight'))['printed_weight__sum'] or 0.0

    class Meta:
        verbose_name = "Загальна звітність друкарів"  # Display name for a single combined summary
        verbose_name_plural = "Загальна звітність друкарів"  # Display name for multiple combined summaries

    def save(self, *args, **kwargs):
        # Recalculate the summary before saving
        self.update_summary()
        super().save(*args, **kwargs)  # Call the parent save method to actually save the object

    def __str__(self):  # String representation of the combined summary
        return f"Summary for {self.printer_nickname}"  # Display the summary for a specific printer
