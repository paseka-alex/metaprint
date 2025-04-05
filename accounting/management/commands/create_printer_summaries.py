# in management/commands/create_printer_summaries.py
from django.core.management.base import BaseCommand
from accounting.models import CombinedSummary, PlasticReceiptReport, PrintReport

class Command(BaseCommand):
    help = 'Create summary entries for all printer nicknames found in reports'

    def handle(self, *args, **options):
        # Get unique printer nicknames from both report types
        plastic_printers = PlasticReceiptReport.objects.values_list('printer_nickname', flat=True).distinct()
        print_printers = PrintReport.objects.values_list('printer_nickname', flat=True).distinct()
        
        # Combine unique nicknames
        all_printers = set(list(plastic_printers) + list(print_printers))
        
        count = 0
        for printer in all_printers:
            summary, created = CombinedSummary.objects.get_or_create(printer_nickname=printer)
            summary.save()
            if created:
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Created {count} new printer summaries'))