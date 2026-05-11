import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hours.settings')
django.setup()

from sheets.models import Sheet

def test_ialization():
    for sheet in Sheet.objects.all():
        data = sheet.data
        updated = False
        for data_item in data:
            if 'Attendance' not in data_item:
                data_item['Attendance'] = ""   # default empty list
                updated = True
        # if updated:
            # sheet.save(update_fields=['data'])

test_ialization()