from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from accounting.models import PrintReport, PlasticReceiptReport, CombinedSummary, PlasticReceiptItem

# Signal handler for save operations on PrintReport and PlasticReceiptReport
@receiver(post_save, sender=PrintReport)
@receiver(post_save, sender=PlasticReceiptReport)
def update_combined_summary_on_save(sender, instance, created, **kwargs):
    if isinstance(instance, PrintReport):
        printer_nickname = instance.printer_nickname
        is_print_report = True
    elif isinstance(instance, PlasticReceiptReport):
        printer_nickname = instance.printer_nickname
        is_print_report = False
    else:
        return

    summary, created = CombinedSummary.objects.get_or_create(printer_nickname=printer_nickname)

    if not created:
        if is_print_report:
            old_value = instance.__class__.objects.get(id=instance.id).quantity_printed
            diff = instance.quantity_printed - old_value
            summary.total_printed += diff
        else:
            old_quantity = PlasticReceiptItem.objects.filter(report__id=instance.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
            new_quantity = PlasticReceiptItem.objects.filter(report__id=instance.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
            diff = new_quantity - old_quantity
            summary.total_reels_received += diff

    summary.update_summary()
    summary.save()

# Signal handler for delete operations on PrintReport and PlasticReceiptReport
@receiver(post_delete, sender=PrintReport)
@receiver(post_delete, sender=PlasticReceiptReport)
def update_combined_summary_on_delete(sender, instance, **kwargs):
    if isinstance(instance, PrintReport):
        printer_nickname = instance.printer_nickname
        is_print_report = True
    elif isinstance(instance, PlasticReceiptReport):
        printer_nickname = instance.printer_nickname
        is_print_report = False
    else:
        return

    try:
        summary = CombinedSummary.objects.get(printer_nickname=printer_nickname)
    except CombinedSummary.DoesNotExist:
        return

    if is_print_report:
        old_value = instance.quantity_printed
        summary.total_printed -= old_value
    else:
        old_quantity = PlasticReceiptItem.objects.filter(report=instance).aggregate(Sum('quantity'))['quantity__sum'] or 0
        summary.total_reels_received -= old_quantity

    summary.update_summary()
    summary.save()

# Signal handler for save and delete operations on PlasticReceiptItem
@receiver(post_save, sender=PlasticReceiptItem)
@receiver(post_delete, sender=PlasticReceiptItem)
def update_combined_summary_from_item(sender, instance, **kwargs):
    report = instance.report
    printer_nickname = report.printer_nickname

    summary, created = CombinedSummary.objects.get_or_create(printer_nickname=printer_nickname)

    total_received = PlasticReceiptItem.objects.filter(report=report).aggregate(Sum('quantity'))['quantity__sum'] or 0
    summary.total_reels_received = total_received

    summary.update_summary()
    summary.save()
