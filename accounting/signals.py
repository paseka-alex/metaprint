import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from accounting.models import PrintReport, PlasticReceiptReport, CombinedSummary, PlasticReceiptItem

#logger = logging.get#logger(__name__)

# Signal handler for both save and delete operations
@receiver(post_save, sender=PrintReport)
@receiver(post_save, sender=PlasticReceiptReport)
def update_combined_summary_on_save(sender, instance, created, **kwargs):
    # Log the incoming instance details
    #logger.debug(f"Signal triggered for {sender.__name__} with instance: {instance}")
    
    if isinstance(instance, PrintReport):
        printer_nickname = instance.printer_nickname
        is_print_report = True
    elif isinstance(instance, PlasticReceiptReport):
        printer_nickname = instance.printer_nickname
        is_print_report = False
    else:
        #logger.debug("Instance is neither PrintReport nor PlasticReceiptReport, exiting.")
        return

    # Get or create the CombinedSummary for the printer
    summary, created = CombinedSummary.objects.get_or_create(printer_nickname=printer_nickname)
    #logger.debug(f"CombinedSummary for {printer_nickname}: {summary}")

    if not created:
        if is_print_report:
            # Update the total printed quantity by calculating the difference
            old_value = instance.__class__.objects.get(id=instance.id).quantity_printed
            diff = instance.quantity_printed - old_value
            #logger.debug(f"Old printed quantity: {old_value}, New printed quantity: {instance.quantity_printed}, Diff: {diff}")
            summary.total_printed += diff
        else:
            # For PlasticReceiptReport, update the total received quantity
            old_quantity = PlasticReceiptItem.objects.filter(report__id=instance.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
            new_quantity = PlasticReceiptItem.objects.filter(report__id=instance.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
            diff = new_quantity - old_quantity
            #logger.debug(f"Old received quantity: {old_quantity}, New received quantity: {new_quantity}, Diff: {diff}")
            summary.total_reels_received += diff

    # Recalculate the summary totals
    summary.update_summary()
    summary.save()
    #logger.debug(f"CombinedSummary updated for {printer_nickname}: {summary}")


@receiver(post_delete, sender=PrintReport)
@receiver(post_delete, sender=PlasticReceiptReport)
def update_combined_summary_on_delete(sender, instance, **kwargs):
    # Log the incoming instance details
    #logger.debug(f"Signal triggered for {sender.__name__} with instance: {instance} (deleted)")
    
    if isinstance(instance, PrintReport):
        printer_nickname = instance.printer_nickname
        is_print_report = True
    elif isinstance(instance, PlasticReceiptReport):
        printer_nickname = instance.printer_nickname
        is_print_report = False
    else:
        #logger.debug("Instance is neither PrintReport nor PlasticReceiptReport, exiting.")
        return

    # Get the CombinedSummary for the printer (this will be updated)
    try:
        summary = CombinedSummary.objects.get(printer_nickname=printer_nickname)
    except CombinedSummary.DoesNotExist:
        #logger.debug(f"CombinedSummary for {printer_nickname} not found, exiting.")
        return
    
    #logger.debug(f"CombinedSummary for {printer_nickname}: {summary}")

    if is_print_report:
        # Update the total printed quantity by subtracting the deleted value
        old_value = instance.quantity_printed
        #logger.debug(f"Old printed quantity (deleted): {old_value}")
        summary.total_printed -= old_value
    else:
        # For PlasticReceiptReport, subtract the total quantity received from the deleted report's items
        old_quantity = PlasticReceiptItem.objects.filter(report=instance).aggregate(Sum('quantity'))['quantity__sum'] or 0
        #logger.debug(f"Old received quantity (deleted): {old_quantity}")
        summary.total_reels_received -= old_quantity

    # Recalculate the summary totals
    summary.update_summary()
    summary.save()
    #logger.debug(f"CombinedSummary updated for {printer_nickname}: {summary}")

@receiver(post_save, sender=PlasticReceiptItem)
@receiver(post_delete, sender=PlasticReceiptItem)
def update_combined_summary_from_item(sender, instance, **kwargs):
    # Get the related PlasticReceiptReport and printer nickname
    report = instance.report
    printer_nickname = report.printer_nickname
    
    # Get or create the CombinedSummary for the printer
    summary, created = CombinedSummary.objects.get_or_create(printer_nickname=printer_nickname)
    
    # Log the action (whether it was created or deleted)
    #if sender == PlasticReceiptItem and kwargs.get('created', False):
        ##logger.debug(f"PlasticReceiptItem created: {instance}")
    #else:
        ##logger.debug(f"PlasticReceiptItem deleted: {instance}")
    
    # Recalculate the total received reels by summing up all related PlasticReceiptItems
    total_received = PlasticReceiptItem.objects.filter(report=report).aggregate(Sum('quantity'))['quantity__sum'] or 0
    ##logger.debug(f"Recalculated total received reels for {printer_nickname}: {total_received}")
    
    # Update the summary total
    summary.total_reels_received = total_received
    
    # Recalculate the summary totals
    summary.update_summary()
    summary.save()
    ##logger.debug(f"CombinedSummary saved for {printer_nickname}: {summary}")