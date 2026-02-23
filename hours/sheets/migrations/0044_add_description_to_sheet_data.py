# Generated manually

from django.db import migrations

def add_description_to_sheet_data(apps, schema_editor):
    Sheet = apps.get_model('sheets', 'Sheet')
    for sheet in Sheet.objects.all():
        modified = False
        if isinstance(sheet.data, list):
            for day_data in sheet.data:
                if 'Description' not in day_data:
                    day_data['Description'] = ''
                    modified = True
            if modified:
                sheet.save(update_fields=['data'])

def remove_description_from_sheet_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0043_update_sheet_user_names'),
    ]

    operations = [
        migrations.RunPython(add_description_to_sheet_data, remove_description_from_sheet_data),
    ]
