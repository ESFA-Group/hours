# Generated migration to populate auto_hour_ID field

from django.db import migrations

# Mapping: auto_hour_ID (key) -> user_id (value)
# Entries with value -1 are excluded as they represent invalid/unmatched users
AUTO_HOUR_ID_MAPPING = {
    1: 2,       # hassan, zahedi
    60: 134,
}


def populate_auto_hour_id(apps, schema_editor):
    """Populate auto_hour_ID field based on the mapping"""
    User = apps.get_model('sheets', 'User')
    
    for auto_hour_id, user_id in AUTO_HOUR_ID_MAPPING.items():
        try:
            user = User.objects.get(pk=user_id)
            user.auto_hour_ID = auto_hour_id
            user.save(update_fields=['auto_hour_ID'])
        except User.DoesNotExist:
            print(f"User with id {user_id} not found for auto_hour_ID {auto_hour_id}")


def reverse_populate(apps, schema_editor):
    """Reverse migration - set auto_hour_ID back to NULL"""
    User = apps.get_model('sheets', 'User')
    User.objects.all().update(auto_hour_ID=None)


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0046_populate_auto_hour_id'),
    ]

    operations = [
        migrations.RunPython(populate_auto_hour_id, reverse_populate),
    ]
