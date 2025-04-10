from django.db.models.signals import post_save, post_delete  # Import signals for post-save and post-delete actions
from django.dispatch import receiver  # Import the receiver decorator for handling signals
from .models import OrderItem  # Import the OrderItem model

# This signal receiver listens for post-save and post-delete events on the OrderItem model
@receiver(post_save, sender=OrderItem)  # Triggered when an OrderItem is saved
@receiver(post_delete, sender=OrderItem)  # Triggered when an OrderItem is deleted
def update_order_total(sender, instance, **kwargs):
    """
    This function is called after an OrderItem is saved or deleted.
    It ensures that the total cost of the associated order is recalculated.
    """
    if instance.order:  # Check if the order related to the OrderItem exists
        instance.order.calculate_total_cost()  # Recalculate the total cost of the associated order
